import argparse
import struct
import json

import ds_utils

def decode_dbase(if_bytes):
	f = if_bytes
	read_int = lambda: struct.unpack('<I', f.read(4))[0]
	offsets = []
	pads = []

	blocks = read_int()
	for b in xrange(blocks):
		offsets.append([])
		pads.append([])
		lines = read_int()
		for l in xrange(lines):
			offsets[-1].append(read_int())
		for l in xrange(lines):
			pad = read_int()
			if pad != 0:
				print "strange padding:", pad
			pads[-1].append(pad)

	table = f.read()

	json_data = [blocks]
	for b in xrange(blocks):
		lines = len(offsets[b])
		block = [lines]
		for l in xrange(lines):
			o = offsets[b][l]
			p = pads[b][l]
			s = table[o:].partition('\0')[0]
			s = ds_utils.to_unicode(s)
			if p == 0:
				block.append(s)
			else:
				block.append([p, s])
		json_data.append(block)

	return json_data

def encode_dbase(of_bytes, json_data):
	f = of_bytes
	write_int = lambda i: f.write(struct.pack('<I', i))

	offset = 0
	table = []
	write_int(json_data[0])
	for block in json_data[1:]:
		write_int(block[0])
		for s in block[1:]:
			if not isinstance(s, basestring):
				s = s[1]
			write_int(offset)
			s = ds_utils.to_sjis(s.encode('utf-8'))
			table.append(s)
			offset += len(s) + 1
		for s in block[1:]:
			pad = 0
			if not isinstance(s, basestring):
				pad = s[0]
			write_int(pad)
		#for i in xrange(len(block[1:])):
		#	write_int(0)  # unknown 0 padding bytes

	for s in table:
		f.write(s)
		f.write(struct.pack('B', 0))

	return f

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("operation", choices=['e', 'd'], help="encode or decode")
	parser.add_argument("in_file")
	parser.add_argument("out_file")
	args = parser.parse_args()

	if args.operation == 'd':
		with open(args.in_file, 'rb') as fileobj:
			jsdata = decode_dbase(fileobj)
		with open(args.out_file, 'w') as fileobj:
			data = json.dumps(jsdata,
				sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=False)
			fileobj.write(data)
	elif args.operation == 'e':
		with open(args.in_file, 'r') as inp:
			with open(args.out_file, 'wb') as outp:
				jsdata = json.loads(inp.read())
				encode_dbase(outp, jsdata)

if __name__ == "__main__":
	main()
