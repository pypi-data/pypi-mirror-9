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
import bob.learn.linear
import bob.measure

import os, sys
import numpy, scipy.spatial
import matplotlib
matplotlib.use('pdf')
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
from matplotlib import pyplot

from .utils import atnt_database_directory, load_images


# The number of eigenfaces that should be kept
KEPT_EIGENFACES = 5

def train(training_images):
  """Trains the PCA module with the given list of training images"""
  # perform training using a PCA trainer
  pca_trainer = bob.learn.linear.PCATrainer()

  # create array set used for training
  # iterate through the training examples and linearize the images
  training_set = numpy.vstack([image.flatten() for image in training_images])

  # training the PCA returns a machine that can be used for projection
  pca_machine, eigen_values = pca_trainer.train(training_set)

  # limit the number of kept eigenfaces
  pca_machine.resize(pca_machine.shape[0], KEPT_EIGENFACES)

  return pca_machine


def extract_feature(image, pca_machine):
  """Projects the given list of images to the PCA subspace and returns the results"""
  # project and return the data after linearizing them
  return pca_machine(image.flatten())


DISTANCE_FUNCTION = scipy.spatial.distance.euclidean

def main():
  """This function will perform an eigenface test on the AT&T database"""

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


  #####################################################################
  ### Training

  # load all training images
  training_files = db.training_files(protocol = protocol)
  print("Loading %d training images" % len(training_files))
  training_images = load_images(db, training_files, face_cropper)

  print("Training PCA machine")
  pca_machine = train(training_images)

  #####################################################################
  ### extract eigenface features of model and probe images

  model_ids = db.model_ids(groups = group)
  print("Extracting %d models" % len(model_ids))
  # generate models for each model ID
  models = {}
  for model_id in model_ids:
    # load enroll images for the current model ID
    enroll_images = load_images(db, db.enroll_files(protocol = protocol, groups = group, model_id = model_id), face_cropper)
    # extract features for all enroll images and store all of them
    models[model_id] = [extract_feature(enroll_image, pca_machine) for enroll_image in enroll_images]

  probe_files = db.probe_files(protocol = protocol, groups = group)
  print("Extracting %d probes" % len(probe_files))
  probe_images = load_images(db, probe_files, face_cropper)
  # extract probe features and store them by probe ID (which is the File.id)
  probes = {}
  for i in range(len(probe_files)):
    probe_id = probe_files[i].id
    probes[probe_id] = extract_feature(probe_images[i], pca_machine)


  #####################################################################
  ### compute scores, we here choose a simple Euclidean distance measure
  positive_scores = []
  negative_scores = []

  print("Computing scores")

  # iterate through models and probes and compute scores
  for model_id, model in models.items():
    # the client ID that is attached to the model
    model_client_id = db.get_client_id_from_model_id(model_id)
    # get the probe files, which should be compared with this model
    model_probe_files = db.probe_files(protocol = protocol, groups = group, model_id = model_id)
    for probe_file in model_probe_files:
      # get the according probe feature using the File.id of the probe file
      probe_feature = probes[probe_file.id]
      # compute scores for all model features
      scores = [- DISTANCE_FUNCTION(model_feature, probe_feature) for model_feature in model]
      # the final score is the average distance
      # :: Note for the testers :: Try out other strategies!
      score = numpy.sum(scores)

      # check if this is a positive score
      if model_client_id == probe_file.client_id:
        positive_scores.append(score)
      else:
        negative_scores.append(score)

  print("Evaluation")
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
  pyplot.title("ROC Curve for Eigenface based AT\&T Verification Experiment")
  pyplot.grid()
  pyplot.axis([0.1, 100, 0, 100]) #xmin, xmax, ymin, ymax

  # save plot to file
  pyplot.savefig("eigenface.pdf")
  print("Saved figure 'eigenface.pdf'")

  # show ROC curve.
  # enable it if you like. This will open a window and display the ROC curve
#  pyplot.show()

