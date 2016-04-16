import argparse
import struct
import json
import ds_utils

def read_int(ram, ptr):
	return struct.unpack('<I', "".join(ram[ptr:ptr+4]))[0]

def read_str(ram, ptr):
	strend = ptr
	skips = 0
	while ord(ram[strend]) != 0:
		if ord(ram[strend]) < 0x10 and skips < 10:
			strend += 1
			skips += 1
		strend += 1
	return ram[ptr:strend]

def extract(ram, offset, ptrs):
	tbl = []
	for p in ptrs:
		pval = read_int(ram, p - offset)
		s = read_str(ram, pval - offset)
		#print ds_utils.to_hex(s)
		tbl.append([p, pval,
			ds_utils.to_hex(s),
			ds_utils.to_unicode(s),
			hex(pval - offset)])
	return tbl

def main():
	parser = argparse.ArgumentParser()
	def auto_int(x):
		return int(x, 0)
	parser.add_argument("binary")
	parser.add_argument("offset", type=auto_int)
	parser.add_argument("ptr_list")
	args = parser.parse_args()

	ram_offset = args.offset
	with open(args.binary, 'rb') as fileobj:
		bindata = fileobj.read()
	with open(args.ptr_list, 'r') as fileobj:
		ptrs = []
		for l in fileobj.readlines():
			strs = l.split()
			if len(strs) > 1:
				ptr, pval = strs[:2]
				ptr = auto_int(ptr)
				pval = auto_int(pval)
				# Validate ptr value
				data = read_int(bindata, ptr - ram_offset)
				if data != pval:
					raise "pointer value mismatch"
				if ord(bindata[data - ram_offset]) != 0:
					ptrs.append(ptr)

	tbl = extract(bindata, ram_offset, ptrs)
	print json.dumps(tbl, sort_keys=True, indent=2,
		separators=(',', ': '), ensure_ascii=False)

if __name__ == "__main__":
	main()
