#!/usr/bin/env python

import bob.db.multipie
import facereclib
import os


# Please update this directory!
MULTIPIE_IMAGE_DIRECTORY = "[YOUR_MULTIPIE_DATABASE_DIRECTORY]"
MULTIPIE_ANNOTATION_DIRECTORY = os.path.realpath(os.path.join(os.path.dirname(__file__), "../../../../annotations/Idiap"))

# This is the database interface that includes the protocol
# When you have another (compatible) database at hand, feel free to replace it here.
database = facereclib.databases.DatabaseBobZT(
    database = bob.db.multipie.Database(
      original_directory = MULTIPIE_IMAGE_DIRECTORY,
      annotation_directory = MULTIPIE_ANNOTATION_DIRECTORY,
    ),
    name = "multipie",
    protocol = 'M',

    all_files_options = {'world_noflash' : True},
    extractor_training_options = {'world_noflash' : True},
    projector_training_options = {'world_noflash' : True},
    enroller_training_options = {'world_noflash' : True}
)
