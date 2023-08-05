RandomIO
===============

[![Build Status](https://travis-ci.org/Storj/RandomIO.svg)](https://travis-ci.org/Storj/RandomIO) [![Coverage Status](https://img.shields.io/coveralls/Storj/RandomIO.svg)](https://coveralls.io/r/Storj/RandomIO?branch=master)

`RandomIO` provides a readable interface for cryptographic quality random bytes.  It also allows for generation of random files, dumping random bytes to files, and a `.read()` method for reading bytes.

### Installation

```
git clone https://github.com/storj/RandomIO
cd RandomIO
pip install .
```

### File generation

Generate a 50 byte file from a seed with one line:

```python
import RandomIO

path = RandomIO.RandomIO('seed string').genfile(50)
with open(path,'rb') as f:
	print(f.read())

# b"\xec\xf4C\xeb\x1d\rU%\xca\xae\xa4^=*in\x90y\x12\x86\xce\xe5N\xce-\x16
#   \xc8r\x83sh\xdfp\xb7\xbb\xc2\x04\x11\xda)\xc1*_\x01\xe5\xd8\x0f}N0"
```

It is possible to specify the directory to generate the file in, or the file name:

```python
# specify a directory:

path = RandomIO.RandomIO('seed string').genfile(100,'dir/')
print(path)

# 'dir/22aae6183b5202cd0c74381c673394d2'

# or file name:

path = RandomIO.RandomIO('seed string').genfile(100,'dir/file')
print(path)

# 'dir/file'
```

### Byte generation

It is possible to read random bytes and dump those bytes to a file object:

```python
import RandomIO

s = RandomIO.RandomIO()
print(s.read(10))

# b'\x8bfT\x9c\x06_)\xa2,\xd0'

# or generate seeded random bytes
s = RandomIO.RandomIO('seed string')
print(s.read(10))

# b'\xec\xf4C\xeb\x1d\rU%\xca\xae'

# dump the bytes into a file object
s = RandomIO.RandomIO('seed string')
with open('path/to/file','wb') as f:
	s.dump(10,f)

with open('path/to/file','rb') as f:
	print(f.read())
	
# b'\xec\xf4C\xeb\x1d\rU%\xca\xae'
```

### CLI Tools

RandomIO includes a small set of CLI tools in IOTools.py:

```
$python IOTools.py --help
usage: IOTools.py <command> [<args>]

Currently available commands include:
   pairgen       Outputs a series of seed-hash pairs for files generated using the RandomIO library.

A series of command-line tools that make use of the RandomIO library.

positional arguments:
  command     Command to run.

optional arguments:
  -h, --help  show this help message and exit
```

Currently, `pairgen` is the only available tool:

```
$ IOTools.py pairgen --help
usage: IOTools.py [-h] [-l LENGTH] [-p PAIRS] [-o OUTPUT] [-v] size

Output a series of seed-hash pairs for files generated in memory using the
RandomIO library.

positional arguments:
  size                  The target size of each file generated and hashed (in
                        bytes).

optional arguments:
  -h, --help            show this help message and exit
  -l LENGTH, --length LENGTH
                        The length of the random seed string to use.
  -p PAIRS, --pairs PAIRS
                        The number of seed-hash pairs to generate.
  -o OUTPUT, --output OUTPUT
                        The name of the file you wish to write pairs to.
  -r, --redis           Write to file using Redis protocol.
  -v, --verbose         Increase output verbosity.

This tool can be used to pre-generate seed-hash pairs for the Storj uptick
service.
```

Example output of `pairgens`:

```
$ IOTools.py pairgen 100000000 -p5 -l 10 -o mypairs.txt -v
Pair 0: Generating hash for 95.4MB file with seed 6a95c93fa9ca92d249d2...
done!
Pair 1: Generating hash for 95.4MB file with seed 7b31909908ff413061ce...
done!
Pair 2: Generating hash for 95.4MB file with seed a440bcd97af94701282c...
done!
Pair 3: Generating hash for 95.4MB file with seed 0f1f9dad1d6da7e03367...
done!
Pair 4: Generating hash for 95.4MB file with seed f146dbbe9c1706e1c3d6...
done!
```

Note that files are generated and hashed in memory. In addition, seeds displayed and/or written to file are hex-encoded. Actual seeds must be decoded before generating hash.

When writing pairs to file using Redis's mass insertion format, you can use the following command to import your pairs to Redis:

`cat pairs.out | redis-cli --pipe`

### Performance

```
> python -m timeit -p -s 'import RandomIO, os' 'path=RandomIO.RandomIO().genfile(100000000);os.remove(path)'
10 loops, best of 3: 1.4 sec per loop
```

From a simple timeit analysis on a 2.4 GHz PC it can generate files at around 70 MB/s.
