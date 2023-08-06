#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pedro Tome <pedro.tome@idiap.ch>
# @date: Tue 2 Nov 18:18:08 2014 CEST
#
# Copyright (C) 2014 Idiap Research Institute, Martigny, Switzerland
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

import argparse
import bob.ip.base
import bob.core
import bob.sp
import bob.io.base
import bob.io.image

import numpy
import os, sys
import string
import math


def spoofingFFT(image):
  #Histogram equalization to normalize
  imageEnhance = numpy.zeros(image.shape)
  imageEnhance = imageEnhance.astype(numpy.uint8)
    
  bob.ip.base.histogram_equalization(image, imageEnhance)   

  #Convert image to doubles
  image_new = bob.core.convert(imageEnhance,numpy.float64,(0,1),(0,255))    
  
  img_h, img_w = image_new.shape
  
  # Determine lower half starting point vertically
  if numpy.mod(img_h,2) == 0:
      half_img_h = img_h/2 + 1
  else:
      half_img_h = numpy.ceil(img_h/2)
  
  # Determine lower half starting point horizontally
  if numpy.mod(img_w,2) == 0:
      half_img_w = img_w/2 + 1
  else:
      half_img_w = numpy.ceil(img_w/2)
    
  Ffreq = bob.sp.fftshift(bob.sp.fft(image_new.astype(numpy.complex128))/math.sqrt(img_h*img_w))    
  F = numpy.log10(abs(Ffreq)**2)
  
  offset_window = 10
  img_half_section_v = F[:,(half_img_w-offset_window):(half_img_w+offset_window)]

  pv = numpy.mean(img_half_section_v,1)
        
  dBthreshold = -3        
  Bwv = numpy.size(numpy.where(pv>dBthreshold))*1.0 / img_h

  return Bwv



def database_get_data(inputDir, dataset, proto):
  
  data = os.path.join(inputDir, proto, dataset)   
  dataObjects = []    
  if dataset == 'test':
    datapathin = os.path.join(data)     
    filenames = [l for l in os.listdir(datapathin)]    
    for f in filenames:
      dataObjects.append(os.path.join(proto,dataset,f))
  
  else:
    datapathin = os.path.join(data, 'real')     
    ldirs = [l for l in os.listdir(datapathin) if os.path.isdir(datapathin+'/'+l)]    
    for user in ldirs:
      filenames = [l for l in os.listdir(datapathin+'/'+user)]
      for f in filenames:
        #RealObjects.append(datapathin+'/'+user+'/'+f)
        dataObjects.append(os.path.join(proto,dataset,'real',user,f))
    
    datapathin = os.path.join(data, 'spoof')     
    ldirs = [l for l in os.listdir(datapathin) if os.path.isdir(datapathin+'/'+l)]    
    for user in ldirs:
      filenames = [l for l in os.listdir(datapathin+'/'+user)]
      for f in filenames:
        #AttackObjects.append(datapathin+'/'+user+'/'+f)
        dataObjects.append(os.path.join(proto,dataset,'spoof',user,f))
          
  
  return dataObjects 


def main():
 
  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'database')
    
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-i', '--input-dir', type=str, dest='inputDir', default=INPUT_DIR, help='Base directory of the database (defaults to "%(default)s")')
  parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Increases this script verbosity')

  args = parser.parse_args()

  if args.verbose == True: verbose  = 2 
  else: verbose  = 0

  inputDir = args.inputDir
  if os.path.isdir('submissions')==False: 
    os.mkdir('submissions')
    

  ########################
  #Querying the database
  ########################
  #trainObjects = database_get_data(inputDir,'train', 'full')
  #devObjects = database_get_data(inputDir,'dev', 'full')
  #testObjects = database_get_data(inputDir,'test', 'full')


  ########################
  #Development set results
  ########################
  print "Development set: full protocol."
  devObjects = database_get_data(inputDir,'dev', 'full')
  
  
  fid = open("submissions/Baseline_dev_full.txt","w")
  for sample in devObjects:
    image = bob.io.base.load(os.path.join(inputDir, sample))
    score = spoofingFFT(image)
    output = sample[sample.find('/')+1:] + ' ' + str(score) +'\n'
    fid.write(output)
    if verbose>1: print sample, score
  fid.close()
  
  print "Development set: cropped protocol."
  devObjects = database_get_data(inputDir,'dev', 'cropped')
  fid = open("submissions/Baseline_dev_cropped.txt","w")
  for sample in devObjects:
    image = bob.io.base.load(os.path.join(inputDir, sample))
    score = spoofingFFT(image)
    output = sample[sample.find('/')+1:] + ' ' + str(score) +'\n'
    fid.write(output)
    if verbose>1: print sample, score
  fid.close()


  ########################
  #Test set results
  ########################
  print "Test set: full protocol."
  testObjects = database_get_data(inputDir,'test', 'full')
  fid = open("submissions/Baseline_test_full.txt","w")
  for sample in testObjects:
    image = bob.io.base.load(os.path.join(inputDir, sample))
    score = spoofingFFT(image)
    output = sample[sample.find('/',sample.find('/')+1)+1:] + ' ' + str(score) +'\n'
    fid.write(output)
    if verbose>1: print sample, score
  fid.close()
  
  print "Test set: cropped protocol."
  testObjects = database_get_data(inputDir,'test', 'cropped')
  fid = open("submissions/Baseline_test_cropped.txt","w")
  for sample in testObjects:
    image = bob.io.base.load(os.path.join(inputDir, sample))
    score = spoofingFFT(image)
    output = sample[sample.find('/',sample.find('/')+1)+1:] + ' ' + str(score) +'\n'
    fid.write(output)
    if verbose>1: print sample, score
  fid.close()
  