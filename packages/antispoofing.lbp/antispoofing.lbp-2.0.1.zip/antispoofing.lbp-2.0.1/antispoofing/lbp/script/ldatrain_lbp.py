#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Thu Feb  9 14:52:09 CET 2012

"""This script makes an LDA classification of data into two categories: real accesses and spoofing attacks. There is an option for normalizing and dimensionality reduction of the data prior to the LDA classification.
After the LDA, each data sample gets a score. Firstly, the EER threshold on the development set is calculated. The, according to this EER, the FAR, FRR and HTER for the test and development set are calculated. The script outputs a text file with the performance results.
The details about the procedure are described in the paper: "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing" - Chingovska, Anjos & Marcel; BIOSIG 2012
"""

import os, sys
import argparse
import bob.io.base
import bob.measure
import numpy

from antispoofing.utils.db import *
from antispoofing.utils.ml import *

def main():

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

  INPUT_DIR = os.path.join(basedir, 'lbp_features')
  OUTPUT_DIR = os.path.join(basedir, 'res')

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-v', '--input-dir', metavar='DIR', type=str, dest='inputdir', default=INPUT_DIR, help='Base directory containing the scores to be loaded')
  parser.add_argument('-d', '--output-dir', metavar='DIR', type=str, dest='outputdir', default=OUTPUT_DIR, help='Base directory that will be used to save the results.')
  parser.add_argument('-n', '--normalize', action='store_true', dest='normalize', default=False, help='If True, will do zero mean unit variance normalization on the data before creating the LDA machine')
  parser.add_argument('-r', '--pca_reduction', action='store_true', dest='pca_reduction', default=False, help='If set, PCA dimensionality reduction will be performed to the data before doing LDA')
  parser.add_argument('-e', '--energy', type=str, dest="energy", default='0.99', help='The energy which needs to be preserved after the dimensionality reduction if PCA is performed prior to LDA')
  parser.add_argument('-s', '--score', dest='score', action='store_true', default=False, help='If set, the final classification scores of all the frames will be dumped in a file')

  from ..helpers import score_manipulate as sm

  #######
  # Database especific configuration
  #######
  Database.create_parser(parser, implements_any_of='video')

  args = parser.parse_args()

  if not os.path.exists(args.inputdir):
    parser.error("input directory does not exist")

  if not os.path.exists(args.outputdir): # if the output directory doesn't exist, create it
    bob.io.base.create_directories_safe(args.outputdir)

  energy = float(args.energy)

  print "Loading input files..."
  database = args.cls(args)
  
  process_train_real, process_train_attack = database.get_train_data()
  process_devel_real, process_devel_attack = database.get_devel_data()
  process_test_real, process_test_attack = database.get_test_data()
  

  # create the full datasets from the file data
  train_real = sm.create_full_dataset(args.inputdir, process_train_real); train_attack = sm.create_full_dataset(args.inputdir, process_train_attack); 
  devel_real = sm.create_full_dataset(args.inputdir, process_devel_real); devel_attack = sm.create_full_dataset(args.inputdir, process_devel_attack); 
  test_real = sm.create_full_dataset(args.inputdir, process_test_real); test_attack = sm.create_full_dataset(args.inputdir, process_test_attack); 
  
  if args.normalize:  # zero mean unit variance data normalziation
    print "Applying standard normalization..."
    #import ipdb; ipdb.set_trace()
    mean, std = norm.calc_mean_std(train_real, train_attack)
    train_real = norm.zeromean_unitvar_norm(train_real, mean, std); train_attack = norm.zeromean_unitvar_norm(train_attack, mean, std)
    devel_real = norm.zeromean_unitvar_norm(devel_real, mean, std); devel_attack = norm.zeromean_unitvar_norm(devel_attack, mean, std)
    test_real = norm.zeromean_unitvar_norm(test_real, mean, std); test_attack = norm.zeromean_unitvar_norm(test_attack, mean, std)

  if args.pca_reduction: # PCA dimensionality reduction of the data
    print "Running PCA reduction..."
    train=numpy.append(train_real, train_attack, axis=0)
    pca_machine = pca.make_pca(train, energy) # performing PCA
    train_real = pca.pcareduce(pca_machine, train_real); train_attack = pca.pcareduce(pca_machine, train_attack)
    devel_real = pca.pcareduce(pca_machine, devel_real); devel_attack = pca.pcareduce(pca_machine, devel_attack)
    test_real = pca.pcareduce(pca_machine, test_real); test_attack = pca.pcareduce(pca_machine, test_attack)

  print "Training LDA machine..."
  lda_machine = lda.make_lda((train_real, train_attack)) # training the LDA
  lda_machine.shape = (lda_machine.shape[0], 1) #only use first component!
  
  print "Computing devel and test scores..."
  devel_real_out = lda.get_scores(lda_machine, devel_real)
  devel_attack_out = lda.get_scores(lda_machine, devel_attack)
  test_real_out = lda.get_scores(lda_machine, test_real)
  test_attack_out = lda.get_scores(lda_machine, test_attack)
  train_real_out = lda.get_scores(lda_machine, train_real)
  train_attack_out = lda.get_scores(lda_machine, train_attack)

  # it is expected that the scores of the real accesses are always higher then the scores of the attacks. Therefore, a check is first made, if the average of the scores of real accesses is smaller then the average of the scores of the attacks, all the scores are inverted by multiplying with -1.
  if numpy.mean(devel_real_out) < numpy.mean(devel_attack_out):
    devel_real_out = devel_real_out * -1; devel_attack_out = devel_attack_out * -1
    test_real_out = test_real_out * -1; test_attack_out = test_attack_out * -1
    train_real_out = train_real_out * -1; train_attack_out = train_attack_out * -1     

  if args.score: # save the scores in a file
    score_dir = os.path.join(args.outputdir, 'scores') # output directory for the socre files
    sm.map_scores(args.inputdir, score_dir, process_devel_real, numpy.reshape(devel_real_out, [len(devel_real_out), 1])) 
    sm.map_scores(args.inputdir, score_dir, process_devel_attack, numpy.reshape(devel_attack_out, [len(devel_attack_out), 1]))
    sm.map_scores(args.inputdir, score_dir, process_test_real, numpy.reshape(test_real_out, [len(test_real_out), 1]))
    sm.map_scores(args.inputdir, score_dir, process_test_attack, numpy.reshape(test_attack_out, [len(test_attack_out), 1]))
    sm.map_scores(args.inputdir, score_dir, process_train_real, numpy.reshape(train_real_out, [len(train_real_out), 1]))
    sm.map_scores(args.inputdir, score_dir, process_train_attack, numpy.reshape(train_attack_out, [len(train_attack_out), 1]))
   
  # calculation of the error rates
  thres = bob.measure.eer_threshold(devel_attack_out.flatten(), devel_real_out.flatten())
  dev_far, dev_frr = bob.measure.farfrr(devel_attack_out.flatten(), devel_real_out.flatten(), thres)
  test_far, test_frr = bob.measure.farfrr(test_attack_out.flatten(), test_real_out.flatten(), thres)
  
  # writing results to a file
  tbl = []
  tbl.append(" ")
  if args.pca_reduction:
    tbl.append("EER @devel - energy kept after PCA = %.2f" % (energy))
  tbl.append(" threshold: %.4f" % thres)
  tbl.append(" dev:  FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (100*dev_far, int(round(dev_far*len(devel_attack))), len(devel_attack), 
       100*dev_frr, int(round(dev_frr*len(devel_real))), len(devel_real),
       50*(dev_far+dev_frr)))
  tbl.append(" test: FAR %.2f%% (%d / %d) | FRR %.2f%% (%d / %d) | HTER %.2f%% " % \
      (100*test_far, int(round(test_far*len(test_attack))), len(test_attack),
       100*test_frr, int(round(test_frr*len(test_real))), len(test_real),
       50*(test_far+test_frr)))
  txt = ''.join([k+'\n' for k in tbl])
  print txt

  # write the results to a file 
  tf = open(os.path.join(args.outputdir, 'perf_table.txt'), 'w')
  tf.write(txt)
 
if __name__ == '__main__':
  main()
