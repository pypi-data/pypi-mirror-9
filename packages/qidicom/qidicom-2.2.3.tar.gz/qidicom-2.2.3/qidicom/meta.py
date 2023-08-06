import os
import re
import operator
from dicom import datadict
from qiutil.logging import logger
from . import (reader, writer)

# Uncomment to debug pydicom.
# import dicom
# dicom.debug(True)

def select(ds, *tags):
    """
    Reads the given DICOM dataset tags.
    
    :param ds: the pydicom dicom object
    :param tags: the names of tags to read (default all unbracketed tags)
    :return: the tag name => value dictionary
    """
    if not tags:
        # Skip tags with a bracketed name.
        tags = (de.name for de in ds if de.name and de.name[0] != '[')
    tdict = {}
    for t in tags:
        try:
            # The tag attribute.
            tattr = re.sub('\W', '', t)
            # Collect the tag value.
            tdict[t] = operator.attrgetter(tattr)(ds)
        except AttributeError:
            pass
    
    return tdict


def edit(*in_files, **opts):
    """
    Sets the tags of the given DICOM files.

    :param in_files: the input DICOM files or directories containing
        DICOM files
    :param opts: the DICOM header (I{name}, I{value}) tag values to set
        and the following option:
    :param dest: the destination directory (default current directory)
    :return: the modified file paths
    """
    dest = opts.pop('dest', os.getcwd())
    # Name -> tag converter.
    tag_for = lambda name: datadict.tag_for_name(name.replace(' ', ''))
    # The {tag: value} dictionary.
    tv = {tag_for(name): value for name, value in opts.iteritems()}
    # The {tag: DICOM VR} dictionary.
    tvr = {tag: datadict.get_entry(tag)[0] for tag in tv.iterkeys()}

    # The array to collect the DICOM file names.
    fnames = []
    # Edit the files.
    logger(__name__).info("Editing the DICOM files with the following tag"
                          " values: %s..." % tv)
    for ds in writer.edit(*in_files, dest=dest):
        # Set the tag values.
        for tag, value in tv.iteritems():
            if tag in ds:
                ds[tag].value = value
            else:
                ds.add_new(tag, tvr[tag], value)
        _, fname = os.path.split(ds.filename)
        fnames.append(fname)

    # Return the output file paths.
    return [os.path.join(dest, f) for f in fnames]
