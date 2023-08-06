
# Generate scores for translations applied to eye annotations
#
# Abhishek Dutta <http://abhishekdutta.org>
# May 01, 2013


import os
import argparse
import bob.io.base
import pkg_resources
import facereclib



def command_line_options(command_line_arguments=None):

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('--algorithms', '-a',  nargs='+', default = ['eigenfaces', 'fisherfaces', 'gabor-jet', 'lgbphs', 'isv'], help = "The FR algorithms to execute")
  parser.add_argument('--grid', '-g', help = "Enable SGE grid submission using the given grid configuration")
  parser.add_argument('--world-types', '-w', nargs='+', default = ['FaceVACS', 'Idiap', 'UT'], choices = ('FaceVACS', 'VeriLook', 'Idiap', 'UT'), help = "The types of annotations to use for training and enrollment")
  parser.add_argument('--probe-types', '-p', nargs='+', default = ['FaceVACS', 'VeriLook', 'Idiap', 'UT'], choices = ('FaceVACS', 'VeriLook', 'Idiap', 'UT'), help = "The types of annotations to use for probing")
  parser.add_argument('parameters', nargs = argparse.REMAINDER, help = "Parameters directly passed to the face verify script. Use -- to separate this parameters from the parameters of this script. See 'bin/faceverify.py --help' for a complete list of options.")

  facereclib.utils.add_logger_command_line_option(parser)
  args = parser.parse_args(command_line_arguments)
  facereclib.utils.set_verbosity_level(args.verbose)

  if not args.parameters:
    args.parameters = ['--']
  if args.verbose:
    args.parameters.append('-' + 'v'*args.verbose)
  if args.grid:
    args.parameters.extend(['--grid', args.grid])

  return args


ALGORITHMS = {
  'eigenfaces' : ['--features', 'linearize', '--tool', 'pca'],
  'fisherfaces' : ['--features', 'linearize', '--tool', 'pca+lda'],
  'gabor-jet' : ['--features', 'grid-graph', '--tool', 'gabor-jet'],
  'lgbphs' : ['--features', 'lgbphs', '--tool', 'lgbphs'],
  'isv' : ['--features', 'dct', '--tool', 'isv'],

}

DATABASE = 'facereclib.databases.DatabaseBobZT(\
database=bob.db.multipie.Database(\
original_directory="{img}", \
annotation_directory="{ann}" \
), \
name="multipie", \
protocol="M", \
all_files_options={{"world_noflash":True}}, \
extractor_training_options={{"world_noflash":True}}, \
projector_training_options={{"world_noflash":True}}, \
enroller_training_options={{"world_noflash":True}}\
)'

def main():
  args = command_line_options()

  # preprocess the data
  from .faceverify import parse_args, face_verify

  # get the database directory
  db = facereclib.utils.resources.load_resource("multipie-m", "database").m_database
  image_directory = os.path.realpath(db.original_directory)
  annotation_directory = os.path.dirname(os.path.realpath(db.annotation_directory))

  types = list(set(args.world_types) | set(args.probe_types))
  deps = []
  for t in types:
    # use 'eigenface' algorithm for preprocessing
    call = [
      './bin/faceverify_iet.py',
      '--database', DATABASE.format(img=image_directory, ann=os.path.join(annotation_directory, t)),
      '--imports', 'bob.db.multipie', 'facereclib', 'xfacereclib.paper.IET2015',
      '--sub-directory', os.path.join('annotations', t),
      '--execute-only', 'preprocessing',
      '--preprocessed-data-directory', 'preprocessed',
      '--preprocessing', 'xfacereclib.paper.IET2015.facereclib.FixedPerturbation(cropped_image_size=(80,64), cropped_positions = {"reye":(16,15), "leye":(16,48)}, translation=(0,0), angle=0)',
    ] + ALGORITHMS['eigenfaces'] + args.parameters[1:]

    print facereclib.utils.command_line(call)

    verif_args = parse_args(call[1:])
    job_ids = face_verify(verif_args, call)
    dep = None
    if 'preprocessing' in job_ids:
      dep = [job_ids['preprocessing']]

    # extract features and enroll models for all algorithms
    for algorithm in args.algorithms:
      call = [
        './bin/faceverify_iet.py',
        '--database', 'multipie-m',
        '--sub-directory', os.path.join('annotations', t, algorithm),
        '--execute-only', 'extractor-training', 'extraction', 'projector-training', 'projection', 'enroller-training', 'enrollment',
        '--preprocessed-data-directory', '../preprocessed',
        '--features-directory', 'features',
        '--projected-features-directory', 'projected',
        '--models-directories', 'models', 'tmodels',
        '--preprocessing', 'face-crop', # since it needs to be specified...
      ] + ALGORITHMS[algorithm] + args.parameters[1:]

      print facereclib.utils.command_line(call)
      verif_args = parse_args(call[1:])
      job_ids = face_verify(verif_args, call, external_dependencies = dep)
      if 'enroll_dev_N' in job_ids:
        deps.append(job_ids['enroll_dev_N'])


  # now, execute the algorithms
  for model in args.world_types:
    for probe in args.probe_types:
      for algorithm in args.algorithms:
        call = [
          './bin/faceverify.py',
          '--database', 'multipie-m',
          '--sub-directory', os.path.join('annotations', model, algorithm),
          '--execute-only', 'projection', 'score-computation', 'concatenation',
          '--features-directory', os.path.join('../..', probe, algorithm, 'features'),
#          '--projector-file', os.path.join('../..', probe, algorithm, 'Projector'),
          '--projected-features-directory', os.path.join(probe, 'projected'),
          '--models-directories', 'models', 'tmodels',
          '--score-sub-directory', probe,
          '--preprocessing', 'face-crop', # since it needs to be specified...
        ] + ALGORITHMS[algorithm] + args.parameters[1:]

        verif_args = parse_args(call[1:])
        job_ids = face_verify(verif_args, call, external_dependencies = deps)
