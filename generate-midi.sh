#!/bin/sh

# Script to generate midi files for the piano. Data below was taken from
# previously generated midi files, but adds a silent note at the end
# since Symbian otherwise brutally cuts off the end of the midi file

notenum=$((0x3c))
for note in pc pcsharp pd pdsharp pe pf pfsharp pg pgsharp pa pbflat pb ptopc; do
	notenumhex=$(printf "%02x" $notenum)

	(sed "s/##/$notenumhex/g" | xxd -r - musician/${note}.mid) <<EOF
0000000: 4d54 6864 0000 0006 0001 0002 0180 4d54  MThd..........MT
0000010: 726b 0000 002f 00ff 0112 4445 5649 4345  rk.../....DEVICE
0000020: 3d47 454e 4552 414c 2e4d 4456 00ff 5804  =GENERAL.MDV..X.
0000030: 0402 2408 00ff 5902 0000 00ff 5103 07a1  ..$...Y.....Q...
0000040: 2000 ff2f 004d 5472 6b00 0000 5600 ff06   ../.MTrk...L...
0000050: 384d 4d4f 5054 3a30 2c31 2c30 2c30 2c31  8MMOPT:0,1,0,0,1
0000060: 2c30 2c33 352c 302e 3030 3033 3030 2c30  ,0,35,0.000300,0
0000070: 2e30 3230 3030 302c 312e 3336 3439 3130  .020000,1.364910
0000080: 2c33 302c 302c 302c 3700 c000 0090 ##60
0000090: 8300 80## 0083 0090 ##00 8400 80## 0000
00000a0: ff2f 00
EOF

	notenum=$(($notenum + 1))
done
