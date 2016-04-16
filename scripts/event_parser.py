# -*- coding: utf-8 -*-

import os
import argparse
import struct
import json
import ds_utils
import glob
import hashlib

import re
import cStringIO

	
def dump_dialog(data):
	assert data[0] == '\x1F'
	# Get speaker
	it = 1
	if data[it] == '\x00':
		character = '-'
		it += 1
	elif data[it] == '\x01':
		it += 1
		char = []
		mainchar = False
		while it < len(data) and data[it] != '\n':
			if data[it] == '\x03':
				mainchar = True
			char.append(data[it])
			it += 1
		it += 1
		character = ds_utils.to_unicode(''.join(char))
		if mainchar:
			character = "[@]"
	else:
		print ds_utils.to_hex(data)
		print ds_utils.to_unicode(''.join(data))
		raise "Unknown"
	# Get lines
	lines = []
	while it < len(data):
		line = []
		while it < len(data) and data[it] != '\n':
			line.append(data[it])
			it += 1
		if it < len(data):
			line.append(data[it])
			it += 1
		lines.append(ds_utils.to_unicode(''.join(line)))
	return {'char': character, 'lines': lines}

def dump_hex(data, start):
	it = start
	datlen = len(data)
	while it < datlen and data[it] != '\0' and data[it] != '\x1F':
		it += 1
	while it < datlen and data[it] == '\0' and data[it] != '\x1F':
		it += 1
	return data[start:it]

def dump_eventbin(table, dialoglist, fname, data):
	jsdata = []

	# Get block count
	nblocks = struct.unpack('<I', data[:4])[0]
	offsets = [struct.unpack('<I', data[x*4+4:x*4+8])[0] for x in xrange(nblocks)]
	print offsets

	# Get pairs of block indexes
	ends = sorted(offsets + [len(data)])
	block_spans = [(o, next(x for x in ends if x > o)) for o in offsets]

	for block_begin, block_end in block_spans:
		jsblock = []
		it = block_begin
		while it < block_end:
			if data[it] == '\x1F':
				start = it
				# 2 command bytes
				it += 2
				# Find \0
				while it < block_end and data[it] != '\0':
					it += 1

				substr = data[start:it]
				if substr[1] not in ['\x00', '\x01'] or len(substr) < 4 or not any([(0x80 < ord(x) < 0x90) for x in substr]):
					print 'unknown', it, ds_utils.to_hex(substr)
					it = start + 1
					dump = dump_hex(data, it)
					it += len(dump)
					print 'unknown', len(dump) + 1, 'bytes processed'
					jsblock.append(ds_utils.to_hex('\x1F'+dump))
					continue

				dialog = dump_dialog(substr)
				h = hashlib.md5()
				h.update(hex(start))
				h.update(hex(it))
				h.update(os.path.basename(fname))
				h.update(dialog['char'])
				for l in dialog['lines']:
					h.update(l)
				h = h.hexdigest()
				h = long(h, 16)
				if h in table:
					print table[h], dialog, start, it
					print ds_utils.to_hex(substr)
					raise "Hash collision"
				dialog['hash'] = h
				table[h] = dialog
				jsblock.append(dialog)
				dialoglist.append(dialog)
			else:
				dump = dump_hex(data, it)
				it += len(dump)
				jsblock.append(ds_utils.to_hex(dump))
		jsdata.append(jsblock)
	return jsdata

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("htmlfile")
	parser.add_argument("eventbin", nargs='+')
	args = parser.parse_args()

	stringtable = {}
	dialoglist = []

	for fileglob in args.eventbin:
		for f in glob.glob(fileglob):
			jsf = f+".txt"
			print "Processing", f
			with open(f, 'rb') as fileobj:
				rawjs = dump_eventbin(stringtable, dialoglist, f, fileobj.read())

			# Concatenate binary data
			jsdata = []
			for block in rawjs:
				jsblock = []
				hexjoin = []
				for entry in block:
					if isinstance(entry, dict):
						if len(hexjoin) > 0:
							jsblock.append(':'.join(hexjoin))
							hexjoin = []
						jsblock.append(entry)
					else:
						hexjoin.append(entry)
				jsblock.append(':'.join(hexjoin))
				jsdata.append(jsblock)

			with open(jsf, 'w') as fileobj:
				data = json.dumps(jsdata,
					sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False)
				fileobj.write(data)

	html = []
	html.append('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
	for d in dialoglist:
		html.append('<p>@'+str(d['hash'])+'</p>')
		html.append('<p>'+d['char']+'</p>')
		line = ' '.join([l.strip() for l in d['lines']])
		
		# Apply some filters
		line = re.sub('（[^）]*）', '', line)

		html.append('<p>'+line+'</p>')

	with open(args.htmlfile, 'w') as fileobj:
		fileobj.write('\n'.join(html))

if __name__ == "__main__":
	main()
