import os
import sys
import glob
import subprocess

cmds = [
	# Compile executables
	[
		'python scripts/arm_text_compress.py',
		'source/root/ftc/arm9.bin',
		'0x2000000',
		'source/root/ftc/arm9.bin.pointers.txt',
		'translated/root/ftc/arm9.bin'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_0',
		'0x22982A0',
		'source/root/ftc/overlay9_0.pointers.txt',
		'translated/root/ftc/overlay9_0'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_1',
		'0x22982A0',
		'source/root/ftc/overlay9_1.pointers.txt',
		'translated/root/ftc/overlay9_1'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_2',
		'0x22982A0',
		'source/root/ftc/overlay9_2.pointers.txt',
		'translated/root/ftc/overlay9_2'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_3',
		'0x22982A0',
		'source/root/ftc/overlay9_3.pointers.txt',
		'translated/root/ftc/overlay9_3'
	],
]

# Compile text database
for f in glob.glob('translated/root/str/text/*.txt'):
	fdir = os.path.dirname(f)
	fout = '.'.join(os.path.basename(f).split('.')[:2])
	cmds.append([
		'python scripts/dbase_parser.py e',
		f,
		os.path.join(fdir, fout)
	])

# Compile dialog
for f in glob.glob('translated/root/eventbin/*.bin.decompressed.txt'):
	fpath = os.path.dirname(f)
	fbase = os.path.basename(f).split('.')[0]
	fout = os.path.join(fpath, fbase + '.raw')
	cmds.append([
		'python scripts/event_compress.py translated/dialog.html',
		f,
		fout
	])
	fcomp = os.path.join(fpath, fbase + '.bin')
	cmds.append([
		os.path.join('scripts', 'DSDecmp.exe') + ' -c lz10 -opt',
		fout,
		fcomp
	])

for c in cmds:
	print c
	status = subprocess.call(' '.join(c), shell=True)

# Remove .cdat from dialog files
for f in glob.glob('translated/root/eventbin/*.bin.cdat'):
	fpath = os.path.dirname(f)
	fbase = os.path.basename(f).split('.')[0]
	fout = os.path.join(fpath, fbase + '.bin')
	os.rename(f, fout)
