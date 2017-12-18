#!/usr/bin/env python
from __future__ import print_function

import sys
import string
import re

from itertools import chain


class TrifidEncoder(object):
    """TrifidEncoder objects will encode messages according to the
    Trifid cipher invented by Felix Delastelle, a three-dimensional
    version of his Bifid cipher that combines fractionalization and
    transposition to achieve the effect.
    """

    def __init__(self, key=''):
        tablekey = string.ascii_letters + '!"%&\',.:;?^ '
        if key:
            # Remove unnecessary characters.
            key = re.sub(r'[^a-zA-Z\!\"\%\&\',\.\:\;\?\^\ ]+', '', key)
            # Remove repeating characters from keystring.
            key = ''.join(sorted(set(key), key=key.index))
            # Append key to alphabet.
            tablekey = key + ''.join(
                char for char in tablekey
                if char not in key
                )
        # Cipher key dictionaries for fast lookup.
        self.itable = dict([(val, idx) for idx, val in enumerate(tablekey)])
        self.otable = dict([(idx, val) for idx, val in enumerate(tablekey)])

    def transpose(self, keys):
        """Transpose key chunk according to trifid enciphering."""
        if len(keys) == 1:
            # Don't bother enciphering when there's only one index.
            return keys
        # Separate the indices into their quarternary digits.
        keytable = [[i // 16, i % 16 // 4, i % 4] for i in keys]
        # Flip and flatten the 2d list.
        flatkeys = list(chain.from_iterable(zip(*keytable)))
        # Construct the new indices by taking the digits three at a time.
        outtable = [
            flatkeys[i]*16 + flatkeys[i+1]*4 + flatkeys[i+2]
            for i in range(0, len(flatkeys), 3)
            ]
        return outtable

    def untranspose(self, keys):
        """Undo Trifid cipher transposition."""
        size = len(keys)
        if size == 1:
            # Don't bother enciphering when there's only one index.
            return keys
        # Separate the indices into quarternary digits and flatten the list.
        keychain = [
            key for key in chain.from_iterable(
                [i // 16, i % 16 // 4, i % 4] for i in keys
                )
            ]
        # Rebuild the original 2d list and pull the old indices.
        keytable = [
            keychain[i]*16 + keychain[i+size]*4 + keychain[i+2*size]
            for i in range(size)
            ]
        return keytable

    def digest(self, intext='', chunksize=5, encode=False):
        """Ciphers message based on the given key and chunksize."""
        if chunksize < 1:
            # Throw for invalid chunk size.
            sys.stderr.write('ValueError: Invalid encoding chunk size')
            sys.exit(1)
        elif chunksize == 1 or not intext:
            # Print warning for degenerate case.
            print('Warning: Degenerate chunk size')
            return intext
        # Use cipher if encoding and decipher if decoding.
        cipher = self.transpose if encode else self.untranspose
        if encode:
            # Remove unnecessary characters.
            intext = re.sub(r'[^a-zA-Z\!\"\%\&\',\.\:\;\?\^\ ]+', '', intext)
        chunklist = []
        for i in range(0, len(intext), chunksize):
            keys = [
                self.itable[char]
                for char in intext[i:i+chunksize]
                ]
            chunklist.append(
                ''.join(
                    self.otable[key]
                    for key in cipher(keys)
                    )
                )
        return ''.join(chunklist)


def trifidcipher(intext):
    encoder = TrifidEncoder('Join our memo: Anyone Want to Talk!')
    return encoder.digest(intext, 5, True)
trifidcipher.command = "trifid"


if __name__ == '__main__':
    encoder = TrifidEncoder('The quick brown fox jumps over the lazy dog.')
    ciphertext = encoder.encode('The quick brown fox jumps over the lazy dog, dumbass.')
    print(ciphertext)
    deciphertext = encoder.decode(ciphertext)
    assert deciphertext == 'The quick brown fox jumps over the lazy dog, dumbass.'
    print(deciphertext)
