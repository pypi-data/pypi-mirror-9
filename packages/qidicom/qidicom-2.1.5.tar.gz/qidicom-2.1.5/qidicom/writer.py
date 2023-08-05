import os
from qiutil.logging import logger
from . import reader

def edit(*in_files, **opts):
    """
    Edits the given DICOM files.

    :param in_files: the input DICOM files or directories containing
        DICOM files
    :param opts: the following options:
    :keyword dest: the directory in which to write the modified DICOM
        files (default is to edit in-place)
    :return: the output file paths
    """
    # Prepare the destination directory.
    dest = opts.get('dest')
    if dest:
        dest = os.path.abspath(dest)
        if not os.path.exists(dest):
            os.makedirs(dest)
    else:
        dest = os.getcwd()
    
    # Open the DICOM store on each DICOM file (skipping non-DICOM files),
    # yield to the edit callback and save to the file in the destination
    # directory.
    for ds in reader.iter_dicom(*in_files):
        logger(__name__).debug("Editing the DICOM file %s..." % ds.filename)
        yield ds
        _, fname = os.path.split(ds.filename)
        out_file = os.path.join(dest, fname)
        ds.save_as(out_file)
        logger(__name__).debug("Saved the edited DICOM file as %s." % out_file)
    logger(__name__).info("The edited DICOM files were saved in %s." % dest)
