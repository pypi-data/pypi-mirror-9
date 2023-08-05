# -*- coding: utf-8 -*-

# Copyright 2009-2013 Richard Dymond (rjdymond@gmail.com)
#
# This file is part of Pyskool.
#
# Pyskool is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Pyskool is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pyskool. If not, see <http://www.gnu.org/licenses/>.

import zlib

def get_snapshot(fname):
    ext = fname[-4:].lower()
    if ext not in ('.sna', '.z80', '.szx', '.tzx'):
        raise SnapshotError("{0}: Unknown file type '{1}'".format(fname, ext[1:]))
    with open(fname, 'rb') as f:
        data = bytearray(f.read()) # PY: 'return f.read()' in Python 3
    if ext == '.sna':
        ram = data[27:49179]
    elif ext == '.z80':
        ram = _read_z80(data)
    elif ext == '.szx':
        ram = _read_szx(data)
    elif ext == '.tzx':
        ram = _read_tzx(data)
    if len(ram) != 49152:
        raise SnapshotError("RAM size is {0}".format(len(ram)))
    mem = [0] * 16384
    mem.extend(ram)
    return mem

def _read_z80(data):
    version = 1 if sum(data[6:8]) > 0 else 2
    header_size = 30 if version == 1 else 32 + data[30]
    header = data[:header_size]
    if version == 1:
        if header[12] & 32 == 0:
            return data[header_size:-4]
        return _decompress_block(data[header_size:-4])
    machine_id = data[34]
    extension = ()
    if (version == 2 and machine_id < 2) or (version == 3 and machine_id in (0, 1, 3)):
        if data[37] & 128:
            banks = (5,) # 16K
            extension = [0] * 32768
        else:
            banks = (5, 1, 2) # 48K
    else:
        page = data[35] & 7
        banks = (5, 2, page) # 128K
    return _decompress(data[header_size:], banks, extension)

def _read_szx(data):
    extension = ()
    machine_id = data[6]
    if machine_id == 0:
        banks = (5,) # 16K
        extension = [0] * 32768
    elif machine_id == 1:
        banks = (5, 2, 0) # 48K
    else:
        specregs = _get_zxstblock(data, 8, 'SPCR')[1]
        if specregs is None:
            raise SnapshotError("SPECREGS (SPCR) block not found")
        page = specregs[1] & 7
        banks = (5, 2, page) # 128K
    pages = {}
    for bank in banks:
        pages[bank] = None
    i = 8
    while 1:
        i, rampage = _get_zxstblock(data, i, 'RAMP')
        if rampage is None:
            break
        page = rampage[2]
        if page in pages:
            ram = rampage[3:]
            if rampage[0] & 1:
                try:
                    # PY: No need to convert to bytes and bytearray in Python 3
                    ram = bytearray(zlib.decompress(bytes(ram)))
                except zlib.error as e:
                    raise SnapshotError("Error while decompressing page {0}: {1}".format(page, e.args[0]))
            if len(ram) != 16384:
                raise SnapshotError("Page {0} is {1} bytes (should be 16384)".format(page, len(ram)))
            pages[page] = ram
    return _concatenate_pages(pages, banks, extension)

def _get_zxstblock(data, index, block_id):
    block = None
    while index < len(data) and block is None:
        size = data[index + 4] + 256 * data[index + 5] + 65536 * data[index + 6] + 16777216 * data[index + 7]
        dw_id = ''.join([chr(b) for b in data[index:index + 4]])
        if dw_id == block_id:
            block = data[index + 8:index + 8 + size]
        index += 8 + size
    return index, block

def _concatenate_pages(pages, banks, extension):
    ram = []
    for bank in banks:
        if pages[bank] is None:
            raise SnapshotError("Page {0} not found".format(bank))
        ram.extend(pages[bank])
    ram.extend(extension)
    return ram

def _decompress(ramz, banks, extension):
    pages = {}
    for bank in banks:
        pages[bank] = None
    j = 0
    while j < len(ramz):
        length = ramz[j] + 256 * ramz[j + 1]
        page = ramz[j + 2] - 3
        if length == 65535:
            if page in pages:
                pages[page] = ramz[j + 3:j + 16387]
            j += 16387
        else:
            if page in pages:
                pages[page] = _decompress_block(ramz[j + 3:j + 3 + length])
            j += 3 + length
    return _concatenate_pages(pages, banks, extension)

def _decompress_block(ramz):
    block = []
    i = 0
    while i < len(ramz):
        b = ramz[i]
        i += 1
        if b == 237:
            c = ramz[i]
            i += 1
            if c == 237:
                length, byte = ramz[i], ramz[i + 1]
                if length == 0:
                    raise SnapshotError("Found ED ED 00 {0:02X}".format(byte))
                block += [byte] * length
                i += 2
            else:
                block += [b, c]
        else:
            block.append(b)
    return block

def _read_tzx(data):
    signature = _get_str(data[:7])
    if signature != 'ZXTape!':
        raise TZXError("Not a TZX file")

    i = 10
    program = ""
    while i < len(data):
        i, block_id, tape_data = _get_tzx_block(data, i)
        if block_id == 16 and tape_data[0] == 0:
            program = _get_str(tape_data[2:12]).strip()
            if program not in ('skooldaze', 'bak2skool'):
                raise TZXError("Unknown program: {0}".format(program))
        elif program and block_id == 17:
            tape_data_len = len(tape_data)
            if tape_data_len != 82109:
                raise TZXError("Turbo speed data block length is {0} != 82109".format(tape_data_len))
            return _tzx_to_snapshot(tape_data)
    raise TZXError("Turbo speed data block not found")

def _tzx_to_snapshot(data):
    snapshot = [0] * 65536
    snapshot[16384:32954] = data[1:16571]
    j = 32902
    for b in data[16571:82109]:
        snapshot[j] = b
        j = (j + 23) % 65536

    if snapshot[16384] == 255:
        # Skool Daze
        snapshot[32768:33280] = snapshot[32256:32768]
        snapshot[32612:32614] = [0] * 2
    else:
        # Back to Skool
        snapshot[32768:33024] = snapshot[58112:58368]
        snapshot[33024:33280] = snapshot[23296:23552]

    return snapshot[16384:]

def _get_tzx_block(data, i):
    # http://www.worldofspectrum.org/TZXformat.html
    block_id = data[i]
    tape_data = []
    i += 1
    if block_id == 16:
        # Standard speed data block
        length = _get_word(data, i + 2)
        tape_data = data[i + 4:i + 4 + length]
        i += 4 + length
    elif block_id == 17:
        # Turbo speed data block
        length = _get_word3(data, i + 15)
        tape_data = data[i + 18:i + 18 + length]
        i += 18 + length
    elif block_id == 18:
        # Pure tone
        i += 4
    elif block_id == 19:
        # Sequence of pulses of various lengths
        i += 2 * data[i] + 1
    elif block_id == 20:
        # Pure data block
        i += _get_word3(data, i + 7) + 10
    elif block_id == 21:
        # Direct recording block
        i += _get_word3(data, i + 5) + 8
    elif block_id == 24:
        # CSW recording block
        i += _get_dword(data, i) + 4
    elif block_id == 25:
        # Generalized data block
        i += _get_dword(data, i) + 4
    elif block_id == 32:
        # Pause (silence) or 'Stop the tape' command
        i += 2
    elif block_id == 33:
        # Group start
        i += data[i] + 1
    elif block_id == 34:
        # Group end
        pass
    elif block_id == 35:
        # Jump to block
        i += 2
    elif block_id == 36:
        # Loop start
        i += 2
    elif block_id == 37:
        # Loop end
        pass
    elif block_id == 38:
        # Call sequence
        i += _get_word(data, i) * 2 + 2
    elif block_id == 39:
        # Return from sequence
        pass
    elif block_id == 40:
        # Select block
        i += _get_word(data, i) + 2
    elif block_id == 42:
        # Stop the tape if in 48K mode
        i += 4
    elif block_id == 43:
        # Set signal level
        i += 5
    elif block_id == 48:
        # Text description
        i += data[i] + 1
    elif block_id == 49:
        # Message block
        i += data[i + 1] + 2
    elif block_id == 50:
        # Archive info
        i += _get_word(data, i) + 2
    elif block_id == 51:
        # Hardware type
        i += data[i] * 3 + 1
    elif block_id == 53:
        # Custom info block
        i += _get_dword(data, i + 16) + 20
    elif block_id == 90:
        # "Glue" block
        i += 9
    else:
        raise TZXError('Unknown block ID {0} at index {1}\n'.format(block_id, i - 1))
    return i, block_id, tape_data

def _get_word(data, index):
    return data[index] + 256 * data[index + 1]

def _get_word3(data, index):
    return _get_word(data, index) + 65536 * data[index + 2]

def _get_dword(data, index):
    return _get_word3(data, index) + 16777216 * data[index + 3]

def _get_str(data):
    return ''.join(chr(b) for b in data)

class SnapshotError(Exception):
    pass

class TZXError(Exception):
    pass
