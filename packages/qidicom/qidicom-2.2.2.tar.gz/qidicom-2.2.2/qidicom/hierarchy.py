from collections import defaultdict
from qiutil.dictionary_hierarchy import DictionaryHierarchy
from . import (reader, meta)


def group_by(tag, *files):
    """
    Groups DICOM files by the given tag description. Subtraction
    images, indicated by a ``SUB`` DICOM Image Type, are ignored.
    The tag can elide blanks, e.g. 'SeriesNumber'.

    :param tag: the DICOM tag
    :param dicom_files: the DICOM files or directories
    :return: a {tag: [DICOM file names]} dictionary
    """
    # Remove tag blanks.
    tag = tag.replace(' ', '')
    series_dict = defaultdict(list)
    for ds in reader.iter_dicom_headers(*files):
        # Ignore subtraction images.
        if not 'SUB' in ds.ImageType:
            # The dictionary key is the string form of the DICOM tag value
            # rather than the tag value itself to work around the following
            # pydicom bug:
            # * Serializing a pydicom tag value with Python 2.x results in
            #   the following error:
            #     TypeError: a class that defines __slots__ without defining __getstate__ cannot be pickled
            #   The work-around is to unwrap the tag value.
            value = getattr(ds, tag)
            # Unwrap the value as either an integer or a string.
            key = int(value) if isinstance(value, int) else str(value)
            series_dict[key].append(ds.filename)

    return series_dict

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
    ImageHierarchy wraps the DICOM image subject/study/series/image
    hierarchy.
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
