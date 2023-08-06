#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Fri Oct  3 16:26:15 CEST 2014
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
import random

from facereclib.preprocessing import FaceCrop, Preprocessor

class RandomPerturbation (Preprocessor):
  """Crops the face according to the eye positions, adding random perturbations of the eye positions for probe images.

  Keyword parameters:

  cropped_image_size: (int, int)
    The resolution of the aligned image

  cropped_positions: {'reye':(y,x), 'leye':(y,x)}
    Specifies the default cropped positions in the aligned image.

  sigma: (float, float)
    The standard deviations in y and x, applied to the probe image eye coordintes

  seed: int
    The random seed to initialize the random number generator
  """

  def __init__(
      self,
      cropped_image_size, # size of the cropped image in 2D
      cropped_positions,  # dictionary of the cropped positions, usually: {'reye':(RIGHT_EYE_Y, RIGHT_EYE_X) , 'leye':(LEFT_EYE_Y, LEFT_EYE_X)}

      sigma = (1.,1.),
      seed = None,
      **kwargs
  ):

    # call base class constructor with all our parameters (mainly for logging purposes)
    Preprocessor.__init__(self, cropped_image_size=cropped_image_size, cropped_positions=cropped_positions, sigma=sigma, seed=seed, **kwargs)

    # here, we keep one version of the face cropper:
    # ... one for cropping default faces:
    self.default_cropper = FaceCrop(cropped_image_size=cropped_image_size, cropped_positions=cropped_positions, **kwargs)

    # the one for cropping perturbed faces will be generated on the fly
    self.m_cropped_image_size = cropped_image_size
    self.m_cropped_positions = cropped_positions
    self.m_sigma = sigma
    self.m_kwargs = kwargs

    if seed is not None:
      random.seed(seed)
    else:
      random.seed() # initialize with current system time

  def _perturb(self):
    """Perturbes the given annotations with a random seed and clamps it to the aligned image shape"""
    def _shift(v, sigma, min_v, max_v):
      while True:
        s = v + random.gauss(0., sigma)
        if s >= min_v and s <= max_v:
          break
      return s

    return {
      'reye' : (
          _shift(self.m_cropped_positions['reye'][0], self.m_sigma[0], 0, self.m_cropped_image_size[0]),
          _shift(self.m_cropped_positions['reye'][1], self.m_sigma[1], 0, self.m_cropped_image_size[1])
      ),
      'leye' : (
          _shift(self.m_cropped_positions['leye'][0], self.m_sigma[0], 0, self.m_cropped_image_size[0]),
          _shift(self.m_cropped_positions['leye'][1], self.m_sigma[1], 0, self.m_cropped_image_size[1])
      )
    }


  def __call__(self, image, annotations, crop_perturbed):
    """Performs face cropping in the given image using the given annotations.
    If crop_perturbed is set to True (e.g. for probe images), the eye positions are perturbed.
    Otherwise, the default eye locations are used.
    """
    if crop_perturbed:
      # compute new perturbed eye positions and generate a new FaceCrop instance
      perturbed_cropper = FaceCrop(cropped_positions=self._perturb(), cropped_image_size=self.m_cropped_image_size, **self.m_kwargs)
      return perturbed_cropper(image, annotations)
    else:
      return self.default_cropper(image, annotations)

