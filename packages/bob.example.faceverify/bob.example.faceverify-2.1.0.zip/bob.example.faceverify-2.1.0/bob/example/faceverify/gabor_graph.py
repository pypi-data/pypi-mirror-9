#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Wed May  1 11:33:00 CEST 2013
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
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

from __future__ import print_function

# import required bob modules
import bob.db.atnt
import bob.io.base
import bob.io.image
import bob.ip.base
import bob.ip.gabor
import bob.measure

import os, sys
import numpy, math
import matplotlib
matplotlib.use('pdf')
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
from matplotlib import pyplot

from .utils import atnt_database_directory, load_images


# define Gabor wavelet transform class globally since it is reused for all images
gabor_wavelet_transform = bob.ip.gabor.Transform(k_max = 0.25 * math.pi)
# pre-allocate Gabor wavelet transform image in the desired size
trafo_image = numpy.ndarray((gabor_wavelet_transform.number_of_wavelets, 112, 92), numpy.complex128)

def extract_feature(image, extractor):
  """Extracts the Gabor graphs from the given image"""

  # perform Gabor wavelet transform on the image
  gabor_wavelet_transform.transform(image, trafo_image)

  # extract the Gabor graphs from the feature image
  gabor_graph = extractor.extract(trafo_image)

  # return the extracted graph
  return gabor_graph


# define a certain Gabor jet similarity function that should be used
SIMILARITY_FUNCTION = bob.ip.gabor.Similarity('PhaseDiffPlusCanberra', gabor_wavelet_transform)

def main():
  """This function will perform Gabor graph comparison test on the AT&T database."""

  # Check the existence of the AT&T database and download it if not
  # Also check if the AT&T database directory is overwritten by the command line
  image_directory = atnt_database_directory(sys.argv[1] if len(sys.argv) > 1 else None)

  # use the bob.db interface to retrieve information about the Database
  db = bob.db.atnt.Database(original_directory = image_directory)

  # The protocol does not exist for AT&T, but to be able to exchange the database, we define it here.
  protocol = None

  # The group is 'dev', throughout
  group = 'dev'

  # The images of the AT&T database are already cropped, so we don't need to specify a face cropper.
  face_cropper = None
  # For other databases you might want to use:
#  face_cropper = bob.ip.base.FaceEyesNorm(crop_size = (80,64), right_eye = (16,15), left_eye = (16,48))

  # After image cropping, we apply an image preprocessor
  preprocessor = bob.ip.base.TanTriggs()
  
  # The image resolution of the (cropped) images, which might change with the database
  image_resolution = (112, 92)

  #####################################################################
  ### Training

  # for Gabor graphs, no training is required.
  print("Creating Gabor graph machine")
  # create a machine that will produce Gabor graphs with inter-node distance (4,4)
  graph_extractor = bob.ip.gabor.Graph(first=(8,6), last=(image_resolution[0]-8, image_resolution[1]-6), step=(4,4))

  #####################################################################
  ### extract Gabor graph features for all model and probe images

  #####################################################################
  ### extract eigenface features of model and probe images

  model_ids = db.model_ids(groups = group)
  print("Extracting %d models" % len(model_ids))
  # generate models for each model ID
  models = {}
  for model_id in model_ids:
    # load enroll images for the current model ID
    enroll_images = load_images(db, db.enroll_files(protocol = protocol, groups = group, model_id = model_id), face_cropper, preprocessor)
    # extract features for all enroll images and store all of them
    models[model_id] = [extract_feature(enroll_image, graph_extractor) for enroll_image in enroll_images]

  probe_files = db.probe_files(protocol = protocol, groups = group)
  print("Extracting %d probes" % len(probe_files))
  probe_images = load_images(db, probe_files, face_cropper, preprocessor)
  # extract probe features and store them by probe ID (which is the File.id)
  probes = {}
  for i in range(len(probe_files)):
    probe_id = probe_files[i].id
    probes[probe_id] = extract_feature(probe_images[i], graph_extractor)

  #####################################################################
  ### compute scores, we here choose a simple Euclidean distance measure
  positive_scores = []
  negative_scores = []

  print("Computing scores")

  # iterate through models and probes and compute scores
  model_count = 1
  for model_id, model in models.items():
    # provide status information
    print("\rModel", model_count, "of", len(models), end='')
    sys.stdout.flush()
    model_count += 1

    # the client ID that is attached to the model
    model_client_id = db.get_client_id_from_model_id(model_id)
    # get the probe files, which should be compared with this model
    model_probe_files = db.probe_files(protocol = protocol, groups = group, model_id = model_id)
    for probe_file in model_probe_files:
      # get the according probe feature using the File.id of the probe file
      probe_feature = probes[probe_file.id]
      # compute local scores for each model gabor jet and each probe jet
      score = 0.
      for gabor_jet_index in range(len(probe_feature)):
        scores = []
        # compute the similarity to all model jets
        for model_feature_index in range(len(model)):
          scores.append(SIMILARITY_FUNCTION(model[model_feature_index][gabor_jet_index], probe_feature[gabor_jet_index]))
        # .. and take the most similar one
        score += max(scores)
      # the final score is computed as the average over all positions, taking the most similar model jet
      score /= len(probe_feature)

      # check if this is a positive score
      if model_client_id == probe_file.client_id:
        positive_scores.append(score)
      else:
        negative_scores.append(score)

  print("\nEvaluation")
  # convert list of scores to numpy arrays
  positives = numpy.array(positive_scores)
  negatives = numpy.array(negative_scores)

  # compute equal error rate
  threshold = bob.measure.eer_threshold(negatives, positives)
  FAR, FRR = bob.measure.farfrr(negatives, positives, threshold)

  print("Result: FAR", FAR, "and FRR", FRR, "at threshold", threshold)

  # plot ROC curve
  bob.measure.plot.roc(negatives, positives, CAR=True)
  pyplot.xlabel("False Acceptance Rate (\%)")
  pyplot.ylabel("Correct Acceptance Rate (\%)")
  pyplot.title("ROC Curve for Gabor phase based AT\&T Verification Experiment")
  pyplot.grid()
  pyplot.axis([0.1, 100, 0, 100]) #xmin, xmax, ymin, ymax

  # save plot to file
  pyplot.savefig("gabor_graph.pdf")
  print("Saved figure 'gabor_graph.pdf'")

  # show ROC curve.
  # enable it if you like. This will open a window and display the ROC curve
#  pyplot.show()

