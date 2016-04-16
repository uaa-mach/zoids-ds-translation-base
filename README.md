# Zoids Saga DS Translation Framework

## Description
This is a tool to extract and edit text resources from Zoids Saga DS: Legend of Arcadia for localisation.

## Usage

Steps to unpack and repack text resources from the ROM:

### Pre-requisites

Tinke 0.9.0+
https://github.com/pleonex/tinke

BatchLZ77

Zoids Saga DS: Legend of Arcadia nds file

### Unpacking

1. Open nds file with Tinke and unpack the root directory to `source/`
2. Use BatchLZ77 to decompress all .bin files in `source/root/eventbin/`
3. Run `extract.py` to extract text resources

### Editing
These files are now available for editing
* Text strings pulled from arm9 executable binaries
  * `translated/root/ftc*.txt`
* Text database files
  * `translated/root/str/text/*.txt`
* Dialog codex
  * `translated/dialog.html`

### Repacking

1. Run `compile.py` to generate new game resources
2. Open original nds file in Tinke and replace the following files. Note you can select all of the files and Tinke will match the filenames for replacement.
  * `translated/root/ftc/`
    * `arm9`
    * `overlay9_0`
    * `overlay9_1`
    * `overlay9_2`
    * `overlay9_3`
  * `translated/root/str/text/*.bin`
  * `translated/root/eventbin/*.bin`
