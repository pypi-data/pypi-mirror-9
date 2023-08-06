#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>

from facereclib.script.faceverify import ToolChainExecutorZT, parse_args
from facereclib import utils

from ..facereclib import PerturbedToolChain
import sys

def face_verify(args, command_line_parameters, external_dependencies = [], external_fake_job_id = 0):
  """This is the main entry point for computing face verification experiments.
  You just have to specify configurations for any of the steps of the toolchain, which are:
  -- the database
  -- the preprocessing
  -- feature extraction
  -- the recognition tool
  -- and the grid configuration (in case, the function should be executed in the grid).
  Additionally, you can skip parts of the toolchain by selecting proper --skip-... parameters.
  If your probe files are not too big, you can also specify the --preload-probes switch to speed up the score computation.
  If files should be re-generated, please specify the --force option (might be combined with the --skip-... options)."""

  # generate tool chain executor
  executor = ToolChainExecutorZT(args)

  #####################################
  # overwrite the ToolChain to use ours
  executor.m_tool_chain = PerturbedToolChain(executor.m_file_selector, args.write_compressed_score_files)

  # the rest is copied from the original face_verify function...
  #####################################

  # as the main entry point, check whether the sub-task is specified
  if args.sub_task is not None:
    # execute the desired sub-task
    executor.execute_grid_job()
    return {}
  elif not args.grid:
    if args.timer is not None and not len(args.timer):
      args.timer = ('real', 'system', 'user')
    # not in a grid, use default tool chain sequentially
    if args.timer:
      utils.info("- Timer: Starting timer")
      start_time = os.times()

    executor.write_info(command_line_parameters)

    executor.execute_tool_chain()

    if args.timer:
      end_time = os.times()
      utils.info("- Timer: Stopped timer")

      for t in args.timer:
        index = {'real':4, 'system':1, 'user':0}[t]
        print ("Elapsed", t ,"time:", end_time[index] - start_time[index], "seconds")

    return {}

  else:
    # no other parameter given, so deploy new jobs

    # get the name of this file
    this_file = __file__
    if this_file[-1] == 'c':
      this_file = this_file[0:-1]

    executor.write_info(command_line_parameters)

    # initialize the executor to submit the jobs to the grid
    executor.set_common_parameters(calling_file = this_file, parameters = command_line_parameters, fake_job_id = external_fake_job_id)

    # add the jobs
    job_ids = executor.add_jobs_to_grid(external_dependencies)

    if executor.m_grid.is_local() and args.run_local_scheduler:
      if args.dry_run:
        print ("Would have started the local scheduler to finally run the experiments with parallel jobs")
      else:
        # start the jman local deamon
        executor.execute_local_deamon()
      return {}

    else:
      return job_ids


def main(command_line_parameters = sys.argv):
  """Executes the main function"""
  try:
    # do the command line parsing
    args = parse_args(command_line_parameters[1:])

    # perform face verification test
    face_verify(args, command_line_parameters)
  except Exception as e:
    # track any exceptions as error logs (i.e., to get a time stamp)
    utils.error("During the execution, an exception was raised: %s" % e)
    raise

if __name__ == "__main__":
  main()

