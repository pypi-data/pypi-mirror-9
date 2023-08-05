"""

Authors: Henning O. Sorensen & Erik Knudsen
         Center for Fundamental Research: Metal Structures in Four Dimensions
         Risoe National Laboratory
         Frederiksborgvej 399
         DK-4000 Roskilde
         email:henning.sorensen@risoe.dk

mods for fabio by JPW

"""
# Get ready for python3:
from __future__ import with_statement, print_function

import sys, logging
logger = logging.getLogger("openimage")
from .fabioutils  import FilenameObject
from .fabioimage import fabioimage
from . import edfimage
from . import adscimage
from . import tifimage
from . import marccdimage
from . import mar345image
from . import fit2dmaskimage
from . import brukerimage
from . import bruker100image
from . import pnmimage
from . import GEimage
from . import OXDimage
from . import dm3image
from . import HiPiCimage
from . import pilatusimage
from . import fit2dspreadsheetimage
from . import kcdimage
from . import cbfimage
from . import xsdimage
from . import binaryimage
from . import pixiimage
from . import hdf5image
from . import raxisimage

MAGIC_NUMBERS = [
    # "\42\5a" : 'bzipped'
    # "\1f\8b" : 'gzipped'
    (b"FORMAT :        86" , 'bruker'),
    (b"\x4d\x4d\x00\x2a"   , 'tif') ,
    # The marCCD and Pilatus formats are both standard tif with a header
    # hopefully these byte patterns are unique for the formats
    # If not the image will be read, but the is missing
    (b"\x49\x49\x2a\x00\x08\x00"   , 'marccd') ,
    (b"\x49\x49\x2a\x00\x82\x00"   , 'pilatus') ,
    (b"\x49\x49\x2a\x00"   , 'tif') ,
    # ADSC must come before edf
    (b"{\nHEA"             , 'adsc'),
    (b"{"                  , 'edf'),
    (b"\r{"                , 'edf'),
    (b"\n{"                , 'edf'),
    (b"ADEPT"              , 'GE'),
    (b"OD"                 , 'OXD'),
    (b"IM"                 , 'HiPiC'),
    (b'\x2d\x04'           , 'mar345'),
    (b'\xd2\x04'           , 'mar345'),
    (b'\x04\x2d'           , 'mar345'),  # some machines may need byteswapping
    (b'\x04\xd2'           , 'mar345'),
    # hint : MASK in 32 bit
    (b'M\x00\x00\x00A\x00\x00\x00S\x00\x00\x00K\x00\x00\x00' , 'fit2dmask') ,
    (b'\x00\x00\x00\x03'   , 'dm3'),
    (b"No"                 , "kcd"),
    (b"<"                  , "xsd"),
    (b"\n\xb8\x03\x00"     , 'pixi'),
    (b"\x89\x48\x44\x46"   , 'hdf5'),
    (b"R-AXIS"             , 'raxis')
    ]

URL_PREFIX = {"file:":False, "hdf5:":True, "h5:":True}  # Shall we split after the last ":"

def do_magic(byts):
    """ Try to interpret the bytes starting the file as a magic number """
    for magic, format_type in MAGIC_NUMBERS:
        if byts.find(magic) == 0:
            return format_type
        if 0:  # debugging - bruker needed 18 bytes below
            logger.debug("m: %s f: %s", magic, format_type)
            logger.debug("bytes: %s len(bytes) %s", magic, len(magic))
            logger.debug("found: %s", byts.find(magic))
            for i in range(len(magic)):
                logger.debug("%s %s %s %s ", ord(magic[i]), ord(byts[i]), magic[i], byts[i])
    raise Exception("Could not interpret magic string")


def openimage(filename, frame=None):
    """ Try to open an image """
    if isinstance(filename, FilenameObject):
        try:
            logger.debug("Attempting to open %s" % (filename.tostring()))
            obj = _openimage(filename.tostring())
            logger.debug("Attempting to read frame %s from %s" % (frame,
                filename.tostring()))
            obj = obj.read(filename.tostring(), frame)
        except Exception as ex:
            # multiframe file
            # logger.debug( "DEBUG: multiframe file, start # %d"%(
            #    filename.num)
            logger.debug("Exception %s, trying name %s" % (ex, filename.stem))
            obj = _openimage(filename.stem)
            logger.debug("Reading frame %s from %s" % (filename.num, filename.stem))
            obj.read(filename.stem, frame=filename.num)
    else:
        logger.debug("Attempting to open %s" % (filename))
        obj = _openimage(filename)
        logger.debug("Attempting to read frame %s from %s" % (frame, filename))
        obj = obj.read(filename, frame)
    return obj


def openheader(filename):
    """ return only the header"""
    obj = _openimage(filename)
    obj.readheader(filename)
    return obj


def _openimage(filename):
    """
    determine which format for a filename
    and return appropriate class which can be used for opening the image
    """
    lower_filename = filename.lower()
    for prefix in URL_PREFIX:
        if lower_filename.startswith(prefix):
            filename = filename[len(prefix):]
            if filename.startswith("//"):
                filename = filename[2:]
            if URL_PREFIX[prefix]:  # process :path[slice,:,:]
                if "[" in filename:
                    filename = filename[:filename.index("[")]
                if ":" in filename:
                    col_split = filename.split(":")
                    filename = ":".join(col_split[:-1])

    try:
        imo = fabioimage()
        byts = imo._open(filename).read(18)
        filetype = do_magic(byts)
        if filetype == "marccd" and filename.find("mccd") == -1:
            # Cannot see a way around this. Need to find something
            # to distinguish mccd from regular tif...
            filetype = "tif"
    except IOError as error:
        logger.error("%s: File probably does not exist", error)
        raise error
    except:
        try:
            file_obj = FilenameObject(filename=filename)
            if file_obj == None:
                raise Exception("Unable to deconstruct filename")
            if (file_obj.format is not None) and\
                len(file_obj.format) != 1 and \
                type(file_obj.format) != type(["list"]):
                # one of OXD/ ADSC - should have got in previous
                raise Exception("openimage failed on magic bytes & name guess")
            filetype = file_obj.format
            # UNUSED filenumber = file_obj.num
        except Exception as error:
            logger.error(error)
            import traceback
            traceback.print_exc()
            raise Exception("Fabio could not identify " + filename)
    klass_name = "".join(filetype) + 'image'
    module = sys.modules.get("fabio." + klass_name, None)
    if module is not None:
        if hasattr(module, klass_name):
            klass = getattr(module, klass_name)
        else:
            raise Exception("Module %s has no image class" % module)
    else:
        raise Exception("Filetype not known %s %s" % (filename, klass_name))
    obj = klass()
    # skip the read for read header
    return obj





