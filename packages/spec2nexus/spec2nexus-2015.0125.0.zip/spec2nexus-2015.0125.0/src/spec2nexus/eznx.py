#!/usr/bin/env python
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2015, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


'''
(Easy NeXus) support reading & writing NeXus HDF5 files using h5py

:predecessor: NeXus h5py example code: ``my_lib.py`` [#]_

.. [#] http://download.nexusformat.org/doc/html/examples/h5py/index.html#mylib-support-module


.. rubric:: Dependencies

* h5py: interface to HDF5 file format


.. rubric:: Exceptions raised

* None


.. rubric:: Example (using ipython)

::

    In [1]: from spec2nexus import eznx
    In [2]: root = eznx.makeFile('test.h5', creator='eznx')
    In [3]: nxentry = eznx.makeGroup(root, 'entry', 'NXentry')
    In [4]: eznx.write_dataset(nxentry, 'title', 'simple test data')
    Out[4]: <HDF5 dataset "title": shape (), type "|O8">
    In [5]: nxdata = eznx.makeGroup(nxentry, 'data', 'NXdata')
    In [6]: eznx.write_dataset(nxdata, 'tth', [10.0, 10.1, 10.2, 10.3], units='degrees')
    Out[6]: <HDF5 dataset "tth": shape (4,), type "<f8">
    In [7]: eznx.write_dataset(nxdata, 'counts', [1, 50, 1000, 5], signal=1, axes='tth', units='counts')
    Out[7]: <HDF5 dataset "counts": shape (4,), type "<i8">
    In [8]: root.close()

.. index:: NeXus structure; SPEC data

The resulting (binary) data file has this structure::

    test.h5:NeXus data file
      @creator = eznx
      entry:NXentry
        @NX_class = NXentry
        title:NX_data = simple test data
        data:NXdata
          @NX_class = NXdata
          counts:NX_INT64[4] = [1, 50, 1000, 5]
            @units = counts
            @signal = 1
            @axes = tth
          tth:NX_FLOAT64[4] = [10.0, 10.1, 10.199999999999999, 10.300000000000001]
            @units = degrees


.. rubric::  Classes and Methods

'''


import h5py    # HDF5 support
#import numpy   # in this case, provides data structures


def makeFile(filename, **attr):
    """
    create and open an empty NeXus HDF5 file using h5py
    
    Any named parameters in the call to this method will be saved as
    attributes of the root of the file.
    Note that ``**attr`` is a dictionary of named parameters.

    :param str filename: valid file name
    :param dict attr: optional dictionary of attributes
    :return: h5py file object
    """
    obj = h5py.File(filename, "w")
    addAttributes(obj, **attr)
    return obj


def makeGroup(parent, name, nxclass, **attr):
    """
    create a NeXus group
    
    Any named parameters in the call to this method 
    will be saved as attributes of the group.
    Note that ``**attr`` is a dictionary of named parameters.
    
    :param obj parent: parent group
    :param str name: valid NeXus group name
    :param str nxclass: valid NeXus class name
    :param dict attr: optional dictionary of attributes
    :return: h5py group object

    """
    obj = parent.create_group(name)
    obj.attrs["NX_class"] = nxclass
    addAttributes(obj, **attr)
    return obj


def openGroup(parent, name, nx_class, **attr):
    '''open or create the NeXus/HDF5 group, return the object

    :param obj parent: h5py parent object
    :param str name: valid NeXus group name to open or create
    :param str nxclass: valid NeXus class name (base class or application definition)
    :param dict attr: optional dictionary of attributes
    '''
    try:
        group = parent[name]
        addAttributes(parent, **attr)
    except KeyError:
        group = makeGroup(parent, name, nx_class, **attr)
    return group


def makeDataset(parent, name, data = None, **attr):
    '''
    create and write data to a dataset in the HDF5 file hierarchy
    
    Any named parameters in the call to this method 
	will be saved as attributes of the dataset.

    :param obj parent: parent group
    :param str name: valid NeXus dataset name
    :param obj data: the information to be written
    :param dict attr: optional dictionary of attributes
    :return: h5py dataset object
    '''
    if data is None:
        obj = parent.create_dataset(name)
    else:
        if isinstance(data, float) or isinstance(data, int) or isinstance(data, str):
            data = [data,]
        obj = parent.create_dataset(name, data=data)
    addAttributes(obj, **attr)
    return obj


def write_dataset(parent, name, data, **attr):
    '''write to the NeXus/HDF5 dataset, create it if necessary, return the object

    :param obj parent: h5py parent object
    :param str name: valid NeXus dataset name to write
    :param obj data: the information to be written
    :param dict attr: optional dictionary of attributes
    '''
    try:
        dset = parent[name]
        dset[:] = data
        addAttributes(dset, **attr)
    except (KeyError, TypeError):
        dset = makeDataset(parent, name, data, **attr)
    return dset


def makeLink(parent, sourceObject, targetName):
    """
    create an internal NeXus (hard) link in an HDF5 file

    :param obj parent: parent group of source
    :param obj sourceObject: existing HDF5 object
    :param str targetName: HDF5 node path to be created, 
                            such as ``/entry/data/data``
    """
    if not 'target' in sourceObject.attrs:
        # NeXus link, NOT an HDF5 link!
        sourceObject.attrs["target"] = str(sourceObject.name)
    import h5py.h5g
    parent._id.link(sourceObject.name, targetName, h5py.h5g.LINK_HARD)


def makeExternalLink(hdf5FileObject, sourceFile, sourcePath, targetPath):
    """
    create an external link from sourceFile, sourcePath to targetPath in hdf5FileObject

    :param obj hdf5FileObject: open HDF5 file object
    :param str sourceFile: file containing existing HDF5 object at sourcePath
    :param str sourcePath: path to existing HDF5 object in sourceFile
    :param str targetPath: full node path to be created in current open HDF5 file, 
                            such as ``/entry/data/data``
                            
    .. note::
       Since the object retrieved is in a different file, 
       its ".file" and ".parent" properties will refer to 
       objects in that file, not the file in which the link resides.

    :see: http://www.h5py.org/docs-1.3/guide/group.html#external-links
    
    This routine is provided as a reminder how to do this simple operation.
    """
    hdf5FileObject[targetPath] = h5py.ExternalLink(sourceFile, sourcePath)


def addAttributes(parent, **attr):
    """
    add attributes to an h5py data item

    :param obj parent: h5py parent object
    :param dict attr: optional dictionary of attributes
    """
    if attr and type(attr) == type({}):
        # attr is a dictionary of attributes
        for k, v in attr.items():
            parent.attrs[k] = v


def read_nexus_field(parent, dataset_name, astype=None):
    '''
    get a dataset from the HDF5 parent group
    
    :param obj parent: h5py parent object
    :param str dataset_name: name of the dataset (NeXus field) to be read
    :param obj astype: option to return as different data type
    '''
    try:
        dataset = parent[dataset_name]
    except KeyError:
        return None
    dtype = dataset.dtype
    if astype is not None:
        dtype = astype
    if len(dataset.shape) > 1:
        raise RuntimeError, "unexpected %d-D data" % len(dataset.shape)
    if dataset.size > 1:
        return dataset[...].astype(dtype)   # as array
    else:
        return dataset[0].astype(dtype)     # as scalar


def read_nexus_group_fields(parent, name, fields):
    '''
    return the fields in the NeXus group as a dict(name=dataset)
    
    This routine provides a mass way to read a directed list
    of datasets (NeXus fields) in an HDF5 group.
    
    :param obj parent: h5py parent object
    :param str name: name of the group containing the fields
    :param [name] fields: list of field names to be read
    :returns: dictionary of {name:dataset}
    :raises KeyError: if a field is not found
    '''
    group = parent[name]
    return {key: read_nexus_field(group, key) for key in fields}
