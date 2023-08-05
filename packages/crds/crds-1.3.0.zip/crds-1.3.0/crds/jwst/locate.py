"""This module provides functions which determine various observatory
specific policies for JWST:

1. How to convert reference file basenames to fully specified paths.

2. How to manage parameters for reference file Validator objects used
in the certification of reference files. 
"""
import os.path
import re

from crds import (log, rmap, data_file, config, utils)
from . import tpn

# =======================================================================

try:
    from jwst_lib.models import DataModel
    MODEL = DataModel()
except Exception:
    MODEL = None

# =======================================================================

HERE = os.path.dirname(__file__) or "./"

# =======================================================================

def test():
    """Run the module doctests."""
    import doctest, locate
    return doctest.testmod(locate)

# =======================================================================

def locate_server_reference(reference):
    """Return the absolute path for the server-side copy of a reference file. Default cache layout."""
    return config.locate_file(reference, "jwst")


def reference_exists(reference):
    """Return True iff basename `reference` is known/exists in CRDS.
    """
    try:
        where = locate_server_reference(reference)
    except KeyError:
        return False
    return os.path.exists(where)

# =======================================================================

# These two functions decouple the generic reference file certifier program 
# from observatory-unique ways of specifying and caching Validator parameters.

from crds.jwst.tpn import get_tpninfos   #  reference_name_to_validator_key, mapping_validator_key  defined here.
from crds.jwst.__init__ import INSTRUMENTS, FILEKINDS, EXTENSIONS, FILETYPE_TO_FILEKIND, FILEKIND_TO_FILETYPE

# =======================================================================

REF_EXT_RE = re.compile(r"\.fits|\.r\dh$")

def get_file_properties(filename):
    """Figure out (instrument, filekind, serial) based on `filename` which
    should be a mapping or FITS reference file.

    >> get_file_properties("./hst_acs_biasfile_0001.rmap")
    ('acs', 'biasfile')

    >> get_file_properties("./hst_acs_biasfile_0001.pmap")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid .pmap filename './hst_acs_biasfile_0001.pmap'

    >> get_file_properties("test_data/s7g1700gl_dead.fits")
    """
    if rmap.is_mapping(filename):
        return decompose_newstyle_name(filename)[2:4]
    elif REF_EXT_RE.search(filename):
        result = get_reference_properties(filename)[2:4]
    else:
        try:
            result = properties_inside_mapping(filename)
        except Exception, exc:
            result = get_reference_properties(filename)[2:4]
    assert result[0] in INSTRUMENTS+[""], "Bad instrument " + \
        repr(result[0]) + " in filename " + repr(filename)
    assert result[1] in FILEKINDS+[""], "Bad filekind " + \
        repr(result[1]) + " in filename " + repr(filename)
    return result

def decompose_newstyle_name(filename):
    """
    >> decompose_newstyle_name("./hst.pmap")
    ('.', 'hst', '', '', '', '.pmap')

    >> decompose_newstyle_name("./hst_0001.pmap")
    ('.', 'hst', '', '', '0001', '.pmap')

    >> decompose_newstyle_name("./hst_acs.imap")
    ('.', 'hst', 'acs', '', '', '.imap')

    >> decompose_newstyle_name("./hst_acs_0001.imap")
    ('.', 'hst', 'acs', '', '0001', '.imap')

    >> decompose_newstyle_name("./hst_acs_biasfile.rmap")
    ('.', 'hst', 'acs', 'biasfile', '', '.rmap')

    >> decompose_newstyle_name("./hst_acs_biasfile_0001.rmap")
    ('.', 'hst', 'acs', 'biasfile', '0001', '.rmap')

    >> decompose_newstyle_name("./hst_acs_biasfile.fits")
    ('.', 'hst', 'acs', 'biasfile', '', '.fits')

    >> decompose_newstyle_name("./hst_acs_biasfile_0001.fits")
    ('.', 'hst', 'acs', 'biasfile', '0001', '.fits')
    """
    path, parts, ext = _get_fields(filename)
    observatory = parts[0]
    serial = list_get(parts, 3, "")

    if ext == ".pmap":
        assert len(parts) in [1,2], "Invalid .pmap filename " + repr(filename)
        instrument, filekind = "", ""
        serial = list_get(parts, 1, "")
    elif ext == ".imap":
        assert len(parts) in [2,3], "Invalid .imap filename " + repr(filename)
        instrument = parts[1]
        filekind = ""
        serial = list_get(parts, 2, "")
    else:
        assert len(parts) in [3,4], "Invalid filename " + repr(filename)
        instrument = parts[1]
        filekind = parts[2]
        serial = list_get(parts, 3, "")

    assert instrument in INSTRUMENTS+[""], "Invalid instrument " + \
        repr(instrument) + " in name " + repr(filename)
    assert filekind in FILEKINDS+[""], "Invalid filekind " + \
        repr(filekind) + " in name " + repr(filename)
    assert re.match("\d*", serial), "Invalid id field " + \
        repr(id) + " in name " + repr(filename)
    # extension may vary for upload temporary files.

    return path, observatory, instrument, filekind, serial, ext

def properties_inside_mapping(filename):
    """Load `filename`s mapping header to discover and 
    return (instrument, filekind).
    """
    map = rmap.fetch_mapping(filename)
    if map.filekind == "PIPELINE":
        result = "", ""
    elif map.filekind == "INSTRUMENT":
        result = map.instrument, ""
    else:
        result = map.instrument, map.filekind
    return result

def _get_fields(filename):
    path = os.path.dirname(filename)
    name = os.path.basename(filename)
    name, ext = os.path.splitext(name)
    parts = name.split("_")
    return path, parts, ext

def list_get(l, index, default):
    try:
        return l[index]
    except IndexError:
        return default

CDBS_DIRS_TO_INSTR = {
   "/jref/":"acs",
   "/oref/":"stis",
   "/iref/":"wfc3",
   "/lref/":"cos",
   "/nref/":"nicmos",
   
   "/upsf/":"wfpc2",
   "/uref/":"wfpc2",
   "/uref_linux/":"wfpc2",
   
   "/yref/" : "fos",
   "/zref/" : "hrs",
   
}

def get_reference_properties(filename):
    """Figure out FITS (instrument, filekind, serial) based on `filename`.
    """
    try:   # Hopefully it's a nice new standard filename, easy
        return decompose_newstyle_name(filename)
    except AssertionError:  # cryptic legacy paths & names, i.e. reality
        pass
    # If not, dig inside the FITS file, slow
    return ref_properties_from_header(filename)

def ref_properties_from_cdbs_path(filename):
    """Based on a HST CDBS `filename`,  return (instrument, filekind, serial). 
    Raise AssertionError if it's not a good filename.
    """
    path, fields, ext = _get_fields(filename)
    # For legacy files,  just use the root filename as the unique id
    serial = os.path.basename(os.path.splitext(filename)[0])
    # First try to figure everything out by decoding filename. fast
    for idir in CDBS_DIRS_TO_INSTR:
        if idir in filename:
            instrument = CDBS_DIRS_TO_INSTR[idir]
            break
    else:
        assert False, "CDBS instrument directory not found in filepath"
    ext = fields[-1]
    try:
        filekind = tpn.extension_to_filekind(instrument, ext)
    except KeyError:
        assert False, "Couldn't map extension " + repr(ext) + " to filekind."
    return path, "jwst", instrument, filekind, serial, ext

# =======================================================================

def filetype_to_filekind(filetype):
    filetype = filetype.upper()
    if filetype in FILETYPE_TO_FILEKIND:
        return FILETYPE_TO_FILEKIND[filetype].lower()
    else:
        return filetype.lower()

def filekind_to_filetype(filekind):
    filekind = filekind.upper()
    if filekind in FILEKIND_TO_FILETYPE:
        return FILEKIND_TO_FILETYPE[filekind]
    else:
        return filekind

def ref_properties_from_header(filename):
    """Look inside FITS `filename` header to determine instrument, filekind.
    """
    # For legacy files,  just use the root filename as the unique id
    path, parts, ext = _get_fields(filename)
    serial = os.path.basename(os.path.splitext(filename)[0])
    header = data_file.get_fits_header_union(filename)
    instrument = header.get("INSTRUME", "UNDEFINED").lower()
    assert instrument in INSTRUMENTS, \
        "Invalid instrument " + repr(instrument) + " in file " + repr(filename)
    filekind = header.get("REFTYPE", "UNDEFINED").lower()
    assert filekind in FILEKINDS, \
        "Invalid file type " + repr(filekind) + " in file " + repr(filename)    
    return path, "jwst", instrument, filekind, serial, ext

# =============================================================================

def reference_name_to_validator_key(filename):
    """Given a reference filename `fitsname`,  return a dictionary key
    suitable for caching the reference type's Validator.
    
    Return (instrument, filekind)
    """
    _path, _obsv, instrument, filekind, _serial, _ext = get_reference_properties(filename)
    return (instrument, filekind, ".tpn")

def mapping_validator_key(mapping):
    """Return the TPN key for ReferenceMapping `mapping`."""
    return (mapping.instrument, mapping.filekind, "_ld.tpn")
# =============================================================================

def reference_keys_to_dataset_keys(rmapping, header):
    """Given a header dictionary for a reference file, map the header back to keys
    relevant to datasets.  So for ACS biasfile the reference says BINAXIS1 but
    the dataset says NUMCOLS.  This would convert { "BINAXIS1": 1024 } to {
    "NUMCOLS" : 1024 }.
    
    In general,  rmap parkeys are matched against datset values and are defined
    as dataset header keywords.   For refactoring though,  what's initially
    available are reference file keywords...  which need to be mapped into the
    terms rmaps know:  dataset keywords.
    """
    header = dict(header)
    try:
        translations = rmapping.reference_to_dataset
        for key in translations:
            if key in header:
                header[translations[key]] = header[key]
    except AttributeError:
        pass
    return header

# =============================================================================

def expand_wildcards(rmapping, header):
    """See hst/substitutions.py"""
    return dict(header)


def condition_matching_header(rmapping, header):
    """Normalize header values for .rmap reference insertion."""
    return dict(header)   # NOOP for JWST,  may have to revisit

# ============================================================================

class MissingDependencyError(Exception):
    """A required package is missing."""

def fits_to_parkeys(fits_header):
    """Map a FITS header onto rmap parkeys appropriate for JWST."""
    if MODEL is None:
        raise MissingDependencyError("JWST data models are not installed.   Cannot fits_to_parkeys().")
    parkeys = {}
    for key, value in fits_header.items():
        key, value = str(key), str(value)
        if not key.lower().startswith("meta."):
            pk = MODEL.find_fits_keyword(key.upper(), return_result=True)
            if not pk:
                pk = key
            else:
                assert len(pk) == 1, "CRDS JWST Data Model ambiguity on " + \
                    repr(key) + " = " + repr(pk)
                pk = pk[0]
        else:
            pk = key
        pk = pk.upper()
        parkeys[pk] = value
    return parkeys

# ============================================================================

def get_env_prefix(instrument):
    """Return the environment variable prefix (IRAF prefix) for `instrument`."""
    return "crds://"

def locate_file(refname, mode=None):
    """Given a valid reffilename in CDBS or CRDS format,  return a cache path for the file.
    The aspect of this which is complicated is determining instrument and an instrument
    specific sub-directory for it based on the filename alone,  not the file contents.
    """
    _path,  _observatory, instrument, _filekind, _serial, _ext = get_reference_properties(refname)
    rootdir = locate_dir(instrument, mode)
    return  os.path.join(rootdir, os.path.basename(refname))

def locate_dir(instrument, mode=None):
    """Locate the instrument specific directory for a reference file."""
    if mode is  None:
        mode = config.get_crds_ref_subdir_mode(observatory="jwst")
    else:
        config.check_crds_ref_subdir_mode(mode)
    crds_refpath = config.get_crds_refpath("jwst")
    if mode == "instrument":   # use simple names inside CRDS cache.
        rootdir = os.path.join(crds_refpath, instrument)
        if not os.path.exists(rootdir):
            utils.ensure_dir_exists(rootdir + "/locate_dir.fits")
    elif mode == "flat":    # use original flat cache structure,  all instruments in same directory.
        rootdir = crds_refpath
    else:
        raise ValueError("Unhandled reference file location mode " + repr(mode))
    return rootdir

# ============================================================================
def load_all_type_constraints():
    """Load all the JWST type constraint files."""
    raise NotImplementedError("expected failure,  JWST type constraints not implemented yet.")

