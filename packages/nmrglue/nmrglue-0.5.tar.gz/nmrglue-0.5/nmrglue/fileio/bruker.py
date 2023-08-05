"""
Functions for reading and writing Bruker binary (ser/fid) files, Bruker
JCAMP-DX parameter (acqus) files, and Bruker pulse program (pulseprogram)
files.
"""

from __future__ import print_function, division

__developer_info__ = """
Bruker file format information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Bruker binary files (ser/fid) store data as an array of int32s whose endiness
is determinded by the parameter BYTORDA (1 = big endian, 0 = little endian).
Typically the direct dimension is digitally filtered. The exact method of
removing this filter is unknown but an approximation is avaliable.

Bruker JCAMP-DX files (acqus, etc) are text file which are described by the
`JCAMP-DX standard <http://www.jcamp-dx.org/>`_.  Bruker parameters are
prefixed with a '$'.

Bruker pulseprogram files are text files described in various Bruker manuals.
Of special important are lines which describe external variable assignments
(surrounded by "'s), loops (begin with lo), phases (contain ip of dp) or
increments (contain id, dd, ipu or dpu).  These lines are parsed when reading
the file with nmrglue.

"""

from functools import reduce
import os
from warnings import warn

import numpy as np

from . import fileiobase
from ..process import proc_base


# data creation

def create_data(data):
    """
    Create a bruker data array (recast into a complex128 or int32)
    """
    if np.iscomplexobj(data):
        return np.array(data, dtype='complex128')
    else:
        return np.array(data, dtype='int32')


# universal dictionary functions

def guess_udic(dic, data):
    """
    Guess parameters of universal dictionary from dic, data pair.

    Parameters
    ----------
    dic : dict
        Dictionary of Bruker parameters.
    data : ndarray
        Array of NMR data.

    Returns
    -------
    udic : dict
        Universal dictionary of spectral parameters.

    """
    # XXX if pprog, acqus are in dic use them

    # create an empty universal dictionary
    udic = fileiobase.create_blank_udic(data.ndim)

    # update default values
    for b_dim in range(data.ndim):
        udic[b_dim]["size"] = data.shape[b_dim]

        # try to add additional parameter from acqus dictionary keys
        try:
            add_axis_to_udic(udic, dic, b_dim)
        except:
            warn("Failed to determine udic parameters for dim: %i" % (b_dim))
    return udic


def add_axis_to_udic(udic, dic, udim):
    """
    Add axis parameters to a udic.

    Parameters
    ----------
    udic : dict
        Universal dictionary to update, modified in place.
    dic : dict
        Bruker dictionary used to determine axes parameters.
    dim : int
        Universal dictionary dimension to update.

    """
    # This could still use some work
    b_dim = udic['ndim'] - udim - 1  # last dim
    acq_file = "acqu" + str(b_dim + 1) + "s"

    if acq_file == "acqu1s":
        acq_file = "acqus"   # Because they're inconsistent,...

    udic[udim]["sw"] = dic[acq_file]["SW_h"]
    udic[udim]["label"] = dic[acq_file]["NUC1"]
    udic[udim]["car"] = dic[acq_file]["O1"]

    if "acqus" in dic and dic["acqus"]["NUC2"] == "15N":
        # Gyromagnetic ratio of 15N is negative
        udic[udim]["obs"] = (dic[acq_file]["BF1"] -
                             dic[acq_file]["O1"] / 1.e6)
    else:
        udic[udim]["obs"] = (dic[acq_file]["BF1"] +
                             dic[acq_file]["O1"] / 1.e6)

    if acq_file == "acqus":
        if dic['acqus']['AQ_mod'] == 0:     # qf
            udic[udim]['complex'] = False
        else:
            udic[udim]['complex'] = True
    else:
        aq_mod = dic[acq_file]["FnMODE"]
        if aq_mod == 0:
            udic[udim]["encoding"] = "undefined"
        elif aq_mod == 1:
            udic[udim]["encoding"] = "magnitude"  # qf
        elif aq_mod == 2:
            udic[udim]["encoding"] = "magnitude"  # qsec
        elif aq_mod == 3:
            udic[udim]["encoding"] = "tppi"
        elif aq_mod == 4:
            udic[udim]["encoding"] = "states"
        elif aq_mod == 5:
            udic[udim]["encoding"] = "states-tppi"  # states-tppi
        elif aq_mod == 6:
            udic[udim]["encoding"] = "echo-antiecho"  # echo-antiecho

    return udic


def create_dic(udic):
    """
    Create a Bruker parameter dictionary from a universal dictionary.

    Parameters
    ----------
    udic : dict
        Universal dictionary of spectral parameters.

    Returns
    -------
    dic : dict
        Dictionary of Bruker parameters.

    """
    ndim = udic['ndim']

    # determind the size in bytes
    if udic[ndim - 1]["complex"]:
        bytes = 8
    else:
        bytes = 4

    for k in range(ndim):
        bytes *= udic[k]["size"]

    dic = {"FILE_SIZE": bytes}

    # create the pprog dictionary parameter
    dic["pprog"] = {'incr': [[], [1]] * (ndim * 2 - 2),
                    'loop': [2] * (ndim * 2 - 2),
                    'ph_extra': [[]] * (ndim * 2 - 2),
                    'phase': [[]] * (ndim * 2 - 2),
                    'var': {}}

    # create acqus dictionary parameters and fill in loop sizes
    dic['acqus'] = create_acqus_dic(udic[ndim - 1], direct=True)
    if ndim >= 2:
        dic["acqu2s"] = create_acqus_dic(udic[ndim - 2])
        dic["pprog"]["loop"][1] = udic[ndim - 2]["size"] // 2
    if ndim >= 3:
        dic["acqu3s"] = create_acqus_dic(udic[ndim - 3])
        dic["pprog"]["loop"][3] = udic[ndim - 3]["size"] // 2
    if ndim >= 4:
        dic["acqu4s"] = create_acqus_dic(udic[ndim - 4])
        dic["pprog"]["loop"][5] = udic[ndim - 4]["size"] // 2

    return dic


def create_acqus_dic(adic, direct=False):
    """
    Create a Bruker acqus dictionary from an Universal axis dictionary.
    Set direct=True for direct dimension.
    """
    if adic["complex"]:
        AQ_mod = 3
        if direct:
            TD = int(np.ceil(adic["size"] / 256.) * 256) * 2
        else:
            TD = adic["size"]
    else:
        AQ_mod = 1
        if direct:
            TD = int(np.ceil(adic["size"] / 256.) * 256)
        else:
            TD = adic["size"]

    s = '##NMRGLUE automatically created parameter file'
    return {'_comments': [], '_coreheader': [s], 'AQ_mod': AQ_mod, 'TD': TD}


# Global read/write function and related utilities

def read(dir=".", bin_file=None, acqus_files=None, pprog_file=None,
         shape=None, cplex=None, big=None, read_pulseprogram=True,
         read_acqus=True):
    """
    Read Bruker files from a directory.

    Parameters
    ----------
    dir : str
        Directory to read from.
    bin_file : str, optional
        Filename of binary file in directory. None uses standard files.
    acqus_files : list, optional
        List of filename(s) of acqus parameter files in directory. None uses
        standard files.
    pprog_file : str, optional
        Filename of pulse program in directory. None uses standard files.
    shape : tuple, optional
        Shape of resulting data.  None will guess the shape from the spectral
        parameters.
    cplex : bool, optional
        True is direct dimension is complex, False otherwise. None will guess
        quadrature from spectral parameters.
    big : bool or None, optional
        Endiness of binary file. True of big-endian, False for little-endian,
        None to determine endiness from acqus file(s).
    read_pulseprogram : bool, optional
        True to read pulse program, False prevents reading.
    read_acqus : bool, optional
        True to read acqus files(s), False prevents reading.

    Returns
    -------
    dic : dict
        Dictionary of Bruker parameters.
    data : ndarray
        Array of NMR data.

    See Also
    --------
    read_pdata : Read Bruker processed files.
    read_lowmem : Low memory reading of Bruker files.
    write : Write Bruker files.

    """
    if os.path.isdir(dir) is not True:
        raise IOError("directory %s does not exist" % (dir))

    # determind parameter automatically
    if bin_file is None:
        if os.path.isfile(os.path.join(dir, "fid")):
            bin_file = "fid"
        elif os.path.isfile(os.path.join(dir, "ser")):
            bin_file = "ser"
        else:
            raise IOError("No Bruker binary file could be found in %s" % (dir))

    if acqus_files is None:
        acqus_files = []
        for f in ["acqus", "acqu2s", "acqu3s", "acqu4s"]:
            if os.path.isfile(os.path.join(dir, f)):
                acqus_files.append(f)

    if pprog_file is None:
        pprog_file = "pulseprogram"

    # create an empty dictionary
    dic = dict()

    # read the acqus_files and add to the dictionary
    if read_acqus:
        for f in acqus_files:
            dic[f] = read_jcamp(os.path.join(dir, f))

    # read the pulse program and add to the dictionary
    if read_pulseprogram:
        try:
            dic["pprog"] = read_pprog(os.path.join(dir, pprog_file))
        except:
            warn('Error reading the pulse program')

    # determind file size and add to the dictionary
    dic["FILE_SIZE"] = os.stat(os.path.join(dir, bin_file)).st_size

    # determind shape and complexity for direct dim if needed
    if shape is None or cplex is None:
        gshape, gcplex = guess_shape(dic)
        if gcplex is True:    # divide last dim by 2 if complex
            t = list(gshape)
            t[-1] = t[-1] / 2
            gshape = tuple(t)
    if shape is None:
        shape = gshape
    if cplex is None:
        cplex = gcplex

    # determind endianness (assume little-endian unless BYTORDA is 1)
    if big is None:
        big = False     # default value
        if "acqus" in dic and "BYTORDA" in dic["acqus"]:
            if dic["acqus"]["BYTORDA"] == 1:
                big = True
            else:
                big = False

    # read the binary file
    f = os.path.join(dir, bin_file)
    null, data = read_binary(f, shape=shape, cplex=cplex, big=big)
    return dic, data


def read_lowmem(dir=".", bin_file=None, acqus_files=None, pprog_file=None,
                shape=None, cplex=None, big=None, read_pulseprogram=True,
                read_acqus=True):
    """
    Read Bruker files from a directory using minimal amounts of memory.

    See :py:func:`read` for Parameters.

    Returns
    -------
    dic : dict
        Dictionary of Bruker parameters.
    data : array_like
        Low memory object which can access NMR data on demand.

    See Also
    --------
    read : Read Bruker files.
    write_lowmem : Write Bruker files using minimal amounts of memory.

    """

    if os.path.isdir(dir) is not True:
        raise IOError("Directory %s does not exist" % (dir))

    # determind parameter automatically
    if bin_file is None:
        if os.path.isfile(os.path.join(dir, "fid")):
            bin_file = "fid"
        elif os.path.isfile(os.path.join(dir, "ser")):
            bin_file = "ser"
        else:
            raise IOError("no Bruker binary file could be found in %s" % (dir))

    if acqus_files is None:
        acqus_files = []
        for f in ["acqus", "acqu2s", "acqu3s", "acqu4s"]:
            if os.path.isfile(os.path.join(dir, f)):
                acqus_files.append(f)

    if pprog_file is None:
        pprog_file = "pulseprogram"

    # create an empty dictionary
    dic = dict()

    # read the acqus_files and add to the dictionary
    if read_acqus:
        for f in acqus_files:
            dic[f] = read_jcamp(os.path.join(dir, f))

    # read the pulse program and add to the dictionary
    if read_pulseprogram:
        dic["pprog"] = read_pprog(os.path.join(dir, pprog_file))

    # determind file size and add to the dictionary
    dic["FILE_SIZE"] = os.stat(os.path.join(dir, bin_file)).st_size

    # determind shape and complexity for direct dim if needed
    if shape is None or cplex is None:
        gshape, gcplex = guess_shape(dic)
        if gcplex is True:    # divide last dim by 2 if complex
            t = list(gshape)
            t[-1] = t[-1] // 2
            gshape = tuple(t)
    if shape is None:
        shape = gshape
    if cplex is None:
        cplex = gcplex

    # determine endianness (assume little-endian unless BYTORDA is 1)
    if big is None:
        big = False     # default value
        if "acqus" in dic and "BYTORDA" in dic["acqus"]:
            if dic["acqus"]["BYTORDA"] == 1:
                big = True
            else:
                big = False

    # read the binary file
    f = os.path.join(dir, bin_file)
    null, data = read_binary_lowmem(f, shape=shape, cplex=cplex, big=big)
    return dic, data


def write(dir, dic, data, bin_file=None, acqus_files=None, pprog_file=None,
          overwrite=False, big=None, write_prog=True, write_acqus=True):
    """
    Write Bruker files to disk.

    Parameters
    ----------
    dir : str
        Directory to write files to.
    dir : dict
        Dictionary of Bruker parameters.
    data : array_like
        Array of NMR data
    bin_file : str, optional
        Filename of binary file in directory. None uses standard files.
    acqus_files : list, optional
        List of filename(s) of acqus parameter files in directory. None uses
        standard files.
    pprog_file : str, optional
        Filename of pulse program in directory. None uses standard files.
    overwrite : bool, optional
        Set True to overwrite files, False will raise a Warning if files
        exist.
    big : bool or None, optional
        Endiness of binary file. True of big-endian, False for little-endian,
        None to determine endiness from Bruker dictionary.
    write_pprog : bool, optional
        True to write the pulse program file, False prevents writing.
    write_acqus : bool, optional
        True to write the acqus files(s), False prevents writing.

    See Also
    --------
    write_lowmem : Write Bruker files using minimal amounts of memory.
    read : Read Bruker files.

    """
    # determind parameters automatically
    if bin_file is None:
        if data.ndim == 1:
            bin_file = "fid"
        else:
            bin_file = "ser"

    if acqus_files is None:
        acq = ["acqus", "acqu2s", "acqu3s", "acqu4s"]
        acqus_files = [k for k in acq if (k in dic)]

    if pprog_file is None:
        pprog_file = "pulseprogram"

    # write out the acqus files
    if write_acqus:
        for f in acqus_files:
            write_jcamp(dic[f], os.path.join(dir, f), overwrite=overwrite)

    # write out the pulse program
    if write_prog:
        write_pprog(os.path.join(dir, pprog_file), dic["pprog"],
                    overwrite=overwrite)

    # determind endianness (assume little-endian unless BYTORDA is 1)
    if big is None:
        big = False     # default value
        if "acqus" in dic and "BYTORDA" in dic["acqus"]:
            if dic["acqus"]["BYTORDA"] == 1:
                big = True
            else:
                big = False

    # write out the binary data
    bin_full = os.path.join(dir, bin_file)
    write_binary(bin_full, dic, data, big=big, overwrite=overwrite)
    return


def write_lowmem(dir, dic, data, bin_file=None, acqus_files=None,
                 pprog_file=None, overwrite=False, big=None, write_prog=True,
                 write_acqus=True):
    """
    Write Bruker files using minimal amounts of memory (trace by trace).

    See :py:func:`write` for Parameters.

    See Also
    --------
    write : Write Bruker files.
    read_lowmem : Read Bruker files using minimal amounts of memory.

    """
    # determind parameters automatically
    if bin_file is None:
        if data.ndim == 1:
            bin_file = "fid"
        else:
            bin_file = "ser"

    if acqus_files is None:
        acq = ["acqus", "acqu2s", "acqu3s", "acqu4s"]
        acqus_files = [k for k in acq if (k in dic)]

    if pprog_file is None:
        pprog_file = "pulseprogram"

    # write out the acqus files
    if write_acqus:
        for f in acqus_files:
            write_jcamp(dic[f], os.path.join(dir, f), overwrite=overwrite)

    # write out the pulse program
    if write_prog:
        write_pprog(os.path.join(dir, pprog_file), dic["pprog"],
                    overwrite=overwrite)

    # determind endianness (assume little-endian unless BYTORDA is 1)
    if big is None:
        big = False     # default value
        if "acqus" in dic and "BYTORDA" in dic["acqus"]:
            if dic["acqus"]["BYTORDA"] == 1:
                big = True
            else:
                big = False

    # write out the binary data
    bin_full = os.path.join(dir, bin_file)
    write_binary_lowmem(bin_full, dic, data, big=big, overwrite=overwrite)
    return


def guess_shape(dic):
    """
    Determine data shape and complexity from Bruker dictionary.

    Returns
    -------
    shape : tuple
        Shape of data in Bruker binary file (R+I for all dimensions).
    cplex : bool
        True for complex data in last (direct) dimension, False otherwise.

    """
    # determine complexity of last (direct) dimension
    try:
        aq_mod = dic["acqus"]["AQ_mod"]
    except KeyError:
        aq_mod = 0

    if aq_mod == 0 or aq_mod == 2:
        cplex = False
    elif aq_mod == 1 or aq_mod == 3:
        cplex = True
    else:
        raise ValueError("Unknown Aquisition Mode")

    # file size
    try:
        fsize = dic["FILE_SIZE"]
    except KeyError:
        warn("cannot determine shape do to missing FILE_SIZE key")
        return (1,), True

    # extract td0,td1,td2,td3 from dictionaries
    try:
        td0 = float(dic["acqus"]["TD"])
    except KeyError:
        td0 = 1024   # default value

    try:
        td2 = int(dic["acqu2s"]["TD"])
    except KeyError:
        td2 = 0     # default value

    try:
        td1 = float(dic["acqu3s"]["TD"])
    except KeyError:
        td1 = int(td2)   # default value

    try:
        td3 = int(dic["acqu4s"]["TD"])
    except KeyError:
        td3 = int(td1)     # default value

    # last (direct) dimension is given by "TD" parameter in acqus file
    # rounded up to nearest 256
    # next-to-last dimension may be given by "TD" in acqu2s. In 3D+ data
    # this is often the sum of the indirect dimensions
    shape = [0, 0, td2, int(np.ceil(td0 / 256.) * 256.)]

    # additional dimension given by data size
    if shape[2] != 0 and shape[3] != 0:
        shape[1] = fsize // (shape[3] * shape[2] * 4)
        shape[0] = fsize // (shape[3] * shape[2] * 16 * 4)

    # if there in no pulse program parameters in dictionary return currect
    # shape after removing zeros
    if "pprog" not in dic or "loop" not in dic["pprog"]:
        return tuple([int(i) for i in shape if i > 1]), cplex

    # if pulseprogram dictionary is missing loop or incr return current shape
    pprog = dic["pprog"]
    if "loop" not in pprog or "incr" not in pprog:
        return tuple([int(i) for i in shape if i > 1]), cplex

    # determine indirect dimension sizes from pulseprogram parameters
    loop = pprog["loop"]
    loopn = len(loop)       # number of loops
    li = [len(i) for i in pprog["incr"]]    # length of incr lists

    # replace td0,td1,td2,td3 in loop list
    rep = {'td0': td0, 'td1': td1, 'td2': td2, 'td3': td3}
    for i, v in enumerate(loop):
        if v in rep.keys():
            loop[i] = rep[v]

    # if the loop variables contains strings, return current shape
    # these variables could be resolved from the var key in the pprog dict
    # but this would require executing unknown code to perform the
    # arithmetic present in the string.
    if str in [type(e) for e in loop]:
        return tuple([int(i) for i in shape if i > 1]), cplex

    # size of indirect dimensions based on number of loops in pulse program
    # there are two kinds of loops, active and passive.
    # active loops are from indirect dimension increments, the corresponding
    # incr lists should have non-zero length and the size of the dimension
    # is twice that of the active loop size.
    # passive loops are from phase cycles and similar elements, these should
    # have zero length incr lists and should be of length 2.

    # The following checks for these and updates the indirect dimension
    # if the above is found.
    if loopn == 1:    # 2D with no leading passive loops
        if li[0] != 0:
            shape[2] = loop[0]
            shape = shape[-2:]

    elif loopn == 2:  # 2D with one leading passive loop
        if loop[0] == 2 and li[0] == 0 and li[1] != 0:
            shape[2] = 2 * loop[1]
            shape = shape[-2:]

    elif loopn == 3:  # 2D with two leading passive loops
        if (loop[0] == 2 and loop[1] == 2 and li[0] == 0 and li[1] == 0
                and li[2] != 0):
            shape[2] = 2 * loop[2]
            shape = shape[-2:]

    elif loopn == 4:  # 3D with one leading passive loop for each indirect dim
        if loop[0] == 2 and li[0] == 0 and li[1] != 0:
            shape[2] = 2 * loop[1]
        if loop[2] == 2 and li[2] == 0 and li[3] != 0:
            shape[1] = 2 * loop[3]
            shape = shape[-3:]

    elif loopn == 5:  # 3D with two/one leading passive loops
        if loop[1] == 2 and li[0] == 0 and li[1] == 0 and li[2] != 0:
            shape[2] = 2 * loop[2]
        if loop[3] == 2 and li[0] == 0 and li[3] == 0 and li[4] != 0:
            shape[1] = 2 * loop[4]
            shape = shape[-3:]

    elif loopn == 6:  # 4D with one leading passive loop for each indirect dim
        if loop[0] == 2 and li[0] == 0 and li[1] != 0:
            shape[2] = 2 * loop[1]
        if loop[2] == 2 and li[2] == 0 and li[3] != 0:
            shape[1] = 2 * loop[3]
        if loop[4] == 2 and li[4] == 0 and li[5] != 0:
            shape[0] = 2 * loop[5]

    elif loopn == 7:
        if loop[1] == 2 and li[0] == 0 and li[1] == 0 and li[2] != 0:
            shape[2] = 2 * loop[2]
        if loop[3] == 2 and li[0] == 0 and li[3] == 0 and li[4] != 0:
            shape[1] = 2 * loop[4]
        if loop[5] == 2 and li[0] == 0 and li[5] == 0 and li[6] != 0:
            shape[0] = 2 * loop[6]

    return tuple([int(i) for i in shape if i >= 2]), cplex


# Bruker processed binary (1r, 1i, 2rr, 2ri, etc) reading

def read_pdata(dir=".", bin_files=None, procs_files=None, read_procs=True,
               shape=None, submatrix_shape=None, all_components=False,
               big=None):
    """
    Read processed Bruker files from a directory.

    Parameters
    ----------
    dir : str
        Directory to read from.
    bin_files : list of str, optional
        List of filename of binary file in directory. None uses standard
        files.
    procs_files : list, optional
        List of filename(s) of procs parameter files in directory. None uses
        standard files.
    read_procss : bool, optional
        True to read procs files(s), False prevents reading.
    shape : tuple, optional
        Shape of resulting data.  None will guess the shape from the
        parameters in the procs file(s).
    submatrix_shape : tuple, optional
        Shape of submatrix for 2D+ data.  None will guess the shape from
        the metadata in the procs file(s).
    all_components : bool
        True to return all a list of all components, False returns just the
        all real component (1r, 2rr, 3rrr, etc).
    big : bool or None, optional
        Endiness of binary file. True of big-endian, False for little-endian,
        None to determine endiness from procs file(s).

    Returns
    -------
    dic : dict
        Dictionary of Bruker parameters.
    data : ndarray or list
        Array of NMR data.  If all_compoents is True this is a list of array
        with each quadrature component.

    Notes
    -----
    There is currently no support for writing Bruker processed files or
    reading processed files using minimal memory.

    """
    # TODO read_pdata_lowmem, write_pdata

    if os.path.isdir(dir) is not True:
        raise IOError("directory %s does not exist" % (dir))

    # find binary files
    if bin_files is None:
        if os.path.isfile(os.path.join(dir, "1r")):
            if all_components:
                bin_files = ['1r', '1i']
            else:
                bin_files = ['1r']
        elif os.path.isfile(os.path.join(dir, "2rr")):
            if all_components:
                bin_files = ['2rr', '2ri', '2ir', '2ii']
            else:
                bin_files = ['2rr']
        elif os.path.isfile(os.path.join(dir, "3rrr")):
            if all_components:
                bin_files = ['3rrr', '3rri', '3rir', '3rii', '3irr', '3iri',
                             '3iir', '3iii']
            else:
                bin_files = ['3rrr']
        else:
            raise IOError("No Bruker binary file could be found in %s" % (dir))

    if procs_files is None:
        procs_files = []
        for f in ["procs", "proc2s", "proc3s", "proc4s"]:
            if os.path.isfile(os.path.join(dir, f)):
                procs_files.append(f)

    # create an empty dictionary
    dic = dict()

    # read the acqus_files and add to the dictionary
    if read_procs:
        for f in procs_files:
            dic[f] = read_jcamp(os.path.join(dir, f))

    # determind shape and complexity for direct dim if needed
    if submatrix_shape is None or shape is None:
        g_shape, g_submatrix_shape = guess_shape_and_submatrix_shape(dic)
        if shape is None:
            shape = g_shape
        if submatrix_shape is None:
            submatrix_shape = g_submatrix_shape

    # issue a warning is submatrix_shape or shape are still None
    if submatrix_shape is None:
        warn('Submatrix shape not defined, returning 1D data')
    if shape is None:
        warn('Data shape not defined, returning 1D data')

    # determind endianness (assume little-endian unless BYTORDA is 1)
    if big is None:
        big = False     # default value
        if "procs" in dic and "BYTORDA" in dic["procs"]:
            if dic["procs"]["BYTORDA"] == 1:
                big = True
            else:
                big = False

    # read the binary file
    data = [read_pdata_binary(os.path.join(dir, f),
                              shape, submatrix_shape, big)[1]
            for f in bin_files]

    if len(data) == 1:
        return dic, data[0]
    else:
        return dic, data


def guess_shape_and_submatrix_shape(dic):
    """
    Guess the data shape and the shape of the processed data submatrix.
    """
    if 'procs' not in dic:  # unknow dimensionality and shapes
        return None, None

    procs = dic['procs']
    if 'SI' not in procs or 'XDIM' not in procs:
        return None, None   # cannot determine shape

    si_0 = procs['SI']
    xdim_0 = procs['XDIM']

    if 'proc2s' not in dic:  # 1D data
        return (si_0, ), (xdim_0, )

    proc2s = dic['proc2s']
    if 'SI' not in proc2s or 'XDIM' not in proc2s:
        return None, None   # cannot determine shape

    si_1 = proc2s['SI']
    xdim_1 = proc2s['XDIM']

    if 'proc3s' not in dic:  # 2D data
        return (si_1, si_0), (xdim_1, xdim_0)

    proc3s = dic['proc3s']
    if 'SI' not in proc3s or 'XDIM' not in proc3s:
        return None, None   # cannot determine shape

    si_2 = proc3s['SI']
    xdim_2 = proc3s['XDIM']

    if 'proc4s' not in dic:  # 3D data
        return (si_2, si_1, si_0), (xdim_2, xdim_1, xdim_0)

    proc4s = dic['proc4s']
    if 'SI' not in proc4s or 'XDIM' not in proc4s:
        return None, None   # cannot determine shape

    si_3 = proc4s['SI']
    xdim_3 = proc4s['XDIM']

    # assume 4D data
    return (si_3, si_2, si_1, si_0), (xdim_3, xdim_2, xdim_1, xdim_0)


def read_pdata_binary(filename, shape=None, submatrix_shape=None, big=True):
    """
    Read a processed Bruker binary file and return dic, data pair.

    If data cannot be reshaped as described a 1D representation of the data
    will be returned after printing a warning message.

    Parameters
    ----------
    filename : str
        Filename of Bruker binary file.
    shape : tuple
        Shape of resulting data.  None will return 1D data.
    submatrix_shape : tuple
        Tuple describing shape of resulting data.  None will return 1D data.
    big : bool
        Endianness of binary file, True for big-endian, False for
        little-endian.

    Returns
    -------
    dic : dict
        Dictionary containing "FILE_SIZE" key and value.
    data : ndarray
        Array of raw NMR data.

    """
    # open the file and get the data
    f = open(filename, 'rb')
    data = get_data(f, big=big)
    f.close()

    # create dictionary
    dic = {"FILE_SIZE": os.stat(filename).st_size}

    # submatrix reordering
    if submatrix_shape is None or shape is None:
        return dic, data
    else:
        try:
            data = reorder_submatrix(data, shape, submatrix_shape)
            return dic, reorder_submatrix(data, shape, submatrix_shape)
        except:
            warn('unable to reorder data')
            return dic, data


def reorder_submatrix(data, shape, submatrix_shape):
    """
    Reorder processed binary Bruker data.

    Parameters
    ----------
    data : array

    shape : tuple
        Shape of final data.
    submatrix_shape : tuple
        Shape of submatrix.

    Returns
    -------
    rdata : array
        Array in which data has been reordered and correctly shaped.

    """
    if submatrix_shape is None or shape is None:
        return data

    # do nothing to 1D data
    if len(submatrix_shape) == 1 or len(shape) == 1:
        return data

    rdata = np.empty(shape, dtype=data.dtype)
    sub_per_dim = [int(i / j) for i, j in zip(shape, submatrix_shape)]
    nsubs = np.product(sub_per_dim)
    data = data.reshape([nsubs] + list(submatrix_shape))

    for sub_num, sub_idx in enumerate(np.ndindex(tuple(sub_per_dim))):
        sub_slices = [slice(i * j, (i + 1) * j) for i, j in
                      zip(sub_idx, submatrix_shape)]
        rdata[sub_slices] = data[sub_num]
    return rdata


# Bruker binary (fid/ser) reading and writing

def read_binary(filename, shape=(1), cplex=True, big=True):
    """
    Read Bruker binary data from file and return dic,data pair

    If data cannot be reshaped as described a 1D representation of the data
    will be returned after printing a warning message.

    Parameters
    ----------
    filename : str
        Filename of Bruker binary file.
    shape : tuple
        Tuple describing shape of resulting data.
    cplex : bool
        Flag indicating if direct dimension is complex.
    big : bool
        Endianness of binary file, True for big-endian, False for
        little-endian.

    Returns
    -------
    dic : dict
        Dictionary containing "FILE_SIZE" key and value.
    data : ndarray
        Array of raw NMR data.

    See Also
    --------
    read_binary_lowmem : Read Bruker binary file using minimal memory.

    """
    # open the file and get the data
    f = open(filename, 'rb')
    data = get_data(f, big=big)

    # complexify if needed
    if cplex:
        data = complexify_data(data)

    # create dictionary
    dic = {"FILE_SIZE": os.stat(filename).st_size}

    # reshape if possible
    try:
        return dic, data.reshape(shape)

    except ValueError:
        warn(str(data.shape) + "cannot be shaped into" + str(shape))
        return dic, data


def read_binary_lowmem(filename, shape=(1), cplex=True, big=True):
    """
    Read Bruker binary data from file using minimal memory.

    Raises ValueError if shape does not agree with file size.
    See :py:func:`read_binary` for Parameters.

    Returns
    -------
    dic : dict
        Dictionary containing "FILE_SIZE" key and value.
    data : array_like
        Low memory object which can access NMR data on demand.

    See Also
    --------
    read_binary: Read Bruker binary file.

    """
    # create dictionary
    dic = {"FILE_SIZE": os.stat(filename).st_size}
    data = bruker_nd(filename, shape, cplex, big)
    return dic, data


def write_binary(filename, dic, data, overwrite=False, big=True):
    """
    Write Bruker binary data to file.

    Parameters
    ----------
    filename : str
        Filename to write to.
    dic : dict
        Dictionary of Bruker parameters.
    data : ndarray
        Array of NMR data.
    overwrite : bool
        True to overwrite files, False will raise a Warning if file exists.
    big : bool
        Endiness to write binary data with True of big-endian, False for
        little-endian.

    See Also
    --------
    write_binary_lowmem : Write Bruker binary data using minimal memory.

    """
    # open the file for writing
    f = fileiobase.open_towrite(filename, overwrite=overwrite)

    # convert objec to an array if it is not already one...
    if not isinstance(data, np.ndarray):
        data = np.array(data)

    if np.iscomplexobj(data):
        put_data(f, uncomplexify_data(data), big)
    else:
        put_data(f, data, big)
    f.close()
    return


def write_binary_lowmem(filename, dic, data, overwrite=False, big=True):
    """
    Write Bruker binary data to file using minimal memory (trace by trace).

    See :py:func:`write_binary` for Parameters.

    See Also
    --------
    write_binary : Write Bruker binary data to file.

    """
    # open the file for writing
    f = fileiobase.open_towrite(filename, overwrite=overwrite)

    cplex = np.iscomplexobj(data)

    # write out file trace by trace
    for tup in np.ndindex(data.shape[:-1]):
        trace = data[tup]
        if cplex:
            put_data(f, uncomplexify_data(trace), big)
        else:
            put_data(f, trace, big)
    f.close()
    return


# lowmemory ND object

class bruker_nd(fileiobase.data_nd):
    """
    Emulate a ndarray objects without loading data into memory for low memory
    reading of Bruker fid/ser files.

    * slicing operations return ndarray objects.
    * can iterate over with expected results.
    * transpose and swapaxes methods create a new objects with correct axes
      ordering.
    * has ndim, shape, and dtype attributes.

    Parameters
    ----------

    filename : str
        Filename of Bruker binary file.
    fshape : tuple
        Shape of NMR data.
    cplex : bool
        Flag indicating if direct dimension is complex.
    big : bool
        Endianess of data.  True for big-endian, False for little-endian.
    order : tuple
        Ordering of axis against file.

    """

    def __init__(self, filename, fshape, cplex, big, order=None):
        """
        Create and set up object.
        """

        # check that size is correct
        pts = reduce(lambda x, y: x * y, fshape)
        if cplex:
            if os.stat(filename).st_size != pts * 4 * 2:
                raise ValueError("shape does not agree with file size")
        else:
            if os.stat(filename).st_size != pts * 4:
                raise ValueError("shape does not agree with file size")

        # check order
        if order is None:
            order = range(len(fshape))

        # finalize
        self.filename = filename
        self.fshape = fshape
        self.cplex = cplex
        self.big = big
        self.order = order

        if self.cplex:
            self.dtype = np.dtype("complex128")
        else:
            self.dtype = np.dtype("int32")

        self.__setdimandshape__()   # set ndim and shape attributes

    def __fcopy__(self, order):
        """
        Create a copy
        """
        n = bruker_nd(self.filename, self.fshape, self.cplex, self.big, order)
        return n

    def __fgetitem__(self, slices):
        """
        return ndarray of selected values

        slices is a well formatted tuple of slices
        """
        # seperate the last slice from the first slices
        lslice = slices[-1]
        fslice = slices[:-1]

        # and the same for fshape
        lfshape = self.fshape[-1]
        ffshape = self.fshape[:-1]

        # find the output size and make a in/out nd interator
        osize, nd_iter = fileiobase.size_and_ndtofrom_iter(ffshape, fslice)
        osize.append(len(range(lfshape)[lslice]))

        # create an empty array to store the selected slices
        out = np.empty(tuple(osize), dtype=self.dtype)

        f = open(self.filename, 'rb')

        # read in the data trace by trace
        for out_index, in_index in nd_iter:

            # determine the trace number from the index
            ntrace = fileiobase.index2trace_flat(ffshape, in_index)

            # seek to the correct place in the file
            if self.cplex:
                ts = ntrace * lfshape * 2 * 4
                f.seek(ts)
                trace = get_trace(f, lfshape * 2, self.big)
                trace = complexify_data(trace)
            else:
                ts = ntrace * lfshape * 2
                f.seek(ts)
                trace = get_trace(f, lfshape, self.big)

            # save to output
            out[out_index] = trace[lslice]

        return out

# binary get/put functions


def get_data(f, big):
    """
    Get binary data from file object with given endiness
    """
    if big:
        return np.frombuffer(f.read(), dtype='>i4')
    else:
        return np.frombuffer(f.read(), dtype='<i4')


def put_data(f, data, big=True):
    """
    Put data to file object with given endiness
    """
    if big:
        f.write(data.astype('>i4').tostring())
    else:
        f.write(data.astype('<i4').tostring())
    return


def get_trace(f, num_points, big):
    """
    Get trace of num_points from file with given endiness
    """
    if big:
        bsize = num_points * np.dtype('>i4').itemsize
        return np.frombuffer(f.read(bsize), dtype='>i4')
    else:
        bsize = num_points * np.dtype('<i4').itemsize
        return np.frombuffer(f.read(bsize), dtype='<i4')


# data manipulation functions


def complexify_data(data):
    """
    Complexify data packed real, imag.
    """
    return data[..., ::2] + data[..., 1::2] * 1.j


def uncomplexify_data(data_in):
    """
    Uncomplexify data (pack real,imag) into a int32 array
    """
    size = list(data_in.shape)
    size[-1] = size[-1] * 2
    data_out = np.empty(size, dtype="int32")
    data_out[..., ::2] = data_in.real
    data_out[..., 1::2] = data_in.imag
    return data_out


# digital filter functions

# Table of points to frequency shift Bruker data to remove digital filter
# (Phase is 360 degrees * num_pts)
# This table is an 'un-rounded' version base on the table by
# W.M. Westler and F. Abildgaard's offline processing note, online at:
# http://www.boc.chem.uu.nl/static/local/prospectnd/dmx_digital_filters.html
# and the updated table with additional entries at:
# http://sbtools.uchc.edu/help/nmr/nmr_toolkit/bruker_dsp_table.asp

# The rounding in the above tables appear to be based on k / (2*DECIM)
# for example 2 : 44.75   = 44 + 3/4
#             4 : 66.625  = 66 + 5/8
#             8 : 68.563 ~= 68 + 9/16 = 68.5625
# Using this the un-rounded table was created by checking possible unrounded
# fracions which would round to those in the original table.

bruker_dsp_table = {
    10: {
        2    : 44.75,
        3    : 33.5,
        4    : 66.625,
        6    : 59.083333333333333,
        8    : 68.5625,
        12   : 60.375,
        16   : 69.53125,
        24   : 61.020833333333333,
        32   : 70.015625,
        48   : 61.34375,
        64   : 70.2578125,
        96   : 61.505208333333333,
        128  : 70.37890625,
        192  : 61.5859375,
        256  : 70.439453125,
        384  : 61.626302083333333,
        512  : 70.4697265625,
        768  : 61.646484375,
        1024 : 70.48486328125,
        1536 : 61.656575520833333,
        2048 : 70.492431640625,
    },
    11: {
        2    : 46.,
        3    : 36.5,
        4    : 48.,
        6    : 50.166666666666667,
        8    : 53.25,
        12   : 69.5,
        16   : 72.25,
        24   : 70.166666666666667,
        32   : 72.75,
        48   : 70.5,
        64   : 73.,
        96   : 70.666666666666667,
        128  : 72.5,
        192  : 71.333333333333333,
        256  : 72.25,
        384  : 71.666666666666667,
        512  : 72.125,
        768  : 71.833333333333333,
        1024 : 72.0625,
        1536 : 71.916666666666667,
        2048 : 72.03125
    },
    12: {
        2    : 46.,
        3    : 36.5,
        4    : 48.,
        6    : 50.166666666666667,
        8    : 53.25,
        12   : 69.5,
        16   : 71.625,
        24   : 70.166666666666667,
        32   : 72.125,
        48   : 70.5,
        64   : 72.375,
        96   : 70.666666666666667,
        128  : 72.5,
        192  : 71.333333333333333,
        256  : 72.25,
        384  : 71.666666666666667,
        512  : 72.125,
        768  : 71.833333333333333,
        1024 : 72.0625,
        1536 : 71.916666666666667,
        2048 : 72.03125
    },
    13: {
        2    : 2.75,
        3    : 2.8333333333333333,
        4    : 2.875,
        6    : 2.9166666666666667,
        8    : 2.9375,
        12   : 2.9583333333333333,
        16   : 2.96875,
        24   : 2.9791666666666667,
        32   : 2.984375,
        48   : 2.9895833333333333,
        64   : 2.9921875,
        96   : 2.9947916666666667
    }
}


def remove_digital_filter(dic, data):
    """
    Remove the digital filter from Bruker data.

    Parameters
    ----------
    dic : dict
        Dictionary of Bruker parameters.
    data : ndarray
        Array of NMR data to remove digital filter from.

    Returns
    -------
    ndata : ndarray
        Array of NMR data with digital filter removed

    See Also
    ---------
    rm_dig_filter : Remove digital filter by specifying parameters.

    """
    if 'acqus' not in dic:
        raise ValueError("dictionary does not contain acqus parameters")

    if 'DECIM' not in dic['acqus']:
        raise ValueError("dictionary does not contain DECIM parameter")
    decim = dic['acqus']['DECIM']

    if 'DSPFVS' not in dic['acqus']:
        raise ValueError("dictionary does not contain DSPFVS parameter")
    dspfvs = dic['acqus']['DSPFVS']

    if 'GRPDLY' not in dic['acqus']:
        grpdly = 0
    else:
        grpdly = dic['acqus']['GRPDLY']

    return rm_dig_filter(data, decim, dspfvs, grpdly)


def rm_dig_filter(data, decim, dspfvs, grpdly=0):
    """
    Remove the digital filter from Bruker data.

    Parameters
    ----------
    data : ndarray
        Array of NMR data to remove digital filter from.
    decim : int
        Decimation rate (Bruker DECIM parameter).
    dspfvs : int
        Firmware version (Bruker DSPFVS parameter).
    grpdly : float, optional
        Group delay. (Bruker GRPDLY parameter). When non-zero decom and
        dspfvs are ignored.

    Returns
    -------
    ndata : ndarray
        Array of NMR data with digital filter removed.

    See Also
    --------
    remove_digital_filter : Remove digital filter using Bruker dictionary.

    """
    # This algorithm gives results similar but not exactly the same
    # as NMRPipe.  It was worked out by examining sample FID converted using
    # NMRPipe against spectra shifted with nmrglue's processing functions.
    # When a frequency shifting with a fft first (fft->first order phase->ifft)
    # the middle of the fid nearly matches NMRPipe's and the difference at the
    # beginning is simply the end of the spectra reversed.  A few points at
    # the end of the spectra are skipped entirely.
    # -jjh 2010.12.01

    # The algorithm is as follows:
    # 1. FFT the data
    # 2. Apply a negative first order phase to the data.  The phase is
    #    determined by the GRPDLY parameter or found in the DSPFVS/DECIM
    #    loopup table.
    # 3. Inverse FFT
    # (these first three steps are a frequency shift with a FFT first, fsh2)
    # 4. Round the applied first order phase up by two integers. For example
    #    71.4 -> 73, 67.8 -> 69, and 48 -> 50, this is the number of points
    #    removed from the end of the fid.
    # 5. If the size of the removed portion is greater than 6, remove the first
    #    6 points, reverse the remaining points, and add then to the beginning
    #    of the spectra.  If less that 6 points were removed, leave the FID
    #    alone.
    if grpdly > 0:  # use group delay value if provided (not 0 or -1)
        phase = grpdly

    # determind the phase correction
    else:
        if dspfvs >= 14:    # DSPFVS greater than 14 give no phase correction.
            phase = 0.
        else:   # loop up the phase in the table
            if dspfvs not in bruker_dsp_table:
                raise ValueError("dspfvs not in lookup table")
            if decim not in bruker_dsp_table[dspfvs]:
                raise ValueError("decim not in lookup table")
            phase = bruker_dsp_table[dspfvs][decim]

    # and the number of points to remove (skip) and add to the beginning
    skip = int(np.floor(phase + 2.))    # round up two integers
    add = int(max(skip - 6, 0))           # 6 less, or 0

    # DEBUG
    # print("phase: %f, skip: %i add: %i"%(phase,skip,add))

    # frequency shift
    pdata = proc_base.fsh2(data, phase)

    # add points at the end of the specta to beginning
    pdata[..., :add] = pdata[..., :add] + pdata[..., :-(add + 1):-1]
    # remove points at end of spectra
    return pdata[..., :-skip]


# JCAMP-DX functions

def read_jcamp(filename):
    """
    Read a Bruker JCAMP-DX file into a dictionary.

    Creates two special dictionary keys _coreheader and _comments Bruker
    parameter "$FOO" are extracted into strings, floats or lists and assigned
    to dic["FOO"]

    Parameters
    ----------
    filename : str
        Filename of Bruker JCAMP-DX file.

    Returns
    -------
    dic : dict
        Dictionary of parameters in file.

    See Also
    --------
    write_jcamp : Write a Bruker JCAMP-DX file.

    Notes
    -----
    This is not a fully functional JCAMP-DX reader, it is only intended
    to read Bruker acqus (and similar) files.

    """
    dic = {"_coreheader": [], "_comments": []}  # create empty dictionary
    f = open(filename, 'r')

    while True:     # loop until end of file is found

        line = f.readline().rstrip()    # read a line
        if line == '':      # end of file found
            break

        if line[:6] == "##END=":
            # print("End of file")
            break
        elif line[:2] == "$$":
            dic["_comments"].append(line)
        elif line[:2] == "##" and line[2] != "$":
            dic["_coreheader"].append(line)
        elif line[:3] == "##$":
            try:
                key, value = parse_jcamp_line(line, f)
                dic[key] = value
            except:
                warn("Unable to correctly parse line:" + line)
        else:
            warn("Extraneous line:" + line)

    return dic


def parse_jcamp_line(line, f):
    """
    Parse a single JCAMP-DX line

    Extract the Bruker parameter name and value from a line from a JCAMP-DX
    file.  This may entail reading additional lines from the fileobj f if the
    parameter value extends over multiple lines.

    """

    # extract key= text from line
    key = line[3:line.index("=")]
    text = line[line.index("=") + 1:].lstrip()

    if "<" in text:   # string
        while ">" not in text:      # grab additional text until ">" in string
            text = text + "\n" + f.readline().rstrip()
        value = text[1:-1]  # remove < and >

    elif "(" in text:   # array
        num = int(line[line.index("..") + 2:line.index(")")]) + 1
        value = []
        rline = line[line.index(")") + 1:]

        # extract value from remainer of line
        for t in rline.split():
            value.append(parse_jcamp_value(t))

        # parse additional lines as necessary
        while len(value) < num:
            nline = f.readline().rstrip()
            for t in nline.split():
                value.append(parse_jcamp_value(t))

    elif text == "yes":
        value = True

    elif text == "no":
        value = False

    else:   # simple value
        value = parse_jcamp_value(text)

    return key, value


def parse_jcamp_value(text):
    """
    Parse value text from Bruker JCAMP-DX file returning the value.
    """
    if "<" in text:
        return text[1:-1]  # remove < and >
    elif "." in text or "e" in text or 'inf' in text:
        return float(text)
    else:
        return int(text)


def write_jcamp(dic, filename, overwrite=False):
    """
    Write a Bruker JCAMP-DX file from a dictionary

    Written file will differ slightly from Bruker's JCAMP-DX files in that all
    multi-value parameters will be written on multiple lines. Bruker is
    inconsistent on what is written to a single line and what is not.
    In addition line breaks may be slightly different but will always be
    within JCAMP-DX specification.  Finally long floating point values
    may loose precision when writing.

    For example:

        ##$QS= (0..7)83 83 83 83 83 83 83 22

        will be written as

        ##$QS= (0..7)
        83 83 83 83 83 83 83 22

    Parameters
    ----------
    dic : dict
        Dictionary of parameters to write
    filename : str
        Filename of JCAMP-DX file to write
    overwrite : bool, optional
        True to overwrite an existing file, False will raise a Warning if the
        file already exists.

    See Also
    --------
    read_jcamp : Read a Bruker JCAMP-DX file.

    """

    # open the file for writing
    f = fileiobase.open_towrite(filename, overwrite=overwrite, mode='w')

    # create a copy of the dictionary
    d = dict(dic)

    # remove the comments and core header key from dictionary
    comments = d.pop("_comments")
    corehdr = d.pop("_coreheader")

    # write out the core headers
    for line in corehdr:
        f.write(line)
        f.write("\n")

    # write out the comments
    for line in comments:
        f.write(line)
        f.write("\n")

    keys = sorted([i for i in d.keys()])

    # write out each key,value pair
    for key in keys:
        write_jcamp_pair(f, key, d[key])

    # write ##END= and close the file
    f.write("##END=")
    f.close()


def write_jcamp_pair(f, key, value):
    """
    Write out a line of a JCAMP file.

    a line might actually be more than one line of text for arrays.
    """

    # the parameter name and such
    line = "##$" + key + "= "

    # need to be type not isinstance since isinstance(bool, int) == True
    if type(value) == float or type(value) == int:  # simple numbers
        line = line + repr(value)

    elif isinstance(value, str):    # string
        line = line + "<" + value + ">"

    elif type(value) == bool:   # yes or no
        if value:
            line = line + "yes"
        else:
            line = line + "no"

    elif isinstance(value, list):
        # write out the current line
        line = line + "(0.." + repr(len(value) - 1) + ")"
        f.write(line)
        f.write("\n")
        line = ""

        # loop over elements in value printing out lines when
        # they reach > 70 characters or the next value would cause
        # the line to go over 80 characters
        for v in value:
            if len(line) > 70:
                f.write(line)
                f.write("\n")
                line = ""

            if isinstance(v, str):
                to_add = "<" + v + ">"
            else:
                to_add = repr(v)

            if len(line + " " + to_add) > 80:
                f.write(line)
                f.write("\n")
                line = ""

            if line != "":
                line = line + to_add + " "
            else:
                line = to_add + " "

    # write out the line and a newline character
    f.write(line)
    f.write("\n")

    return


# pulse program read/writing functions

def read_pprog(filename):
    """
    Read a Bruker pulse program (pulseprogram) file.

    Resultsing dictionary contains the following keys:

    ========    ===========================================================
    key         description
    ========    ===========================================================
    var         dictionary of variables assigned in pulseprogram
    incr        list of lists containing increment times
    loop        list of loop multipliers
    phase       list of lists containing phase elements
    ph_extra    list of lists containing comments at the end of phase lines
    ========    ===========================================================

    The incr,phase and ph_extra lists match up with loop list.  For example
    incr[0],phase[0] and ph_extra[0] are all increment and phase commands
    with comments which occur during loop 0 which has loop[0] steps.

    Parameters
    ----------
    filename : str
        Filename of pulseprogram file to read from,

    Returns
    -------
    dic : dict
        A dictionary with keys described above.

    See Also
    --------
    write_pprog : Write a Bruker pulse program to file.

    """

    # open the file
    f = open(filename, 'r')

    # initilize lists and dictionaries
    var = dict()
    loop = []
    incr = [[]]
    phase = [[]]
    ph_extra = [[]]

    # loop over lines in pulseprogram looking for loops, increment,
    # assigments and phase commands
    for line in f:

        # split line into comment and text and strip leading/trailing spaces
        if ";" in line:
            comment = line[line.index(";"):]
            text = line[:line.index(";")].strip()
        else:
            comment = ""
            text = line.strip()

        # remove label from text when first word is all digits or
        # has "," as the last element
        if len(text.split()) != 0:
            s = text.split()[0]
            if s.isdigit() or s[-1] == ",":
                text = text[len(s):].strip()

        # skip blank lines and include lines
        if text == "" or text[0] == "#":
            # print(line,"--Blank, Comment or Include")
            continue

        # see if we have quotes and have an assigment
        # syntax "foo=bar"
        # add foo:bar to var dictionary
        if "\"" in text:
            if "=" in line:
                # strip quotes, split on = and add to var dictionary
                text = text.strip("\"")
                t = text.split("=")
                if len(t) >= 2:
                    key, value = t[0], t[1]
                    var[key] = value
                    # print(line,"--Assignment")
                else:
                    pass
                    # print(line,"--Statement")
                continue
            else:
                # print(line,"--Statement")
                continue

        # loops begin with lo
        # syntax is: lo to N time M
        # add M to loop list
        if text[0:2] == "lo":
            loop.append(text.split()[4])
            incr.append([])
            phase.append([])
            ph_extra.append([])
            # print(line,"--Loop")
            continue

        tokens = text.split()
        if len(tokens) >= 2:
            token2 = tokens[1]
            # increment statement have id, dd, ipu or dpu
            # syntax foo {id/dd/ipu/dpu}N
            # store N to incr list
            if token2.startswith('id') or token2.startswith('dd'):
                incr[len(loop)].append(int(token2[2:]))
                # print(line,"--Increment")
                continue

            if token2.startswith("ipu") or token2.startswith("dpu"):
                incr[len(loop)].append(int(token2[3:]))
                # print(line,"--Increment")
                continue

            # phase statement have ip or dp
            # syntax fpp {ip/dp}N extra
            # store N to phase list and extra to ph_extra list
            if token2.startswith("ip") or token2.startswith("dp"):
                phase[len(loop)].append(int(token2[2:]))

                # find the first space after "ip" and read past there
                last = text.find(" ", text.index("ip"))
                if last == -1:
                    ph_extra[len(loop)].append("")
                else:
                    ph_extra[len(loop)].append(text[last:].strip())
                # print(line,"--Phase")
                continue

            # print(line,"--Unimportant")

    f.close()

    # remove the last empty incr, phase and ph_extra lists
    incr.pop()
    phase.pop()
    ph_extra.pop()

    # convert loop to numbers if possible
    for i, t in enumerate(loop):
        if t.isdigit():
            loop[i] = int(t)
        else:
            if (t in var) and var[t].isdigit():
                loop[i] = int(var[t])

    # create the output dictionary
    dic = {"var": var, "incr": incr, "loop": loop, "phase": phase,
           "ph_extra": ph_extra}

    return dic


def write_pprog(filename, dic, overwrite=False):
    """
    Write a minimal Bruker pulse program to file.

    **DO NOT TRY TO RUN THE RESULTING PULSE PROGRAM**

    This pulse program should return the same dictionary when read using
    read_pprog, nothing else.  The pulse program will be nonsense.

    Parameters
    ----------
    filename : str
        Filename of file to write pulse program to.
    dic : dict
        Dictionary of pulse program parameters.
    overwrite : bool, optional
        True to overwrite an existing file, False will raise a Warning if the
        file already exists.

    See Also
    --------
    read_pprog : Read a Bruker pulse program.

    """

    # open the file for writing
    f = fileiobase.open_towrite(filename, overwrite=overwrite, mode='w')

    # write a comment
    f.write("; Minimal Bruker pulseprogram created by write_pprog\n")

    # write our the variables
    for k, v in dic["var"].items():
        f.write("\"" + k + "=" + v + "\"\n")

    # write out each loop
    for i, steps in enumerate(dic["loop"]):

        # write our the increments
        for v in dic["incr"][i]:
            f.write("d01 id" + str(v) + "\n")

        # write out the phases
        for v, w in zip(dic["phase"][i], dic["ph_extra"][i]):
            f.write("d01 ip" + str(v) + " " + str(w) + "\n")

        f.write("lo to 0 times " + str(steps) + "\n")

    # close the file
    f.close()

    return
