#!/usr/bin/env python
# Pedro Tome <Pedro.Tome@idiap.ch>
# Wed Aug 20 16:10:13 CET 2014
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

''' Performes the final evaluation of the results'''

import numpy, os, argparse
import bob.measure
import sys
from itertools import chain
import pickle
import string

def decryption_test_file(scoresfilename, diccionary_file):
  infile = open(scoresfilename, 'r')
  outfilename = scoresfilename+'_decrypted'
  outfile = open(outfilename, 'w')
  dicfile = open(diccionary_file, 'r')
    
  lines = infile.readlines()
  linesdic = dicfile.readlines()
  
  testdic = []
  realdic = []
  for i in range(0,len(linesdic)):
    words = linesdic[i].split() 
    testdic.append(words[0])
    realdic.append(words[1])
  
  for i in range(0,len(lines)):
    testfile = lines[i].split(' ')[0]
    if testfile.find('.')==-1:
      ind = testdic.index(testfile+'.png')
    else:
      ind = testdic.index(testfile)
    
    real_name = realdic[ind]
    score_value = lines[i].split(' ')[1][:-1] #[:-1] to remove the character '/n'
    outfile.write('%s %s\n' % (real_name, score_value))
   
  infile.close()
  outfile.close()
  dicfile.close()
  
  return outfilename

def command_line_options():
  """This function defines and parses the command line arguments that are accepted by this script."""
  # create argument parser
  parser = argparse.ArgumentParser()

  # add command lien arguments, with description and default values
  parser.add_argument('-d', '--devfile', required = True, help = 'The score file of the development set')
  parser.add_argument('-e', '--testfile', required=True, help = 'The score file of the evaluation set')
  parser.add_argument('-t', '--decryptionlist', required=False, help = 'The list of filename replacements for the evaluation files (required the first time)')
  parser.add_argument('-o', '--outfile', required=False, help = 'The output file')
  
  # parse and return the given command line arguments
  return parser.parse_args()


def main():
  
  # get command line arguments
  args = command_line_options()
 
  devfile = open(args.devfile, 'r')
  #import pdb; pdb.set_trace()   
  if args.decryptionlist != None:
    testfilename = decryption_test_file(args.testfile, args.decryptionlist)
  else:
    testfilename = args.testfile

  print testfilename
    
  testfile = open(testfilename, 'r')
  dev_pos = []; dev_neg = []
  test_pos = []; test_neg = []
  
  dev_lines = devfile.readlines()
  test_lines = testfile.readlines()
  
  for l in dev_lines:
    words = l.split()
    if string.find(words[0], 'spoof') != -1:
      dev_neg.append(float(words[1]))
    else:
      dev_pos.append(float(words[1]))
      
  for l in test_lines:
    words = l.split()
    if string.find(words[0], 'spoof') != -1:
      test_neg.append(float(words[1]))
    else:
      test_pos.append(float(words[1]))
      
      
  print 'Files in dev: %d positive and %d negative\n' % (len(dev_pos), len(dev_neg))
  print 'Files in test: %d positive and %d negative\n' % (len(test_pos), len(test_neg))
  
  thres = bob.measure.eer_threshold(dev_neg, dev_pos)
  thres = bob.measure.min_hter_threshold(dev_neg, dev_pos)
  dev_res = bob.measure.farfrr(dev_neg, dev_pos, thres)
  test_res = bob.measure.farfrr(test_neg, test_pos, thres)
  
  test_pos_correct = bob.measure.correctly_classified_positives(test_pos, thres)
  test_neg_correct = bob.measure.correctly_classified_negatives(test_neg, thres)

  print "Incorrectly classified positives: %d" % (test_pos_correct.size - sum(test_pos_correct))
  print "Incorrectly classified negatives: %d" % (test_neg_correct.size - sum(test_neg_correct))

  print 'thres: %f\n' % thres
  print 'DEV: FAR - %.2f%%; FRR - %.2f%%; HTER - %.2f%%\n' % (dev_res[0]*100, dev_res[1]*100, ((dev_res[0] + dev_res[1])/2)*100)
  print 'TEST: FAR - %.2f%%; FRR - %.2f%%; HTER - %.2f%%\n' % (test_res[0]*100, test_res[1]*100, ((test_res[0] + test_res[1])/2)*100)

  if args.outfile != None:
    outfile = open(args.outfile, 'a')
    outfile.write('Experiment result name: %s\n' % args.testfile)
    outfile.write('- dev file: %s\n' % args.devfile)
    outfile.write('- test file: %s\n\n' % args.testfile)
    
    outfile.write('thres: %f\n' % thres)
    outfile.write('DEV: FAR - %.2f%%; FRR - %.2f%%; HTER - %.2f%%\n' % (dev_res[0]*100, dev_res[1]*100, ((dev_res[0] + dev_res[1])/2)*100))
    outfile.write('TEST: FAR - %.2f%%; FRR - %.2f%%; HTER - %.2f%%\n\n' % (test_res[0]*100, test_res[1]*100, ((test_res[0] + test_res[1])/2)*100))
    outfile.close()
    
  devfile.close()
  testfile.close()
  
if __name__ == '__main__':
  main()
