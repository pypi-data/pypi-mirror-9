#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Command line tool to print the structure of an HDF5 file'''

__url__ = 'http://spec2nexus.readthedocs.org/en/latest/h5toText.html'

import os       #@UnusedImport
import sys      #@UnusedImport
import h5py
import numpy
import spec2nexus


class H5toText(object):
    '''
    Example usage showing default display::
    
        mc = H5toText(filename)
        mc.array_items_shown = 5
        show_attributes = False
        txt = mc.report(show_attributes)
    '''
    requested_filename = None
    isNeXus = False
    array_items_shown = 5

    def __init__(self, filename):
        '''store filename and test if file is NeXus HDF5'''
        self.requested_filename = filename
        self.filename = None
        self.show_attributes = True
        if os.path.exists(filename):
            self.filename = filename
            self.isNeXus = isNeXusFile(filename)

    def report(self, show_attributes=True):
        '''
        return the structure of the HDF5 file in a list of strings
        
        The work of parsing the datafile is done in this method.
        '''
        if self.filename is None: return None
        self.show_attributes = show_attributes
        f = h5py.File(self.filename, 'r')
        txt = self.filename
        if self.isNeXus:
            txt += " : NeXus data file"
        structure = self._renderGroup(f, txt, indentation = "")
        f.close()
        return structure

    def _renderGroup(self, obj, name, indentation = "  "):
        '''return a [formatted_string] with the contents of the group'''
        s = []
        nxclass = obj.attrs.get('NX_class', '')
        if len(nxclass) > 0:
            if isinstance(nxclass, numpy.ndarray):      # attribute reported as DATATYPE SIMPLE
                nxclass = nxclass[0]                    # convert as if DATATYPE SCALAR
            nxclass = ":" + nxclass
        s += [ indentation + name + nxclass ]
        s += self._renderAttributes(obj, indentation)
        # show datasets and links next
        groups = []
        for itemname in sorted(obj):
            linkref  = obj.get(itemname, getlink=True)
            try:
                # this will fail for external links if file is not available
                classref = obj.get(itemname, getclass=True)
            except KeyError:
                classref = None

            if classref is None:
                s += [ '%s  %s: external file missing' % (indentation, itemname) ]
                fmt = '%s    %s = %s'
                s += [ fmt % (indentation, '@file', linkref.filename) ]
                s += [ fmt % (indentation, '@path', linkref.path) ]
            else:
                value = obj.get(itemname)
                if isNeXusLink(value):
                    s += self._renderLinkedObject(value, itemname, indentation+"  ")
                elif isHdf5Group(value) or isHdf5File(value):
                    groups.append(value)
                    # TODO: report external group links in the right place
                    # The problem is the link file and path need to be fed into the
                    # next call to _renderGroup().  No such design exists now for that. 
                elif isHdf5Dataset(value):
                    s += self._renderDataset(value, itemname, indentation+"  ")
                    if isHdf5ExternalLink(linkref):
                        # When "classref" is defined, then external data is available
                        fmt = '%s    %s = %s'
                        s += [ fmt % (indentation, '@file', linkref.filename) ]
                        s += [ fmt % (indentation, '@path', linkref.path) ]
                else:
                    msg = "unidentified %s: %s, %s", itemname, repr(classref), repr(linkref)
                    raise Exception, msg

        for value in groups:        # show things that look like groups
            itemname = value.name.split("/")[-1]
            s += self._renderGroup(value, itemname, indentation+"  ")
        
        return s

    def _renderAttributes(self, obj, indentation = "  "):
        '''return a [formatted_string] with any attributes'''
        s = []
        if self.show_attributes:
            for name, value in obj.attrs.iteritems():
                s.append("%s  @%s = %s" % (indentation, name, str(value)))
        return s

    def _renderLinkedObject(self, obj, name, indentation = "  "):
        '''return a [formatted_string] with the name and target of a NeXus linked object'''
        s = []
        s.append("%s%s --> %s" % (indentation, name, obj.attrs['target']))
        return s

    def _renderDataset(self, dset, name, indentation = "  "):
        '''return a [formatted_string] with the contents and structure of a dataset'''
        shape = dset.shape
        # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        if self.isNeXus:
            if "target" in dset.attrs:
                if dset.attrs['target'] != dset.name:
                    return ["%s%s --> %s" % (indentation, name, dset.attrs['target'])]
        txType = self._renderDsType(dset)
        txShape = self._renderDsShape(dset)
        s = []
        if dset.dtype.kind == 'S':
            if isinstance(dset.value, numpy.ndarray):
                value = " = %s" % dset.value[0]
            else:
                value = " = %s" % str(dset.value)
            s += [ "%s%s:%s%s" % (indentation, name, txType, value) ]
            s += self._renderAttributes(dset, indentation)
            # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        elif dset.dtype.kind == 'O':
            value = " = %s" % str(dset.value)
            s += [ "%s%s:%s%s" % (indentation, name, txType, value) ]
            s += self._renderAttributes(dset, indentation)
        elif shape == (1,):
            value = " = %s" % str(dset[0])
            s += [ "%s%s:%s%s%s" % (indentation, name, txType, 
                                   txShape, value) ]
            s += self._renderAttributes(dset, indentation)
        else:

            if self.array_items_shown > 2:
                value = self._renderArray(dset, indentation + '  ')
                if len(dset.shape) < 2:
                    # show the array inline with the field
                    s += [ "%s%s:%s%s = %s" % (
                            indentation, name, txType, txShape, value) ]
                else:
                    # show multi-D arrays different
                    s += [ "%s%s:%s%s = __array" % (
                            indentation, name, txType, txShape) ]
                    s += [ "%s  %s = %s" % (indentation, "__array", value) ]
            else:
                s += [ "%s%s:%s%s = [ ... ]" % (
                        indentation, name, txType, txShape) ]

            # show these after __array
            s += self._renderAttributes(dset, indentation)
        return s

    def _renderDsType(self, obj):
        ''' get the storage (data) type of the dataset '''
        t = str(obj.dtype)
        # dset.dtype.kind == 'S', nchar = dset.dtype.itemsize
        if obj.dtype.kind == 'S':        # fixed-length string
            t = 'char[%s]' % obj.dtype.itemsize
        elif obj.dtype.kind == 'O':      # variable-length string
            t = 'CHAR'
        if self.isNeXus:
            t = 'NX_' + t.upper()
        return t

    def _renderDsShape(self, obj):
        ''' return the shape of the HDF5 dataset '''
        s = obj.shape
        l = []
        for dim in s:
            l.append(str(dim))
        if l == ['1']:
            result = ""
        else:
            result = "[%s]" % ",".join(l)
        return result

    def _renderArray(self, obj, indentation = '  '):
        ''' nicely format an array up to arbitrary rank '''
        shape = obj.shape
        r = ""
        if len(shape) > 0:
            r = self._renderNdArray(obj, indentation + '  ')
        return r

    def _decideNumShown(self, n):
        ''' determine how many values to show '''
        if self.array_items_shown != None:
            if n > self.array_items_shown:
                n = self.array_items_shown - 2
        return n

    def _renderNdArray(self, obj, indentation = '  '):
        ''' return a list of lower-dimension arrays, nicely formatted '''
        
        def __render(obj, rank, key, indents):
            if rank == 1:
                item = obj[key]
            else:
                # this replaces a lot of code: if rank == ...
                indices = ', '.join( [str(key)] + (':'*(rank-1)).split() )
                part = eval('obj[%s]' % indices)
                item = self._renderNdArray(part, indents + '  ')    # recursion
            return item

        shape = obj.shape
        rank = len(shape)
        if rank < 1: return None
        n = self._decideNumShown( shape[0] )
        r = []
        for i in range(n):
            r.append( __render(obj, rank, i, indentation + '  ') )
        if n < shape[0]:
            r.append("...")    # skip over most
            r.append( __render(obj, rank, -1, indentation + '  ') ) # last one

        if rank == 1:
            s = str( r )
        else:
            s = "[\n" + indentation + '  '
            s += ("\n" + indentation + '  ').join( r )
            s += "\n" + indentation + "]"
        return s


def isNeXusFile(filename):
    '''
    is `filename` is a NeXus HDF5 file?
    
    In short, verify this NeXus classpath exists::
    
        /NXentry/NXdata/dataset/@signal=1
    
    Tests for the existence of any NXentry group 
    containing any NXdata group containing a single dataset 
    with signal=1 attribute (allows either integer or text representation).
    This is the minimum requirement for a NeXus data file.
    
    This method ignores any exceptions incurred.
    '''
    try:
        f = h5py.File(filename, 'r')
        if not isHdf5File(f):
            f.close()
            return False
        for node0 in f.values():
            if not isNeXusGroup(node0, 'NXentry'):
                continue
            for node1 in node0.values():
                if not isNeXusGroup(node1, 'NXdata'):
                    continue
                signal1_count = 0   # count datasets with signal=1 attribute
                for node2 in node1.values():
                    if isNeXusDataset(node2) and node2.attrs.get('signal', None) in (1, '1'):
                        signal1_count += 1
                if signal1_count == 1:  # ensure only 1 is defined
                    return True
        f.close()
    except:
        pass    # ignore any Exceptions, they mean that result stays "False"
    return False


def isNeXusGroup(obj, NXtype):
    '''is `obj` a NeXus group?'''
    nxclass = None
    if isHdf5Group(obj):
        nxclass = obj.attrs.get('NX_class', None)
        if isinstance(nxclass, numpy.ndarray):
            nxclass = nxclass[0]
    return nxclass == str(NXtype)


def isNeXusDataset(obj):
    '''is `obj` a NeXus dataset?'''
    return isHdf5Dataset(obj)


def isNeXusLink(obj):
    '''is `obj` linked to another NeXus item?'''
    target = obj.attrs.get('target', '')
    return len(target) > 0 and target != obj.name


def isHdf5File(obj):
    '''is `obj` an HDF5 File?'''
    return isinstance(obj, h5py.File)


def isHdf5Group(obj):
    '''is `obj` an HDF5 Group?'''
    return isinstance(obj, h5py.Group)


def isHdf5Dataset(obj):
    '''is `obj` an HDF5 Dataset?'''
    return isinstance(obj, h5py.Dataset)


def isHdf5Link(obj):
    '''is `obj` an HDF5 Link?'''
    return isinstance(obj, h5py.HardLink)


def isHdf5ExternalLink(obj):
    '''is `obj` an HDF5 ExternalLink?'''
    return isinstance(obj, h5py.ExternalLink)


def do_filelist(filelist, limit=5, show_attributes=True):
    '''
    interpret and print the structure of a list of HDF5 files
    
    :param [str] filelist: one or more file names to be interpreted
    :param int limit: maximum number of array items to be shown (default = 5)
    '''
    for item in filelist:
        mc = H5toText(item)
        mc.array_items_shown = limit
        print '\n'.join(mc.report(show_attributes) or '')


def main():
    '''standard command-line interface'''
    NUM_DISPLAYED_DEFAULT = 5
    NUM_DISPLAYED_MIN = 3
    import argparse
    doc = __doc__.strip().splitlines()[0]
    doc += '\n  URL: ' + __url__
    doc += '\n  v' + spec2nexus.__version__
    parser = argparse.ArgumentParser(prog='h5toText', description=doc)
    parser.add_argument('infile', 
                        action='store', 
                        nargs='+', 
                        help="HDF5 data file name(s)")
    msg =  "limit number of displayed array items to NUM_DISPLAYED"
    msg += " (must be >=%d or 'None')" % NUM_DISPLAYED_MIN
    msg += ", default = %s" % str(NUM_DISPLAYED_DEFAULT)
    parser.add_argument('-n', 
                        action='store', 
                        dest='num_displayed', 
                        help=msg, 
                        default=str(NUM_DISPLAYED_DEFAULT))
    parser.add_argument('-a', 
                        action='store_false', 
                        default=True,
                        dest='show_attributes',
                        help='Do not print attributes')
    parser.add_argument('-v', 
                        '--version', 
                        action='version', 
                        version=spec2nexus.__version__)
    cmd_args = parser.parse_args()

    if cmd_args.num_displayed.lower() == "none":
        limit = None
    else:
        limit = max(NUM_DISPLAYED_MIN, int(cmd_args.num_displayed))
    do_filelist(cmd_args.infile, limit, cmd_args.show_attributes)


if __name__ == '__main__':
    main()
