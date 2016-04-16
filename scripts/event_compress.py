# -*- coding: utf-8 -*-

import argparse
import struct
import json
import ds_utils
import glob
import hashlib
import textwrap

import re
import cStringIO


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("codex")
	parser.add_argument("js_src")
	parser.add_argument("output")
	args = parser.parse_args()

	codex = {}

	with open(args.codex, 'rb') as fileobj:
		lines = [l.strip() for l in fileobj.readlines()]
		# Remove html tags
		lines = [re.sub(r'^<[^>]*>', '', l) for l in lines]
		lines = [re.sub(r'<[^>]*>$', '', l) for l in lines]
		# Remove any header lines, first translation string contains @
		for i in xrange(len(lines)):
			if any([c == '@' for c in lines[i]]):
				lines = lines[i:]
				break

		groups = [lines[i:i + 3] for i in range(0, len(lines), 3)]
		for g in groups:
			h, char, line = g
			assert any([c == '@' for c in h])
			h = long(re.sub('[^a-fA-F0-9]', '', h))
			codex[h] = (char, line)

	with open(args.js_src, 'rb') as fileobj:
		jsdata = json.loads(fileobj.read())

	for blocks in jsdata:
		for e in blocks:
			if not isinstance(e, dict):
				continue

			tchar, tline = codex[e['hash']]

			tchar = tchar.decode("utf-8")
			tchar = tchar[:20]
			tchar = tchar.encode("utf-8")
			tchar = ds_utils.to_sjis(tchar)

			tline = tline.decode('utf-8')

			# Substitutions before wordwrapping
			tline = re.sub(u"\[@\]", u"\x03", tline)
			tline = re.sub(u"\[..\]", u"\u2026", tline)
			tline = re.sub(u"\[...\]", u"\u2025", tline)

			# Wrap in quotes
			quoted = False
			if any([c in tline for c in [u'「',u'"']]):
				tline = u'\u201c' + re.sub(u'[「"]', '', tline) + u'\u201d'
				quoted = True

			# Textwrap
			tline = textwrap.wrap(tline, 20, subsequent_indent=' ' if quoted else '')
			unic = tline
			#print tline
			tline = [l.encode('utf-8') for l in tline]
			#for l in tline:
				#print l
			try:
				tline = [ds_utils.to_sjis(l) for l in tline]
			except:
				print tline
				raise

			if e['char'] != '-':
				e['char'] = tchar
			e['lines'] = tline # split this thing

	dialogs = 0
	block_header = []
	block_data = ""
	for blocks in jsdata:
		data = []
		for e in blocks:
			if not isinstance(e, dict):
				for ch in e.split(':'):
					ch = int(ch, 16)
					data.append(chr(ch))
			else:
				data.append('\x1F')
				if e['char'] == '-':
					data.append('\x00')
				else:
					data.append('\x01')
					data.append(e['char'])
					data.append('\n')
				data.append('\n'.join(e['lines']))
				dialogs += 1
		block_header.append(len(block_data)+4+4*len(jsdata))
		block_data = block_data + "".join(data)

	with open(args.output, 'wb') as fileobj:
		fileobj.write(struct.pack('<I', len(block_header)))
		for start in block_header:
			fileobj.write(struct.pack('<I', start))
		fileobj.write(block_data)

	print "Compressed dialogs"
	print "blocks:", block_header
	print "dialogs:", dialogs

if __name__ == "__main__":
	main()
