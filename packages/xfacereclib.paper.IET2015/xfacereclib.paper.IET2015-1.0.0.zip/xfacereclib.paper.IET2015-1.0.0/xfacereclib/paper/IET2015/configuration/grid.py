import facereclib

# define the SGE queue using all the default parameters
sge = facereclib.utils.GridParameters(
  'sge',
  number_of_preprocessing_jobs = 2,
  number_of_extraction_jobs = 2,
  number_of_projection_jobs = 2,
  number_of_enrollment_jobs = 2,
  number_of_scoring_jobs = 4,
)


# define a 'local' queue using two parallel processes **per job**
local = facereclib.utils.GridParameters(
  'local',
  number_of_parallel_processes = 2,
)
