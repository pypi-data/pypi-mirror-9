#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, print_function, with_statement, division

__doc__ = """
General purpose utilities functions for fabio
"""
__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPL"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "08/01/2015"
__status__ = "stable"
__docformat__ = 'restructuredtext'

import re, os, logging, threading, sys
logger = logging.getLogger("fabioutils")
from .third_party import six

if six.PY2:
    bytes = str
    FileIO = file
    StringTypes = (str, unicode)
    to_str = lambda s: str(s)
else:
    StringTypes = (str, bytes)
    unicode = str
    from io import FileIO
    to_str = lambda s: str(s, "ASCII")

from .compression import bz2, gzip
import traceback
from math import ceil

if sys.version_info < (3, 4):
    from threading import _Semaphore as _Semaphore
else:
    from threading import Semaphore as _Semaphore


FILETYPES = {
    # extension NNNimage fabioclass
    # type consistency - always use a list if one case is
    'edf'    : ['edf'],
    'cor'    : ['edf'],
    'pnm'    : ['pnm'],
    'pgm'    : ['pnm'],
    'pbm'    : ['pnm'],
    'tif'    : ['tif'],
    'tiff'   : ['tif'],
    'img'    : ['adsc', 'OXD', 'HiPiC', 'raxis'],
    'mccd'   : ['marccd'],
    'mar2300': ['mar345'],
    'sfrm'   : ['bruker100'],
    'msk'    : ['fit2dmask'],
    'spr'    : ['fit2dspreadsheet'],
    'dm3'    : ['dm3'],
    'kcd'    : ['kcd'],
    'cbf'    : ['cbf'],
    'xml'    : ["xsd"],
    'xsd'    : ["xsd"],
             }

# Add bzipped and gzipped
for key in list(FILETYPES.keys()):
    FILETYPES[key + ".bz2"] = FILETYPES[key]
    FILETYPES[key + ".gz"] = FILETYPES[key]


# Compressors

COMPRESSORS = {}


dictAscii = {None:[chr(i) for i in range(32, 127)],
           }

try:
    lines = os.popen("gzip -h 2>&1").read()
    # Looking for "usage"
    if "sage" in lines:
        COMPRESSORS['.gz'] = 'gzip -dc '
    else:
        COMPRESSORS['.gz'] = None
except Exception:
    COMPRESSORS['.gz'] = None

try:
    lines = os.popen("bzip2 -h 2>&1").read()
    # Looking for "usage"
    if "sage" in lines:
        COMPRESSORS['.bz2'] = 'bzip2 -dc '
    else:
        COMPRESSORS['.bz2'] = None
except Exception:
    COMPRESSORS['.bz2'] = None

def deprecated(func):
    """
    used to deprecate a function/method: prints a lot of warning messages to enforce the modifaction of the code
    """
    def wrapper(*arg, **kw):
        """
        decorator that deprecates the use of a function
        """
        logger.warning("%s is Deprecated !!! %s" % (func.func_name, os.linesep.join([""] + traceback.format_stack()[:-1])))
        return func(*arg, **kw)
    return wrapper

def pad(mystr, pattern=" ", size=80):
    """
    Performs the padding of the string to the right size with the right pattern
    """
    size = int(size)
    padded_size = int(ceil(float(len(mystr)) / size) * size)
    if len(pattern) == 1:
        return mystr.ljust(padded_size, pattern)
    else:
        return (mystr + pattern * int(ceil(float(padded_size - len(mystr)) / len(pattern))))[:padded_size]


def getnum(name):
    """
    # try to figure out a file number
    # guess it starts at the back
    """
    stem , num, post_num = numstem(name)
    try:
        return int(num)
    except ValueError:
        return None

class FilenameObject(object):
    """
    The 'meaning' of a filename ...
    """
    def __init__(self, stem=None,
            num=None,
            directory=None,
            format=None,
            extension=None,
            postnum=None,
            digits=4,
            filename=None):
        """
        This class can either be instanciated by a set of parameters like  directory, prefix, num, extension, ...

        @param stem: the stem is a kind of prefix (str)
        @param num: image number in the serie (int)
        @param directory: name of the directory (str)
        @param format: ??
        @param extension:
        @param postnum:
        @param digits: Number of digits used to print num

        Alternative constructor:

        @param filename: fullpath of an image file to be deconstructed into directory, prefix, num, extension, ...

        """


        self.stem = stem
        self.num = num
        self.format = format
        self.extension = extension
        self.digits = digits
        self.postnum = postnum
        self.directory = directory
        self.compressed = None
        if filename is not None:
            self.deconstruct_filename(filename)


    def str(self):
        """ Return a string representation """
        fmt = "stem %s, num %s format %s extension %s " + \
                "postnum = %s digits %s dir %s"
        return fmt % tuple([str(x) for x in [
                    self.stem ,
                    self.num ,
                    self.format ,
                    self.extension ,
                    self.postnum ,
                    self.digits ,
                    self.directory ] ])
    __repr__ = str

    def tostring(self):
        """
        convert yourself to a string
        """
        name = self.stem
        if self.digits is not None and self.num is not None:
            fmt = "%0" + str(self.digits) + "d"
            name += fmt % self.num
        if self.postnum is not None:
            name += self.postnum
        if self.extension is not None:
            name += self.extension
        if self.directory is not None:
            name = os.path.join(self.directory, name)
        return name


    def deconstruct_filename(self, filename):
        """
        Break up a filename to get image type and number
        """
        direc, name = os.path.split(filename)
        direc = direc or None
        parts = name.split(".")
        compressed = False
        stem = parts[0]
        extn = ""
        postnum = ""
        ndigit = 4
        num = None
        typ = None
        if parts[-1] in ["gz", "bz2"]:
            extn = "." + parts[-1]
            parts = parts[:-1]
            compressed = True
        if parts[-1] in FILETYPES.keys():
            typ = FILETYPES[parts[-1]]
            extn = "." + parts[-1] + extn
            try:
                stem, numstring, postnum = numstem(".".join(parts[:-1]))
                num = int(numstring)
                ndigit = len(numstring)
            except Exception as err:
                # There is no number - hence make num be None, not 0
                logger.debug("l176: %s" % err)
                num = None
                stem = "".join(parts[:-1])
        else:
            # Probably two type left
            if len(parts) == 1:
                # Probably GE format stem_numb
                parts2 = parts[0].split("_")
                if parts2[-1].isdigit():
                    num = int(parts2[-1])
                    ndigit = len(parts2[-1])
                    typ = ['GE']
                    stem = "_".join(parts2[:-1]) + "_"
            else:
                try:
                    num = int(parts[-1])
                    ndigit = len(parts[-1])
                    typ = ['bruker']
                    stem = ".".join(parts[:-1]) + "."
                except Exception as err:
                    logger.debug("l196: %s" % err)
                    typ = None
                    extn = "." + parts[-1] + extn
                    numstring = ""
                    try:
                        stem , numstring, postnum = numstem(".".join(parts[:-1]))
                    except Exception as err:
                        logger.debug("l202: %s" % err)
                        raise
                    if numstring.isdigit():
                        num = int(numstring)
                        ndigit = len(numstring)
                #            raise Exception("Cannot decode "+filename)

        self.stem = stem
        self.num = num
        self.directory = direc
        self.format = typ
        self.extension = extn
        self.postnum = postnum
        self.digits = ndigit
        self.compressed = compressed

def numstem(name):
    """ cant see how to do without reversing strings
    Match 1 or more digits going backwards from the end of the string
    """
    reg = re.compile(r"^(.*?)(-?[0-9]{0,9})(\D*)$")
    # reg = re.compile("""(\D*)(\d\d*)(\w*)""")
    try:
        res = reg.match(name).groups()
        # res = reg.match(name[::-1]).groups()
        # return [ r[::-1] for r in res[::-1]]
        if len(res[0]) == len(res[1]) == 0:  # Hack for file without number
            return [res[2], '', '']
        return [ r for r in res]
    except AttributeError:  # no digits found
        return [name, "", ""]

# @deprecated
def deconstruct_filename(filename):
    """
    Function for backward compatibility.
    Deprecated
    """
    return FilenameObject(filename=filename)

def construct_filename(filename, frame=None):
    "Try to construct the filename for a given frame"
    fobj = FilenameObject(filename=filename)
    if frame is not None:
        fobj.num = frame
    return fobj.tostring()

def next_filename(name, padding=True):
    """ increment number """
    fobj = FilenameObject(filename=name)
    fobj.num += 1
    if not padding:
        fobj.digits = 0
    return fobj.tostring()

def previous_filename(name, padding=True):
    """ decrement number """
    fobj = FilenameObject(filename=name)
    fobj.num -= 1
    if not padding:
        fobj.digits = 0
    return fobj.tostring()

def jump_filename(name, num, padding=True):
    """ jump to number """
    fobj = FilenameObject(filename=name)
    fobj.num = num
    if not padding:
        fobj.digits = 0
    return fobj.tostring()


def extract_filenumber(name):
    """ extract file number """
    fobj = FilenameObject(filename=name)
    return fobj.num

def isAscii(name, listExcluded=None):
    """
    @param name: string to check
    @param listExcluded: list of char or string excluded.
    @return: True of False whether  name is pure ascii or not
    """
    isascii = None
    try:
        name.encode("ASCII")
    except UnicodeDecodeError:
        isascii = False
    else:
        if listExcluded:
            isascii = not(any(bad in  name for bad in listExcluded))
        else:
            isascii = True
    return isascii

def toAscii(name, excluded=None):
    """
    @param name: string to check
    @param excluded: tuple of char or string excluded (not list: they are mutable).
    @return: the name with all non valid char removed
    """
    if excluded not in dictAscii:
        ascii = dictAscii[None][:]
        for i in excluded:
            if i in ascii:
                ascii.remove(i)
            else:
                logger.error("toAscii: % not in ascii table" % i)
        dictAscii[excluded] = ascii
    else:
        ascii = dictAscii[excluded]
    out = [i for i in str(name) if i in ascii]
    return "".join(out)

def nice_int(s):
    """
    Workaround that int('1.0') raises an exception

    @param s: string to be converted to integer
    """
    try:
        return int(s)
    except ValueError:
        return int(float(s))


class BytesIO(six.BytesIO):
    """
    just an interface providing the name and mode property to a BytesIO

    BugFix for MacOSX mainly
    """
    def __init__(self, data, fname=None, mode="r"):
        six.BytesIO.__init__(self, data)
        if not "closed" in dir(self):
            self.closed = False
        if fname == None:
            self.name = "fabioStream"
        else:
            self.name = fname
        self.mode = mode
        self.lock = _Semaphore()
        self.__size = None

    def getSize(self):
        if self.__size is None:
            logger.debug("Measuring size of %s" % self.name)
            with self.lock:
                pos = self.tell()
                self.seek(0, os.SEEK_END)
                self.__size = self.tell()
                self.seek(pos)
        return self.__size
    def setSize(self, size):
        self.__size = size
    size = property(getSize, setSize)


class File(FileIO):
    """
    wrapper for "file" with locking
    """
    def __init__(self, name, mode="rb", buffering=0):
        """file(name[, mode[, buffering]]) -> file object

        Open a file.  The mode can be 'r', 'w' or 'a' for reading (default),
        writing or appending.  The file will be created if it doesn't exist
        when opened for writing or appending; it will be truncated when
        opened for writing.  Add a 'b' to the mode for binary files.
        Add a '+' to the mode to allow simultaneous reading and writing.
        If the buffering argument is given, 0 means unbuffered, 1 means line
        buffered, and larger numbers specify the buffer size.  The preferred way
        to open a file is with the builtin open() function.
        Add a 'U' to mode to open the file for input with universal newline
        support.  Any line ending in the input file will be seen as a '\n'
        in Python.  Also, a file so opened gains the attribute 'newlines';
        the value for this attribute is one of None (no newline read yet),
        '\r', '\n', '\r\n' or a tuple containing all the newline types seen.

        'U' cannot be combined with 'w' or '+' mode.
        """
        if six.PY2:
            FileIO.__init__(self, name, mode, buffering)
        else:  # for python3 we drop buffering
            FileIO.__init__(self, name, mode)
        self.lock = _Semaphore()
        self.__size = None

    def getSize(self):
        if self.__size is None:
            logger.debug("Measuring size of %s" % self.name)
            with self.lock:
                pos = self.tell()
                self.seek(0, os.SEEK_END)
                self.__size = self.tell()
                self.seek(pos)
        return self.__size
    def setSize(self, size):
        self.__size = size
    def __exit__(self, *args, **kwargs):
        """
        Close the file.
        """
        return FileIO.close(self)
    def __enter__(self, *args, **kwargs):
        return self
    size = property(getSize, setSize)


class UnknownCompressedFile(File):
    """
    wrapper for "File" with locking
    """
    def __init__(self, name, mode="rb", buffering=0):
        logger.warning("No decompressor found for this type of file (are gzip anf bz2 installed ???")
        File.__init__(self, name, mode, buffering)


if gzip is None:
    GzipFile = UnknownCompressedFile
else:
    class GzipFile(gzip.GzipFile):
        """
        Just a wrapper forgzip.GzipFile providing the correct seek capabilities for python 2.5
        """
        def __init__(self, filename=None, mode=None, compresslevel=9, fileobj=None):
            """
            Wrapper with locking for constructor for the GzipFile class.

            At least one of fileobj and filename must be given a
            non-trivial value.

            The new class instance is based on fileobj, which can be a regular
            file, a StringIO object, or any other object which simulates a file.
            It defaults to None, in which case filename is opened to provide
            a file object.

            When fileobj is not None, the filename argument is only used to be
            included in the gzip file header, which may includes the original
            filename of the uncompressed file.  It defaults to the filename of
            fileobj, if discernible; otherwise, it defaults to the empty string,
            and in this case the original filename is not included in the header.

            The mode argument can be any of 'r', 'rb', 'a', 'ab', 'w', or 'wb',
            depending on whether the file will be read or written.  The default
            is the mode of fileobj if discernible; otherwise, the default is 'rb'.
            Be aware that only the 'rb', 'ab', and 'wb' values should be used
            for cross-platform portability.

            The compresslevel argument is an integer from 1 to 9 controlling the
            level of compression; 1 is fastest and produces the least compression,
            and 9 is slowest and produces the most compression.  The default is 9.
            """
            gzip.GzipFile.__init__(self, filename, mode, compresslevel, fileobj)
            self.lock = _Semaphore()
            self.__size = None

        def __repr__(self):
            return "fabio." + gzip.GzipFile.__repr__(self)

        def measureSize(self):
            if self.mode == gzip.WRITE:
                return self.size
            if self.__size is None:
                with self.lock:
                    if self.__size is None:
                        pos = self.offset
                        end_pos = len(gzip.GzipFile.read(self)) + pos
                        self.seek(pos)
                        logger.debug("Measuring size of %s: %s @ %s == %s" % (self.name, end_pos, pos, self.offset))
                        self.__size = end_pos
            return self.__size


if bz2 is None:
    BZ2File = UnknownCompressedFile
else:
    class BZ2File(bz2.BZ2File):
        "Wrapper with lock"
        def __init__(self, name , mode='r', buffering=0, compresslevel=9):
            """
            BZ2File(name [, mode='r', buffering=0, compresslevel=9]) -> file object

            Open a bz2 file. The mode can be 'r' or 'w', for reading (default) or
            writing. When opened for writing, the file will be created if it doesn't
            exist, and truncated otherwise. If the buffering argument is given, 0 means
            unbuffered, and larger numbers specify the buffer size. If compresslevel
            is given, must be a number between 1 and 9.

            Add a 'U' to mode to open the file for input with universal newline
            support. Any line ending in the input file will be seen as a '\n' in
            Python. Also, a file so opened gains the attribute 'newlines'; the value
            for this attribute is one of None (no newline read yet), '\r', '\n',
            '\r\n' or a tuple containing all the newline types seen. Universal
            newlines are available only when reading.
            """
            bz2.BZ2File.__init__(self, name , mode, buffering, compresslevel)
            self.lock = _Semaphore()
            self.__size = None
        def getSize(self):
            if self.__size is None:
                logger.debug("Measuring size of %s" % self.name)
                with self.lock:
                    pos = self.tell()
                    all = self.read()
                    self.__size = self.tell()
                    self.seek(pos)
            return self.__size
        def setSize(self, value):
            self.__size = value
        size = property(getSize, setSize)
        def __exit__(self, *args, **kwargs):
                """
                Close the file.
                """
                return bz2.BZ2File.close(self)
        def __enter__(self, *args, **kwargs):
            return self


class DebugSemaphore(_Semaphore):
    """
    threading.Semaphore like class with helper for fighting dead-locks
    """
    write_lock = _Semaphore()
    blocked = []
    def __init__(self, *arg, **kwarg):
        _Semaphore.__init__(self, *arg, **kwarg)


    def acquire(self, *arg, **kwarg):
        if self._Semaphore__value == 0:
            with self.write_lock:
                self.blocked.append(id(self))
                sys.stderr.write(os.linesep.join(["Blocking sem %s" % id(self)] + \
                                        traceback.format_stack()[:-1] + [""]))

        return _Semaphore.acquire(self, *arg, **kwarg)

    def release(self, *arg, **kwarg):
        with self.write_lock:
            uid = id(self)
            if uid in self.blocked:
                self.blocked.remove(uid)
                sys.stderr.write("Released sem %s %s" % (uid, os.linesep))
        _Semaphore.release(self, *arg, **kwarg)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *arg, **kwarg):
        self.release()

