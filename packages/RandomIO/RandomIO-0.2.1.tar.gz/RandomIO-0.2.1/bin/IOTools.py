#!/usr/bin/env python

#
# The MIT License (MIT)
#
# Copyright (c) 2014 Josh Brandoff for Storj Labs
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import argparse
import hashlib
import RandomIO
import binascii

class IOTools(object):

    def __init__(self):
        """Initialization of top-level IO Tools menu."""
        parser = argparse.ArgumentParser(
            description='A series of command-line tools that make use of the RandomIO library.', usage='''IOTools.py <command> [<args>]

Currently available commands include:
   pairgen       Outputs a series of seed-hash pairs for files generated using the RandomIO library.''')
        parser.add_argument('command', help='Command to run.')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command.')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def _sizeformat(self, num):
        """Utility method for printing byte sizes with easier-to-read units.

        :param num: integer byte number
        :returns: human-readable string of byte input converted to KB, MB or GB
        """
        for x in ['bytes', 'KB', 'MB', 'GB']:
            if abs(num) < 1024.0:
                return "%3.1f%s" % (num, x)
            num /= 1024.0

    def _genredis(self, seed, hash):
        """Utility method for writing to Redis protocol for mass key-value insertion.

        :param seed: hex-encoded file seed string to act as key
        :param hash: hash for file generated from seed
        :returns: Redis protocol for `SET key value` command
        """
        return '*3\r\n$3\r\nSET\r\n${0}\r\n{1}\r\n${2}\r\n{3}\r\n'.format(len(seed), seed, len(hash), hash)

    def pairgen(self):
        parser = argparse.ArgumentParser(description='Output a series of seed-hash pairs for files generated in memory using the RandomIO library.',
                                         epilog='This tool can be used to pre-generate seed-hash pairs for the Storj uptick service.')
        parser.add_argument(
            'size', type=int, help='The target size of each file generated and hashed (in bytes).')
        parser.add_argument(
            '-l', '--length', type=int, help='The length of the random seed string to use.', action='store', default=12)
        parser.add_argument(
            '-p', '--pairs', type=int, help='The number of seed-hash pairs to generate.', action='store', default=1)
        parser.add_argument(
            '-o', '--output', type=str, help='The name of the file you wish to write pairs to.', action='store', default='pairs.out')
        parser.add_argument(
            '-r', '--redis', action='store_true', help='Write to file using Redis protocol.')
        parser.add_argument(
            '-v', '--verbose', action='store_true', help='Increase output verbosity.')
        args = parser.parse_args(sys.argv[2:])

        with open(args.output or 'pairs.out', 'w') as f:
            for i in range(args.pairs or 1):
                seed = os.urandom(args.length or 12)
                hexseed = binascii.hexlify(seed).decode('ascii')
                if (args.verbose):
                    filesize = self._sizeformat(args.size)
                    print('Pair {0}: Generating hash for {1} file with seed {2}...'.format(
                        i, filesize, hexseed))
                hash = hashlib.sha256(
                    RandomIO.RandomIO(seed).read(args.size)).hexdigest()
                if (args.redis):
                    f.write(self._genredis(hexseed, hash))
                else:
                    f.write('{0} {1}\n'.format(hexseed, hash))
                if (args.verbose):
                    print('done!')

if __name__ == '__main__':
    IOTools()
