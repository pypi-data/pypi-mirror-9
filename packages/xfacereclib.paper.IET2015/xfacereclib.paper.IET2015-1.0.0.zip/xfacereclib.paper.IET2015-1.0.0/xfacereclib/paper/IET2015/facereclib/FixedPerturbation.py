#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Fri Oct  3 16:20:46 CEST 2014
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math

from facereclib.preprocessing import FaceCrop, Preprocessor

class FixedPerturbation (Preprocessor):
  """Crops the face according to the eye positions, possibly adding perturbations

  Keyword parameters:

  cropped_positions: {'reye':(y,x), 'leye':(y,x)}
    Specifies the default cropped positions in the aligned image.

  translation: (int, int)
    The translation that is added to the eye locations of the probe images, in aligned image dimensions.

  angle: float
    The angle that is added to the eye locations of the probe images.
    The rotation center is the center between the eyes.

  """

  def __init__(
      self,
      cropped_positions,  # dictionary of the cropped positions, usually: {'reye':(RIGHT_EYE_Y, RIGHT_EYE_X) , 'leye':(LEFT_EYE_Y, LEFT_EYE_X)}
      translation = (0.,0.),
      angle = 0.,
      **kwargs           # Other keyword arguments that will be directly passed to the FaceCrop classes
  ):

    # call base class constructor with all our parameters (mainly for logging purposes)
    Preprocessor.__init__(self, cropped_positions=cropped_positions, translation=translation, angle=angle, **kwargs)


    # here, we keep two versions of the face cropper:
    # ... one for cropping default faces:
    self.default_cropper = FaceCrop(cropped_positions=cropped_positions, **kwargs)

    # ... and one for cropping perturbed faces:

    # compute fixed offset positions for face cropping
    # instead of shifting the eyes in the perturbed original image
    # we here directly shift the eye positions (in opposite direction) in the preprocessed image
    assert 'reye' in cropped_positions and 'leye' in cropped_positions
    rey, rex = cropped_positions['reye']
    ley, lex = cropped_positions['leye']

    # compute eye center (transformation center)
    cy = (ley + rey)/2.
    cx = (lex + rex)/2.

    # compute rotation
    cos_angle = math.cos(math.radians(angle))
    sin_angle = math.sin(math.radians(angle))

    # compute new eye locations
    new_positions = {
      'reye' : (
        + (rey - cy) * cos_angle + (rex - cx) * sin_angle + cy + translation[0],
        - (rey - cy) * sin_angle + (rex - cx) * cos_angle + cx + translation[1]
      ),
      'leye' : (
        + (ley - cy) * cos_angle + (lex - cx) * sin_angle + cy + translation[0],
        - (ley - cy) * sin_angle + (lex - cx) * cos_angle + cx + translation[1]
      )
    }

    # perturber cropper
    self.perturbed_cropper = FaceCrop(cropped_positions=new_positions, **kwargs)


  def __call__(self, image, annotations, crop_perturbed):
    """Performs face cropping in the given image using the given annotations.
    If crop_perturbed is set to True (e.g. for probe images), the eye positions are perturbed.
    Otherwise, the default eye locations are used.
    """
    if crop_perturbed:
      return self.perturbed_cropper(image, annotations)
    else:
      return self.default_cropper(image, annotations)

