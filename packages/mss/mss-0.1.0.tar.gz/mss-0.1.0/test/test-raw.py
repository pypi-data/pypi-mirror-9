#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Test raw data.

from struct import pack
import os.path
import zlib
import sys


def save_img(data, width, height, output):
    ''' Dump data to the image file.
        Pure python PNG implementation.
        Image represented as RGB tuples, no interlacing.
        http://inaps.org/journal/comment-fonctionne-le-png
    '''

    to_take = (width * 3 + 3) & -4
    padding = 0 if to_take % 8 == 0 else (to_take % 8) // 2
    scanlines = b''.join(
        [b'0' + data[(y * to_take):(y * to_take) + to_take - padding]
         for y in range(height)])

    magic = pack(b'>8B', 137, 80, 78, 71, 13, 10, 26, 10)

    # Header: size, marker, data, CRC32
    ihdr = [b'', b'IHDR', b'', b'']
    ihdr[2] = pack(b'>2I5B', width, height, 8, 2, 0, 0, 0)
    ihdr[3] = pack(b'>I', zlib.crc32(b''.join(ihdr[1:3])) & 0xffffffff)
    ihdr[0] = pack(b'>I', len(ihdr[2]))

    # Data: size, marker, data, CRC32
    idat = [b'', b'IDAT', b'', b'']
    idat[2] = zlib.compress(scanlines, 9)
    idat[3] = pack(b'>I', zlib.crc32(b''.join(idat[1:3])) & 0xffffffff)
    idat[0] = pack(b'>I', len(idat[2]))

    # Footer: size, marker, None, CRC32
    iend = [b'', b'IEND', b'', b'']
    iend[3] = pack(b'>I', zlib.crc32(iend[1]) & 0xffffffff)
    iend[0] = pack(b'>I', len(iend[2]))

    with open(output, 'wb') as fileh:
        fileh.write(
            magic + b''.join(ihdr) + b''.join(idat) + b''.join(iend))
    if not os.path.isfile(output):
        msg = 'Impossible to write data to file "{}".'.format(output)
        raise ScreenshotError(msg)

if len(sys.argv) < 4:
    print('python {0} data.raw width height'.format(sys.argv[0]))
else:
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
        width = int(sys.argv[2])
        height = int(sys.argv[3])
        save_img(data, width, height, sys.argv[1] + '.png')
