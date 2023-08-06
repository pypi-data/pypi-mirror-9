#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date: Mon Jul 22 19:56:11 CEST 2013
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

import os
import bob.io.base
import bob.ip.color
import numpy

def atnt_database_directory(atnt_user_directory = None):
  #Checks, where the AT&T database is located and downloads it on need
  if atnt_user_directory is not None:
    # a user directory is specified
    atnt_default_directory = atnt_user_directory
  elif 'ATNT_DATABASE_DIRECTORY' in os.environ:
    # the environment variable is set
    atnt_default_directory = os.environ['ATNT_DATABASE_DIRECTORY']
  else:
    atnt_default_directory = 'Database'

  # Check if the database is already in the specified directory
  if os.path.isdir(atnt_default_directory) and set(['s%d'%s for s in range(1,41)]).issubset(os.listdir(atnt_default_directory)):
    return atnt_default_directory

  # ... download the database ...

  # create directory
  if not os.path.exists(atnt_default_directory):
    os.mkdir(atnt_default_directory)

  # setup
  import sys, tempfile
  if sys.version_info[0] <= 2:
    import urllib2 as urllib
  else:
    import urllib.request as urllib

  db_url = 'http://www.cl.cam.ac.uk/Research/DTG/attarchive/pub/data/att_faces.zip'
  import logging
  logger = logging.getLogger('bob')
  logger.warn("Downloading the AT&T database from '%s' to '%s' ..." % (db_url, atnt_default_directory))

  # download
  url = urllib.urlopen(db_url)
  local_zip_file = tempfile.mkstemp(prefix='atnt_db_', suffix='.zip')[1]
  dfile = open(local_zip_file, 'wb')
  dfile.write(url.read())
  dfile.close()

  # unzip
  import zipfile
  zip = zipfile.ZipFile(local_zip_file)
  zip.extractall(atnt_default_directory)
  zip.close()

  # remove temporary zip file
  os.remove(local_zip_file)

  return atnt_default_directory


def load_images(database, files, face_cropper = None, preprocessor = None):
  """Loads the original images for the given list of File objects.
  
  Keyword Parameters:
  
  database : :py:class:`bob.db.verification.utils.Database` or derived from it
    The database interface to query.
    
  files : [:py:class:`bob.db.verification.utils.File`] or derived from it
    A list of ``File`` objects for which the images should be loaded.
    
  face_cropper : :py:class:`bob.ip.base.FaceEyesNorm` or ``None``
    If a face cropper is given, the face will be cropped using the eye annotations of the database.
    
  preprocessor : ``function``, ``object`` or ``None``
    If a preprocessor is given, it will be applied to the (cropped) faces.
  """
  file_names = database.original_file_names(files)
  # iterate through the list of file names and load images
  images = [bob.io.base.load(file_name) for file_name in file_names]
  # convert color to gray images if necessary
  gray_images = []
  for image in images:
    gray_image = bob.ip.color.rgb_to_gray(image).astype(numpy.float64) if len(image.shape) == 3 else image
    gray_images.append(gray_image.astype(numpy.float64))

  if face_cropper is not None:
    cropped_images = []
    for i in range(len(files)):
      # get the annotations for the files
      annotations = database.annotations(files[i])
      assert 'reye' in annotations and 'leye' in annotations
      cropped_images.append(face_cropper(gray_images[i], right_eye = annotations['reye'], left_eye = annotations['leye']))
  else:
    cropped_images = gray_images

  if preprocessor is not None:
    preprocessed_images = [preprocessor(i) for i in cropped_images]
  else:
    preprocessed_images = cropped_images

  return preprocessed_images

