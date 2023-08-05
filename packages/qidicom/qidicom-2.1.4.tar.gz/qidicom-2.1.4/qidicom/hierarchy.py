from collections import defaultdict
from qiutil.dictionary_hierarchy import DictionaryHierarchy
from . import (reader, meta)

def read_hierarchy(*files):
    """
    Returns the ImageHierarchy for the DICOM files in the given locations.

    :param files: the files or directories to walk for DICOM files
    :return: the image hierarchy
    :rtype: :class:`qiutil.image_hierarchy.ImageHierarchy`
    """
    return ImageHierarchy(*files)


class ImageHierarchy(DictionaryHierarchy):
    """
    ImageHierarchy wraps the DICOM image subject-study-series-image hierarchy.
    """

    TAGS = ('Patient ID', 'Study Instance UID', 'Series Instance UID',
            'Instance Number')

    def __init__(self, *files):
        """
        :param the input DICOM files
        """
        
        # the subject: series: image nested dictionary
        self.tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        super(ImageHierarchy, self).__init__(self.tree)
        for ds in reader.iter_dicom_headers(*files):
            self.add(ds)

    def add(self, ds):
        """
        Adds the subject-study-series-image hierarchy entries from the given
        DICOM dataset.

        :param ds: the DICOM dataset
        """
        # build the image hierarchy
        tdict = meta.select(ds, *ImageHierarchy.TAGS)
        path = [tdict[t] for t in ImageHierarchy.TAGS]
        self.tree[path[0]][path[1]][path[2]].append(path[3])
