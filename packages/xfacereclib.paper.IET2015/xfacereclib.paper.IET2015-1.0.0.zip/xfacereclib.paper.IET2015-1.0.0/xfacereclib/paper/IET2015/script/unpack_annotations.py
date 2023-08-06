
# Generate scores for translations applied to eye annotations
#
# Abhishek Dutta <http://abhishekdutta.org>
# May 01, 2013

"""Extracts the eye landmarks for the given annotation types into a directory structure required by the bob.db.multipie Multi-PIE database interface.
The default output-directory is selected such that the current database interface will find them automatically.
If you change the --output-directory option, please change the database configuration file accordingly.
"""

import os
import argparse
import bob.io.base
import pkg_resources
import facereclib



def command_line_options(command_line_arguments=None):

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('--landmark-file', '-f', default = pkg_resources.resource_filename('xfacereclib.paper.IET2015', 'data/Landmarks.csv'), help = "The original landmark file (rarely changed)")
  parser.add_argument('--output-directory', '-D', default = "annotations", help = "The base annotation directory to write, rarely changed")
  parser.add_argument('--types', '-t', nargs='+', default = ['FaceVACS', 'VeriLook', 'Idiap', 'UT'], choices = ('FaceVACS', 'VeriLook', 'Idiap', 'UT'), help = "The types of annotations to extract (will be used as sub-directory names)")

  facereclib.utils.add_logger_command_line_option(parser)
  args = parser.parse_args(command_line_arguments)
  facereclib.utils.set_verbosity_level(args.verbose)

  return args


indices = {
  'FaceVACS' : [2, 3, 4, 5],
  'VeriLook' : [6, 7, 8, 9],
  'UT'       : [10, 11, 12, 13],
  'Idiap'    : [14, 15, 16, 17]
}

def main():
  args = command_line_options()

  facereclib.utils.info("Reading landmarks from file '%s'" % args.landmark_file)
  # read landmark file
  with open(args.landmark_file) as f:
    facereclib.utils.info("Writing landmarks to directories %s" % str([os.path.join(args.output_directory, t) for t in args.types]))
    # skip first line
    f.readline()
    for line in f:
      splits = line.rstrip().split(',')
      assert len(splits) == 18
      # write files
      basename = splits[1] + "_00.pos"
      for t in args.types:
        filename = os.path.join(args.output_directory, t, basename)
        facereclib.utils.debug("Writing file '%s'" % filename)
        bob.io.base.create_directories_safe(os.path.dirname(filename))
        with open(filename, 'w') as a:
          # write the number of annotations and the annotations themselves
          a.write("2\n%s %s\n%s %s\n" % tuple(splits[i] for i in indices[t]))
