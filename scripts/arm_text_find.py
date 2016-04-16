import argparse
import cStringIO
import struct
import json
import ds_utils

def read_int(ram, ptr):
	return struct.unpack('<I', "".join(ram[ptr:ptr+4]))[0]

def read_str(ram, ptr):
	strend = ptr
	skips = 0
	while ord(ram[strend]) != 0:
		if ord(ram[strend]) < 0xf and skips < 3:
			strend += 5
			skips += 1
		strend += 1
	return ram[ptr:strend]

def ram_mark(mark, ptr, strlen):
	strlen += 4
	strlen = strlen - (strlen % 4)
	for p in xrange(ptr, ptr + strlen):
		mark[p] = chr(255)

def dump(ram, mark, offset, start, end):
	tbl_data = []
	rsp, rep = start - offset, end - offset
	for taddr in xrange(rsp, rep, 4):
		# pointer detected
		if ord(ram[taddr+3]) == 2:
			# ptr indirection
			p = read_int(ram, taddr) - offset
			if p < 500000:
				continue
			data = read_str(ram, p)

			ram_mark(mark, p, len(data))
			print str(taddr), str(p + offset), ds_utils.to_hex(data)
			tbl_data.append([taddr + offset, p + offset,
				ds_utils.to_hex(data), ds_utils.to_unicode(data)])
	return {
		'start': start,
		'end': end,
		'table': tbl_data
	}

def main():
	parser = argparse.ArgumentParser()
	def auto_int(x):
		return int(x, 0)
	parser.add_argument("file")
	args = parser.parse_args()

	ram_base = 0x02000000
	ram = ['\0']*4194304
	regions = []

	def ram_load(ram, offset, data):
		ram[offset:offset+len(data)] = list(data)

	def ram_search(ram, ram_base, regions, data_regions):
		ptrs = set()
		for begin, end in regions:
			rb = begin - ram_base
			re = end - ram_base
			for p in xrange(rb, re, 4):
				if ord(ram[p+3]) == 2:
					pval = read_int(ram, p)
					for x, y in data_regions:
						if x <= pval < y:
							ptrs.add((p + ram_base, pval))
		ptrs = list(ptrs)
		ptrs.sort()
		return ptrs


	with open(args.file, 'rb') as fileobj:
		bindata = fileobj.read()

	ram_load(ram, 0, bindata)
	regions.append((ram_base, ram_base+len(bindata)))

	overlay_offset = 0x022982A0
	overlay_files = [
		"../overlay/overlay_0000.bin",
		"../overlay/overlay_0001.bin",
		"../overlay/overlay_0002.bin",
		"../overlay/overlay_0003.bin",
		"../overlay/overlay_0004.bin",
	]
	for ofile in overlay_files:
		with open(ofile, 'rb') as fileobj:
			overlaydata = fileobj.read()

		ram_load(ram, overlay_offset - ram_base, overlaydata)
		ov_regions = [(overlay_offset, overlay_offset+len(overlaydata))]

		#ptrs = ram_search(ram, ram_base, regions, regions)
		#ptrs = ram_search(ram, ram_base, regions, [(0x022982A0, 0x0232CE20)])
		#ptrs = ram_search(ram, ram_base, ov_regions, regions)  # none exist
		#ptrs = ram_search(ram, ram_base, regions, ov_regions)  # none exist
		ptrs = ram_search(ram, ram_base, ov_regions, ov_regions)

		print ofile
		for p, pval in ptrs:
			rp = pval - ram_base
			if ord(ram[rp-1]) == 0:
				prefzero = "ZERO"
			else:
				prefzero = ""
			print hex(p), hex(pval), ds_utils.to_hex("".join(read_str(ram,rp))), prefzero

if __name__ == "__main__":
	main()
