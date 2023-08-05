"""

=========================
PDB file input and output
=========================
Reading and writing files from the PDB file format.


PDB files
---------
The PDB file format is sometimes used for reading and writing information about
tractography results. The *nominal* PDB file format specification is as
follows, but note that some of these things are not implemented in PDB version
3. For example, there are no algorithms to speak of, so that whole bit is
completely ignored.

 The file-format is organized as a semi-hierarchical data-base, according to
    the following specification:
    [ header size] - int
    -- HEADER FOLLOWS --
    [4x4 xform matrix ] - 16 doubles
    [ number of pathway statistics ] - int
    for each statistic:
        [ currently unused ] - bool
        [ is stat stored per point, or aggregate per path? ] - bool
        [ currently unused ] - bool
        [ name of the statistic ] - char[255]
        [ currently unused ] - char[255]
        [ unique ID - unique identifier for this stat across files ] - int

    ** The algorithms bit is not really working as advertised: **
    [ number of algorithms ] - int
    for each algorithm:
       [ algorithm name ] - char[255]
       [ comments about the algorithm ] - char[255]
       [ unique ID -  unique identifier for this algorithm, across files ] - int

    [ version number ] - int
    -- HEADER ENDS --
    [ number of pathways ] - int
    [ pts per fiber ] - number of pathways integers
    for each pathway:
       [ header size ] - int
       -- PATHWAY HEADER FOLLOWS --
        ** The following are not actually encoded in the fiber header and are
         currently set in an arbitrary fashion: **
       [ number of points ] - int
       [ algorithm ID ] - int
       [ seed point index ] - int

       for each statistic:
          [ precomputed statistical value ] - double
       -- PATHWAY HEADER ENDS --
       for each point:
            [ position of the point ] - 3 doubles (ALREADY TRANSFORMED from
                                                   voxel space!)
          for each statistic:
             IF computed per point (see statistics header, second bool field):
             for each point:
               [ statistical value for this point ] - double


"""
# Import from standard lib:
import struct
import os
import warnings

import numpy as np

import nibabel as nib
import nibabel.trackvis as tv


# This one's a global used in both packing and unpacking the data
_fmt_dict = {'int':['=i', 4],
             'double':['=d', 8],
             'char':['=c', 1],
             'bool':['=?', 1],
             #'uint':['=I', 4],
                }

def _unpacker(file_read, idx, obj_to_read, fmt='int'):

    """
    Helper function to unpack binary data from files with the struct library.

    Relies on http://docs.python.org/library/struct.html

    Parameters
    ----------
    file_read: The output of file.read() from a file object
    idx: An index into x
    obj_to_read: How many objects to read
    fmt: A format string, telling us what to read from there
    """
    # For each one, this is [fmt_string, size]

    fmt_str = _fmt_dict[fmt][0]
    fmt_sz = _fmt_dict[fmt][1]

    out = np.array([struct.unpack(fmt_str,
                    file_read[idx + fmt_sz * j:idx + fmt_sz + fmt_sz * j])[0]
        for j in range(obj_to_read)])

    idx += obj_to_read * fmt_sz
    return out, idx


def _packer(file_write, vals, fmt='int'):
    """
    Helper function to pack binary data to files, using the struct library:

    Relies on http://docs.python.org/library/struct.html

    """
    fmt_str = _fmt_dict[fmt][0]
    if np.iterable(vals):
        for pack_this in vals:
            s = struct.pack(fmt_str, pack_this)
            file_write.write(s)

    else:
        s = struct.pack(fmt_str, vals)
        file_write.write(s)


def _word_maker(arr):
    """
    Helper function Make a string out of pdb stats header "name" variables
    """
    make_a_word = []
    for this in arr:
        if this: # The sign that you reached the end of the word is an empty
                 # char
            make_a_word.append(this)
        else:
            break
    return ''.join(make_a_word)


def _char_list_maker(name):
    """
    Helper function that does essentially the opposite of _word_maker. Takes a
    string and makes it into a 255 long list of characters with the name of a
    stat, followed by a single white-space and then 'g' for the rest of the 255
    """

    l = list(name)
    l.append('\x00')  # The null character
    while len(l)<255:
        l.append('g')
    return l
    
def read(file_name):
    """
    Read the definition of a fiber-group from a .pdb file

    Parameters
    ----------
    file_name: str
       Full path to the .pdb file
    Returns
    -------
    dict 

    Note
    ----
    This only reads Version 3 PDB files.
    """
    hdr = {}
    # Read the file as binary info:
    f_obj = file(file_name, 'r')
    f_read = f_obj.read()
    f_obj.close()
    # This is an updatable index into this read:
    idx = 0

    # First part is an int encoding the offset to the fiber part:
    offset, idx = _unpacker(f_read, idx, 1)

    # Next bit are doubles, encoding the xform (4 by 4 = 16 of them):
    xform, idx  = _unpacker(f_read, idx, 16, 'double')
    xform = np.reshape(xform, (4, 4))
    hdr['affine'] = xform

    # Next is an int encoding the number of stats:
    numstats, idx = _unpacker(f_read, idx, 1)
    hdr['n_stats'] = numstats
    # The stats header is a dict with lists holding the stat per
    stats_header = dict(luminance_encoding=[],  # int => bool
                        computed_per_point=[],  # int => bool
                        viewable=[],  # int => bool
                        agg_name=[],  # char array => string
                        local_name=[],  # char array => string
                        uid=[]  # int
        )

    # Read the stats header:
    counter = 0
    while counter < numstats:
        counter += 1
        for k in ["luminance_encoding",
                  "computed_per_point",
                  "viewable"]:
            this, idx = _unpacker(f_read, idx, 1)
            stats_header[k].append(np.bool(this))

        for k in ["agg_name", "local_name"]:
            this, idx = _unpacker(f_read, idx, 255, 'char')
            stats_header[k].append(_word_maker(this))
        # Must have integer reads be word aligned (?):
        idx += 2
        this, idx = _unpacker(f_read, idx, 1)
        stats_header["uid"].append(this)

    hdr['stats'] = stats_header

    # We skip the whole bit with the algorithms and go straight to the version
    # number, which is one int length before the fibers:
    idx = offset - 4
    version, idx = _unpacker(f_read, idx, 1)
    hdr['version'] = version

    if int(version) < 2:
        raise ValueError("Can only read PDB version 2 or version 3 files")

    if int(version) == 2:
        idx = offset

    # How many fibers?
    numpaths, idx = _unpacker(f_read, idx, 1)
    hdr['n_paths'] = numpaths

    fibers=[]
    fiber_stats=[]
    node_stats=[]
    
    if int(version) == 2:
        pts = []
        f_stats = []
        n_stats = []
        for p_idx in range(numpaths):
            f_stats_dict = {}
            n_stats_dict = {}

            # Keep track of where you are right now
            ppos = idx
            path_offset, idx = _unpacker(f_read, idx, 1)
            n_nodes, idx = _unpacker(f_read, idx, 1)
            # As far as I can tell the following two don't matter much:
            algo_type, idx = _unpacker(f_read, idx, 1)
            seed_pt_idx, idx = _unpacker(f_read, idx, 1)
            # Read out the per-path stats:
            for stat_idx in range(numstats):
                per_fiber_stat, idx = _unpacker(f_read, idx, 1, 'double')
                f_stats_dict[stats_header["local_name"][stat_idx]] = \
                    per_fiber_stat
            f_stats.append(f_stats_dict)
            # Skip forward to where the paths themselves are:
            idx = ppos
            # Read the nodes:
            pathways, idx = _unpacker(f_read, idx, n_nodes*3, 'double')

            pts.append(np.reshape(pathways, (n_nodes, 3)))
            for stat_idx in range(numstats):
                if stats_header["computed_per_point"][stat_idx]:
                    name = stats_header["local_name"][stat_idx]
                    n_stats_dict[name], idx = _unpacker(f_read, idx, n_nodes,
                                                    'double')

            n_stats.append(n_stats_dict)

        # Initialize all the fibers:
        for p_idx in range(numpaths):
            this_fstats_dict = f_stats[p_idx]
            f_stat_k = this_fstats_dict.keys()
            f_stat_v = [this_fstats_dict[k] for k in f_stat_k]
            this_nstats_dict = n_stats[p_idx]
            n_stats_k = this_nstats_dict.keys()
            n_stats_v = [this_nstats_dict[k] for k in n_stats_k]
            fibers.append(pts[p_idx]),
            fiber_stats.append(dict(zip(f_stat_k, f_stat_v)))
            node_stats.append(dict(zip(n_stats_k, n_stats_v)))


    elif int(version) == 3:
        # The next few bytes encode the number of points in each fiber:
        pts_per_fiber, idx = _unpacker(f_read, idx, numpaths)
        total_pts = np.sum(pts_per_fiber)
        # Next we have the xyz coords of the nodes in all fibers:
        fiber_pts, idx = _unpacker(f_read, idx, total_pts * 3, 'double')

        # We extract the information on a fiber-by-fiber basis
        pts_read = 0
        pts = []
        for p_idx in range(numpaths):
            n_nodes = pts_per_fiber[p_idx]
            pts.append(np.reshape(
                       fiber_pts[pts_read * 3:(pts_read + n_nodes) * 3],
                       (n_nodes, 3)))
            pts_read += n_nodes

        f_stats_dict = {}
        for stat_idx in range(numstats):
            per_fiber_stat, idx = _unpacker(f_read, idx, numpaths, 'double')
            # This is a fiber-stat only if it's not computed per point:
            if not stats_header["computed_per_point"][stat_idx]:
                f_stats_dict[stats_header["local_name"][stat_idx]] =\
                    per_fiber_stat

        per_point_stat = []
        n_stats_dict = {}
        for stat_idx in range(numstats):
            pts_read = 0
            # If it is computed per point, it's a node-stat:
            if stats_header["computed_per_point"][stat_idx]:
                name = stats_header["local_name"][stat_idx]
                n_stats_dict[name] = []
                per_point_stat, idx = _unpacker(f_read, idx, total_pts, 'double')
                for p_idx in range(numpaths):
                    n_stats_dict[name].append(
                        per_point_stat[pts_read:pts_read + pts_per_fiber[p_idx]])

                    pts_read += pts_per_fiber[p_idx]
            else:
                per_point_stat.append([])

        # Initialize all the fibers:
        for p_idx in range(numpaths):
            f_stat_k = f_stats_dict.keys()
            f_stat_v = [f_stats_dict[k][p_idx] for k in f_stat_k]
            n_stats_k = n_stats_dict.keys()
            n_stats_v = [n_stats_dict[k][p_idx] for k in n_stats_k]
            fibers.append(pts[p_idx]),
            fiber_stats.append(dict(zip(f_stat_k, f_stat_v)))
            node_stats.append(dict(zip(n_stats_k, n_stats_v)))
    
    return fibers, hdr, fiber_stats, node_stats


def write(fibers, hdr, fiber_stats, node_stats, file_name):
    """
    Write a pdb file.

    Parameters
    ----------
    fibers : list
         Streamlines, as (N, 3) arrays

    hdr : dict

    fiber_stats : list

    node_stats : list 

    file_name: str
       Full path to the pdb file to be saved.

    Notes
    -----
    Files are written as version 3 
    """

    fwrite = file(file_name, 'w')
    
    n_stats = hdr['n_stats']
    stats_hdr_sz = (4 * _fmt_dict['int'][1] + 2 * _fmt_dict['char'][1] * 255 + 2)

    # This is the 'offset' to the beginning of the fiber-data. Note that we are
    # just skipping the whole algorithms thing, since that seems to be unused
    # in the mrDiffusion implementation of this file-format, from this was
    # adpated: 
    hdr_sz = (4 * _fmt_dict['int'][1] + # ints: hdr_sz itself, n_stats, n_algs
                                        # (always 0), version
             16 *_fmt_dict['double'][1] +      # doubles: the 4 by 4 affine
             n_stats * stats_hdr_sz) # The stats part of the header, add
                                        # one for good measure(?).


    _packer(fwrite, hdr_sz)
    if hdr['affine'] is None:
            affine = tuple(np.eye(4).ravel().squeeze())
    else:
        affine = tuple(np.array(hdr['affine']).ravel().squeeze())

    _packer(fwrite, affine, 'double')
    _packer(fwrite, n_stats)

    for uid in range(hdr['n_stats']):
        _packer(fwrite, int(hdr['stats']['luminance_encoding'][uid]))  
        _packer(fwrite, int(hdr['stats']['computed_per_point'][uid])) 
        _packer(fwrite, int(hdr['stats']['viewable'][uid]))
        char_list = _char_list_maker(hdr['stats']['agg_name'][uid])
        _packer(fwrite, char_list, 'char')
        char_list = _char_list_maker(hdr['stats']['local_name'][uid])
        _packer(fwrite, char_list, 'char')
        _packer(fwrite, ['g','g'], 'char')  # Add this, so that that the uid ends
                                            # up "word-aligned".
        _packer(fwrite, uid)

    _packer(fwrite, 0) # Number of algorithms - set to 0 always

    fwrite.seek(hdr_sz - _fmt_dict['int'][1])

    # This is the PDB file version:
    _packer(fwrite, 3)
    _packer(fwrite, hdr['n_paths'])

    for fib in fibers:
        # How many coords in each fiber:
        _packer(fwrite, fib.shape[0])
    
    # x,y,z coords in each fiber:
    for fib in fibers:
        _packer(fwrite, fib.ravel(), 'double')
    
    for stat_idx in range(hdr['n_stats']):
        if not hdr['stats']['computed_per_point'][stat_idx]:
            for f in fiber_stats:
                _packer(fwrite, f[hdr['stats']['local_name'][stat_idx]], 'double')
        else: 
            for f in fiber_stats:
                _packer(fwrite, 0, 'double')

    for stat_idx in range(hdr['n_stats']):
        if hdr['stats']['computed_per_point'][stat_idx]:
            for f in node_stats:
                _packer(fwrite, f[hdr['stats']['local_name'][stat_idx]], 'double')

    fwrite.close()

def empty_hdr():
    """
    
    """
    return {'affine': np.eye(4),
            'n_paths': np.array([0]),
            'n_stats': np.array([0]),
            'stats': {'agg_name': [],
                      'computed_per_point': [],
                      'local_name': [],
                      'luminance_encoding': [],
                      'uid': [],
                      'viewable': []},
            'version': np.array([3])}

def trk2pdb(trk_file, pdb_file, affine=None):
    trk_fibs, trk_hdr = nib.trackvis.read(trk_file)
    pdb_hdr = empty_hdr()
    if affine is None:
        try:
            pdb_hdr['affine'] = nib.trackvis.aff_from_hdr(trk_hdr)
        except:
            pdb_hdr['affine'] = np.eye(4)

    else:
        pdb_hdr['affine'] = affine
        
    pdb_hdr['n_paths'] = trk_hdr['n_count']
    fibers = [f[0] for f in trk_fibs]
    fiber_stats = []
    node_stats = []
    write(fibers, pdb_hdr, fiber_stats, node_stats, pdb_file)
    

def pdb2trk(pdb_file, trk_file, affine=None):
    pdb_fibs, pdb_hdr, fiber_stats, node_stats = read(pdb_file)
    trk_hdr = nib.trackvis.empty_header()
    if affine is None:
        try:
            nib.trackvis.aff_to_hdr(pdb_hdr['affine'], trk_hdr)
        except np.linalg.LinAlgError:
            nib.trackvis.aff_to_hdr(np.eye(4), trk_hdr)
    else:
        nib.trackvis.aff_to_hdr(affine, trk_hdr)
        
    trk_fibs = []
    for ff in pdb_fibs:
        trk_fibs.append((ff, None, None))

    nib.trackvis.write(trk_file, trk_fibs, trk_hdr)
