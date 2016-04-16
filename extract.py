import os
import sys
import glob
import subprocess

cmds = [
	# Extract strings from arm9 executables
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/arm9.bin',
		'0x2000000',
		'source/root/ftc/arm9.bin.pointers.txt',
		'>translated/root/ftc/arm9.bin.strings.txt'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_0',
		'0x22982A0',
		'source/root/ftc/overlay9_0.pointers.txt',
		'>translated/root/ftc/overlay9_0.strings.txt'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_1',
		'0x22982A0',
		'source/root/ftc/overlay9_1.pointers.txt',
		'>translated/root/ftc/overlay9_1.strings.txt'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_2',
		'0x22982A0',
		'source/root/ftc/overlay9_2.pointers.txt',
		'>translated/root/ftc/overlay9_2.strings.txt'
	],
	[
		'python scripts/arm_text_extract.py',
		'source/root/ftc/overlay9_3',
		'0x22982A0',
		'source/root/ftc/overlay9_3.pointers.txt',
		'>translated/root/ftc/overlay9_3.strings.txt'
	],
]

# String database files
for f in glob.glob('source/root/str/text/*'):
	fname = os.path.basename(f)
	cmds.append([
		'python scripts/dbase_parser.py d',
		os.path.join('source/root/str/text', fname),
		os.path.join('translated/root/str/text', fname+'.strings.txt'),
	])

# Dialog files
cmds.append([
	'python scripts/event_parser.py',
	'translated/dialog.html',
	'source/root/eventbin/*.decompressed'
	]
)

for c in cmds:
	print c
	status = subprocess.call(' '.join(c), shell=True)

# Move dialog files to translate dir
for f in glob.glob('source/root/eventbin/*.decompressed.txt'):
	fname = os.path.basename(f)
	fout = os.path.join('translated/root/eventbin', fname)
	os.unlink(fout)
	os.rename(f, fout)