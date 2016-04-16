import argparse
import cStringIO
import struct
import json
import ds_utils

def read_int(ram, ptr):
	return struct.unpack('<I', ram[ptr:ptr+4])[0]

def read_str(ram, ptr):
	strend = ptr
	skips = 0
	while ord(ram[strend]) != 0:
		if ord(ram[strend]) < 0x10 and skips < 10:
			strend += 1
			skips += 1
		strend += 1
	return ram[ptr:strend]

def write_int(ram, ptr, i):
	ram[ptr:ptr+4] = struct.pack('<I', i)

def write_str(ram, ptr, s, zpad):
	datlen = len(s)
	ram[ptr:ptr+datlen] = list(s)
	ram[ptr+datlen:ptr+datlen+zpad] = ['\0']*zpad

def main():
	parser = argparse.ArgumentParser()
	def auto_int(x):
		return int(x, 0)
	parser.add_argument("binary")
	parser.add_argument("ram_offset", type=auto_int)
	parser.add_argument("strfile")
	parser.add_argument("outfile")
	args = parser.parse_args()

	ram_offset = args.ram_offset
	with open(args.binary, 'rb') as fileobj:
		bindata = fileobj.read()
	writeram = list(bindata)

	with open(args.strfile) as fileobj:
		strtable = json.loads(fileobj.read())

	# Step 1 verify pre-patch matches, convert to utf-8
	for s in strtable:
		p = s[0]
		pval = s[1]
		if read_int(bindata, p - ram_offset) != pval:
			raise "Old pointer values don't match, is ram offset correct?"
		s[3] = s[3].encode('utf-8')

	# Step 2 gather regions to overwrite
	regions = []
	for s in strtable:
		ramptr = s[1]
		free = s[1] - ram_offset
		s = read_str(bindata, free)
		slen = len(s) + 4
		slen = slen - (slen % 4)
		pad = slen - len(s)
		for r in xrange(free + len(s) + 1, free + slen):
			if ord(bindata[r]) != 0:
				#raise "Non 0 padding byte detected"
				print "Non 0 padding", s[1]
		regions.append([ramptr, slen])
	regions.sort()

	# Coalesce regions
	compressed_regions = []
	cur = [0,0]
	freecount = 0
	for r in regions:
		freecount += r[1]
		if cur[1] + cur[0] == r[0]:
			cur[1] += r[1]
		else:
			compressed_regions.append(cur)
			cur = r
	compressed_regions.append(cur)
	regions = compressed_regions

	# Allocate new strings
	allocated = 0
	saved = 0
	cache = {}
	for s in strtable:
		ptr = s[0]
		data = s[3]
		data = bytes(ds_utils.to_sjis(data))
		slen = len(data) + 4
		slen = slen - (slen % 4)
		pad = slen - len(data)

		if data not in cache:
			found = False
			for r in regions:
				if r[1] >= slen:
					target = r[0]
					r[0] += slen
					r[1] -= slen
					write_int(writeram, ptr - ram_offset, target)
					write_str(writeram, target - ram_offset, data, pad)
					cache[data] = target
					allocated += slen
					saved += 1
					found = True
					print ds_utils.to_hex(data)
					break
			if not found:
				print regions
				print slen
				print freecount
				print saved, len(strtable)
				raise "No free region"
		else:
			target = cache[data]
			write_int(writeram, ptr - ram_offset, target)

	# Fill unused regions
	regions = filter(lambda r: r[1] > 0, regions)
	for r in regions:
		target = r[0]
		data = chr(0xff)*r[1]
		write_str(writeram, target - ram_offset, data, 0)
	print "Unused regions:", regions

	with open(args.outfile, 'wb') as fileobj:
		fileobj.write(bytes(b''.join(writeram)))

	print "DONE"

if __name__ == "__main__":
	main()
