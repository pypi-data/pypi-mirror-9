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
import bob.learn.em
import bob.measure

import os, sys
import numpy
import matplotlib
matplotlib.use('pdf')
# enable LaTeX interpreter
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', family='serif')
matplotlib.rc('lines', linewidth = 4)
from matplotlib import pyplot

from .utils import atnt_database_directory, load_images


# setup the logging system (used by C++ functionality in Bob)
import logging
formatter = logging.Formatter("%(name)s@%(asctime)s -- %(levelname)s: %(message)s")
logger = logging.getLogger("bob")
for handler in logger.handlers:
  handler.setFormatter(formatter)
logger.setLevel(logging.INFO)


# Parameters of the DCT extraction
DCT_BLOCK_SIZE = 12
DCT_BLOCK_OVERLAP = 11
NUMBER_OF_DCT_COMPONENTS = 45

# create a DCT block extractor model
dct_extractor = bob.ip.base.DCTFeatures(NUMBER_OF_DCT_COMPONENTS, (DCT_BLOCK_SIZE, DCT_BLOCK_SIZE), (DCT_BLOCK_OVERLAP, DCT_BLOCK_OVERLAP))

def extract_feature(image):
  """Extracts the DCT features for the given image"""

  # extract DCT blocks
  return dct_extractor(image)



# Parameters of the UBM/GMM module training
NUMBER_OF_GAUSSIANS = 100

def train(training_features, number_of_gaussians = NUMBER_OF_GAUSSIANS):
  """Trains the UBM/GMM module with the given set of training DCT features"""

  # create array set used for training
  training_set = numpy.vstack(training_features)

  input_size = training_set.shape[1]
  # create the KMeans and UBM machine
  kmeans = bob.learn.em.KMeansMachine(number_of_gaussians, input_size)
  ubm = bob.learn.em.GMMMachine(number_of_gaussians, input_size)

  # create the KMeansTrainer
  kmeans_trainer = bob.learn.em.KMeansTrainer()

  # train using the KMeansTrainer
  bob.learn.em.train(kmeans_trainer, kmeans, training_set, max_iterations=10, convergence_threshold=0.001)

  [variances, weights] = kmeans.get_variances_and_weights_for_each_cluster(training_set)
  means = kmeans.means

  # initialize the GMM
  ubm.means = means
  ubm.variances = variances
  ubm.weights = weights

  # train the GMM
  trainer = bob.learn.em.ML_GMMTrainer()
  bob.learn.em.train(trainer, ubm, training_set, max_iterations=10, convergence_threshold=0.001)
  return ubm


def enroll(model_features, ubm, gmm_trainer, max_iterations=1):
  """Enrolls the GMM model for the given model features (which should stem from the same identity)"""
  # create array set used for enrolling
  enroll_set = numpy.vstack(model_features)
  # create a GMM from the UBM
  gmm = bob.learn.em.GMMMachine(ubm)

  # train the GMM
  bob.learn.em.train(gmm_trainer, gmm, enroll_set,max_iterations=max_iterations)

  # return the resulting gmm
  return gmm


def stats(probe_feature, ubm):
  """Computes the UBM Statistics for the given feature vector"""
  # compute the UBM stats for the given probe feature
  probe_feature = numpy.vstack([probe_feature])

  # Accumulate statistics
  gmm_stats = bob.learn.em.GMMStats(ubm.shape[0], ubm.shape[1])
  gmm_stats.init()
  ubm.acc_statistics(probe_feature, gmm_stats)

  return gmm_stats


def main():
  """This function will perform an a DCT block extraction and a UBM/GMM modeling test on the AT&T database"""

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

  #####################################################################
  ### UBM Training
  # load all training images
  training_files = db.training_files(protocol = protocol)
  training_files = training_files
  print("Loading %d training images" % len(training_files))
  training_images = load_images(db, training_files, face_cropper, preprocessor)

  print("Extracting %d training features" % len(training_files))
  training_features = [extract_feature(image) for image in training_images]

  print("Training UBM model")
  ubm = train(training_features)

  #####################################################################
  ### GMM model enrollment
  gmm_trainer = bob.learn.em.MAP_GMMTrainer(ubm, relevance_factor=4.0, update_means=True)


  # enroll a GMM model for each model identity (i.e., each client)
  model_ids = db.model_ids(groups = group)
  model_ids = model_ids
  print("Enrolling %d GMM models" % len(model_ids))
  # generate models for each model ID
  models = {}
  for model_id in model_ids:
    # load enroll images for the current model ID
    enroll_images = load_images(db, db.enroll_files(protocol = protocol, groups = group, model_id = model_id), face_cropper, preprocessor)
    # extract features
    enroll_features = [extract_feature(enroll_image) for enroll_image in enroll_images]
    models[model_id] = enroll(enroll_features, ubm, gmm_trainer)


  #####################################################################
  ### probe stats
  probe_files = db.probe_files(protocol = protocol, groups = group)
  print("Computing %d probe statistics" % len(probe_files))
  probe_images = load_images(db, probe_files, face_cropper, preprocessor)
  # extract probe features and store them by probe ID (which is the File.id)
  probes = {}
  for i in range(len(probe_files)):
    # provide status information
    print("\rProbe", i+1, "of", len(probe_files), end='')
    sys.stdout.flush()

    probe_id = probe_files[i].id
    probe_feature = extract_feature(probe_images[i])
    probes[probe_id] = stats(probe_feature, ubm)

  #####################################################################
  ### compute scores, using the linear_scoring function
  positive_scores = []
  negative_scores = []

  print("\nComputing scores")
  distance_function = bob.learn.em.linear_scoring

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
      # get the according probe statistics using the File.id of the probe file
      probe_stats = probes[probe_file.id]
      # compute score
      score = distance_function([model], ubm, [probe_stats])[0,0]

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
  pyplot.title("ROC Curve for UBM/GMM based AT\&T Verification Experiment")
  pyplot.grid()
  pyplot.axis([0.1, 100, 0, 100]) #xmin, xmax, ymin, ymax

  # save plot to file
  pyplot.savefig("dct_ubm.pdf")
  print("Saved figure 'dct_ubm.pdf'")

  # show ROC curve.
  # enable it if you like. This will open a window and display the ROC curve
#  pyplot.show()

