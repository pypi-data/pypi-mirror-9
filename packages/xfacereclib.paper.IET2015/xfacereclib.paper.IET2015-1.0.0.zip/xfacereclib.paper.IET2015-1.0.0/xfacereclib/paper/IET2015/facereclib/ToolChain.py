#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>

from facereclib.toolchain import ToolChain
from facereclib import utils
import os

class PerturbedToolChain (ToolChain):
  """This class includes functionalities for a default tool chain to produce verification scores."""

  def __init__(self, file_selector, write_compressed_score_files = False):
    """Initializes the tool chain object with the current file selector."""
    # only call base class constructor
    ToolChain.__init__(self, file_selector, write_compressed_score_files)


  def is_probe_file(self, file_name, probe_files):
    """Checks whether the given file name belongs to one of the probe files."""
    for probe_file in probe_files:
      if str(probe_file.path) in str(file_name):
        return True
    return False


  def preprocess_data(self, preprocessor, groups=None, indices=None, force=False):
    """Preprocesses the original data with the given preprocessor.
    For all data of the probe list, the preprocessor is called with parameter 'crop_preturbed' set to ``True``
    all others (training set and enrollment set) is called with 'crop_preturbed' set to ``False``.
    """
    # get the file lists
    data_files = self.m_file_selector.original_data_list(groups=groups)
    preprocessed_data_files = self.m_file_selector.preprocessed_data_list(groups=groups)

    probe_files = self.m_file_selector.probe_objects(group='dev')

    # select a subset of keys to iterate
    if indices != None:
      index_range = range(indices[0], indices[1])
      utils.info("- Preprocessing: splitting of index range %s" % str(indices))
    else:
      index_range = range(len(data_files))

    utils.ensure_dir(self.m_file_selector.preprocessed_directory)
    utils.info("- Preprocessing: processing %d data files from directory '%s' to directory '%s'" % (len(index_range), self.m_file_selector.m_database.original_directory, self.m_file_selector.preprocessed_directory))

    # read annotation files
    annotation_list = self.m_file_selector.annotation_list(groups=groups)

    for i in index_range:
      preprocessed_data_file = preprocessed_data_files[i]

      if not self.__check_file__(preprocessed_data_file, force, 1000):
        data = preprocessor.read_original_data(str(data_files[i]))

        # get the annotations; might be None
        annotations = self.m_file_selector.get_annotations(annotation_list[i])

        # call the preprocessor
        preprocessed_data = preprocessor(data, annotations, crop_perturbed = self.is_probe_file(preprocessed_data_file, probe_files))
        if preprocessed_data is None:
          utils.error("Preprocessing of file %s was not successful" % str(data_files[i]))

        utils.ensure_dir(os.path.dirname(preprocessed_data_file))
        preprocessor.save_data(preprocessed_data, str(preprocessed_data_file))



