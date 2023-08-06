#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Manuel Guenther <Manuel.Guenther@idiap.ch>

"""Parses through the list of resulting experiments and generates the plots for the paper."""

import argparse
import os
import sys
import facereclib
import math
import numpy

import bob.measure

import matplotlib
matplotlib.rc('text', usetex=True)
matplotlib.rc('font', size=20)
from matplotlib import pyplot


def command_line_options(command_line_arguments=None):

  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('--scores-directory', '-D', default="results", help = "The base directory of the scores; defaults to the default result directory of the FaceRecLib")
  parser.add_argument('--algorithms', '-a', nargs='+', default = ['eigenfaces', 'fisherfaces', 'gabor-jet', 'lgbphs', 'isv'], help = "The FR algorithms to evaluate")
  parser.add_argument('--experiments', '-e', nargs='+', default=['fixed', 'random', 'roc'], choices = ('fixed', 'random', 'roc'), help = "The experiment to evaluate")
  parser.add_argument('--ty-list', '-y', type=int, nargs='+', default = [-9, -7, -5, -3, -1, 0, 1, 3, 5, 7, 9], help = "The vertical shifts for the fixed experiment")
  parser.add_argument('--tx-list', '-x', type=int, nargs='+', default = [-9, -7, -5, -3, -1, 0, 1, 3, 5, 7, 9], help = "The horizontal shifts for the fixed experiment")
  parser.add_argument('--angle-list', '-t', type=int, nargs='+', default = [-20, -15, -10, -5, 0, 5, 10, 15, 20], help = "The orientations for the fixed experiment")
  parser.add_argument('--sy-list', '-Y', type=int, nargs='+', default = [9, 7, 5, 4, 3, 2, 1], help = "The vertical standard deviations for the random experiment")
  parser.add_argument('--sx-list', '-X', type=int, nargs='+', default = [1, 2, 3, 4, 5, 7, 9], help = "The horizontal standard deviations for the random experiment")
  parser.add_argument('--seed-list', '-s', type=int, nargs='+', default = [95359, 4464, 29721], help = "The seeds for the random experiment")
  parser.add_argument('--world-types', '-w', nargs='+', default = ['UT', 'Idiap', 'FaceVACS'], choices = ('FaceVACS', 'VeriLook', 'Idiap', 'UT'), help = "The types of annotations used for training and enrollment in the roc experiment")
  parser.add_argument('--probe-types', '-p', nargs='+', default = ['UT', 'Idiap', 'FaceVACS', 'VeriLook'], choices = ('FaceVACS', 'VeriLook', 'Idiap', 'UT'), help = "The types of annotations used for probing in the roc experiment")

  parser.add_argument('--plots-directory', '-O', default = 'plots', help = "Where to write the resulting csv and pdf files.")

  facereclib.utils.add_logger_command_line_option(parser)
  args = parser.parse_args(command_line_arguments)
  facereclib.utils.set_verbosity_level(args.verbose)

  return args


LABELS={
  'eigenfaces' : 'Eigenfaces',
  'fisherfaces' : 'Fisherfaces',
  'gabor-jet' : 'Gabor-Jet',
  'lgbphs' : 'LGBPHS',
  'isv' : 'ISV'
}

LIMITS = {
  'eigenfaces' : 0,
  'fisherfaces' : 0,
  'gabor-jet' : 60,
  'lgbphs' : 60,
  'isv' : 96
}

STYLES = {
  'FaceVACS' : {'linestyle' : '--', 'color' : 'black'},
  'VeriLook' : {'linestyle' : ':', 'color' : 'gray'},
  'Idiap'    : {'linestyle' : '-', 'color' : 'black'},
  'UT'       : {'linestyle' : '-', 'color' : 'gray'},
}


def compute_auc(far, frr):
  """Computes Area Under ROC from the given FAR and according FRR values"""
  car = 1.0 - frr
  auc = 0.0
  for i in range(1,len(far)):
    x1 = far[i-1]
    x2 = far[i]
    y1 = car[i-1]
    y2 = car[i]

    # compute area of trapezoid slice
    auc += math.fabs(x1-x2)*math.fabs((y1+y2)/2.)
  return auc


def get_fixed_score_file(y, x, a, algorithm, scores_dir):
  return os.path.join(scores_dir, 'fixed', 'ty%+d' % y, 'tx%+d' % x, 'a%+03d' % a, algorithm, 'scores', 'M', 'nonorm', 'scores-dev')

def get_random_score_file(y, x, s, algorithm, scores_dir):
  return os.path.join(scores_dir, 'random', 'sy%+d' % y, 'sx%+d' % x, 'seed%d' % (s+1), algorithm, 'scores', 'M', 'nonorm', 'scores-dev')

def get_roc_score_file(world, probe, algorithm, scores_dir):
  return os.path.join(scores_dir, 'annotations', world, algorithm, probe, 'M', 'nonorm', 'scores-dev')


def plot_fixed(args):
  hter_figure = pyplot.figure(figsize=(len(args.angle_list)*2+2,len(args.algorithms)*2+1))
  auc_figure = pyplot.figure(figsize=(len(args.angle_list)*2+2,len(args.algorithms)*2+1))

  plot_index = 1
  # evaluate the score files for the required algorithms
  for algorithm in args.algorithms:
    # get baseline scores
    baseline_score_file = get_fixed_score_file(0, 0, 0, algorithm, args.scores_directory)
    baseline_negatives, baseline_positives = bob.measure.load.split_four_column(baseline_score_file)
    threshold = bob.measure.min_hter_threshold(baseline_negatives, baseline_positives)

    # the fixed experiment
    hters = numpy.ones((len(args.angle_list), len(args.ty_list), len(args.tx_list)), numpy.float64)
    aucs = numpy.zeros((len(args.angle_list), len(args.ty_list), len(args.tx_list)), numpy.float64)

    with open(os.path.join(args.plots_directory, algorithm + '_fixed_hter_auc.csv'), 'w') as output_file:
      output_file.write('theta,tx,ty,hter,auc')
      # iterate though all the experimental results
      for y, ty in enumerate(args.ty_list):
        for x, tx in enumerate(args.tx_list):
          for a, angle in enumerate(args.angle_list):
            score_file = get_fixed_score_file(ty, tx, angle, algorithm, args.scores_directory)
            if os.path.exists(score_file):
              # compute HTER and AUC
              negatives, positives = bob.measure.load.split_four_column(score_file)
              far, frr = bob.measure.farfrr(negatives, positives, threshold)
              hter = (far + frr) / 2.

              roc = bob.measure.roc(negatives, positives, 500)
              auc = compute_auc(roc[0,:], roc[1,:])

              facereclib.utils.info("%s <ty = %+d, tx = %+d, angle = %+03d> HTER: %3.2f%%; AUC = %1.5f" % (algorithm, ty, tx, angle, hter*100., auc))
              output_file.write('\n%d,%d,%d,%.6f,%.6f' %(angle, tx, ty, hter, auc))

              hters[a,y,x] = hter
              aucs[a,y,x] = auc

            else:
              # score file does not (yet) exist
              facereclib.utils.info("%s <ty = %+d, tx = %+d, angle = %+2d> '%s' not found" % (algorithm, ty, tx, angle, score_file))

    # plot
    for a in range(len(args.angle_list)):
      pyplot.figure(hter_figure.number)
      hter_figure.add_subplot(len(args.algorithms), len(args.angle_list), plot_index)
      hter_img = pyplot.imshow(hters[a], cmap='gray', interpolation='none', vmin=0., vmax=.5, aspect='auto')

      pyplot.figure(auc_figure.number)
      auc_figure.add_subplot(len(args.algorithms), len(args.angle_list), plot_index)
      auc_img = pyplot.imshow(aucs[a], cmap='gray', interpolation='none', vmin=0.5, vmax=1., aspect='auto')
      plot_index += 1

  # finalize plot
  for figure, img, filename in ((hter_figure, hter_img, 'HTER_fixed.pdf'), (auc_figure, auc_img, 'AUC_fixed.pdf')):
    pyplot.figure(figure.number)

    # remove ticks
    index=1
    for a in range(len(args.algorithms)):
      for b in range(len(args.angle_list)):
        axis = pyplot.subplot(len(args.algorithms), len(args.angle_list), index)
        pyplot.xticks([])
        pyplot.yticks([])
        index += 1

    # add our own ticks
    yticks = [(i,str(y)) for i,y in enumerate(args.ty_list) if y in [-9, -5, 0, 5, 9]]
    for a in range(len(args.algorithms)):
      axis = pyplot.subplot(len(args.algorithms), len(args.angle_list), a * len(args.angle_list) + 1)
      pyplot.yticks([t[0] for t in yticks], [t[1] for t in yticks])
      axis.yaxis.tick_left()

    xticks = [(i,str(x)) for i,x in enumerate(args.tx_list) if x in [-9, -3, 0, 3, 9]]
    for a in range(len(args.angle_list)):
      axis = pyplot.subplot(len(args.algorithms), len(args.angle_list), len(args.angle_list) * (len(args.algorithms)-1) + a + 1)
      pyplot.xticks([t[0] for t in xticks], [t[1] for t in xticks])
      axis.xaxis.tick_bottom()

    # add labels
    for a in range(len(args.algorithms)):
      axis = pyplot.subplot(len(args.algorithms), len(args.angle_list), (a+1) * len(args.angle_list))
      pyplot.ylabel(LABELS[args.algorithms[a]], rotation=270, backgroundcolor='gray', labelpad=21)
      axis.yaxis.set_label_position('right')

    for a in range(len(args.angle_list)):
      axis = pyplot.subplot(len(args.algorithms), len(args.angle_list), a + 1)
      pyplot.xlabel("$\\theta = %+3d^\\circ$" % args.angle_list[a], backgroundcolor='gray', labelpad=7)
      axis.xaxis.set_label_position('top')

    # add plot legends and color bar
    axis = figure.add_subplot(111)
    axis.spines['top'].set_color('none')
    axis.spines['bottom'].set_color('none')
    axis.spines['left'].set_color('none')
    axis.spines['right'].set_color('none')
    axis.set_axis_bgcolor('none')
    axis.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
    axis.set_ylabel("Translation along y-axis")
    axis.set_xlabel("Translation along x-axis (in pixel units of $64\\times80$ normalized image)")

    # add color bar
    figure.subplots_adjust(left=0.05, right=0.9, top=0.95, bottom=0.08, wspace=0.05, hspace=0.05)
    cbar_ax = figure.add_axes([0.94, 0.3, 0.02, 0.4])
    figure.colorbar(img, cax=cbar_ax)

    # write both to the same PDF
    pyplot.savefig(os.path.join(args.plots_directory, filename))
    print ("Successfully generated plot %s" % os.path.join(args.plots_directory, filename))


def plot_random(args):
  hter_figure = pyplot.figure(figsize=(len(args.seed_list)*4+2,len(args.algorithms)*2+1))
  auc_figure = pyplot.figure(figsize=(len(args.seed_list)*4+2,len(args.algorithms)*2+1))

  plot_index = 1
  for algorithm in args.algorithms:
    # get baseline scores (the same as for the other plot)
    baseline_score_file = get_fixed_score_file(0, 0, 0, algorithm, args.scores_directory)
    baseline_negatives, baseline_positives = bob.measure.load.split_four_column(baseline_score_file)
    threshold = bob.measure.min_hter_threshold(baseline_negatives, baseline_positives)

    # collect results from other score files
    hters = numpy.ndarray((len(args.angle_list), len(args.sy_list), len(args.sx_list)), numpy.float64)
    aucs = numpy.ndarray((len(args.angle_list), len(args.sy_list), len(args.sx_list)), numpy.float64)
    hters[:,:,:] = 1.
    aucs[:,:,:] = 0.

    with open(os.path.join(args.plots_directory, algorithm + '_random_hter_auc.csv'), 'w') as output_file:
      output_file.write('sigma_x,sigma_y,random_seed,hter,auc')
      # iterate though all the experimental results
      for y, sy in enumerate(args.sy_list):
        for x, sx in enumerate(args.sx_list):
          for s, seed in enumerate(args.seed_list):
            score_file = get_random_score_file(sy, sx, s, algorithm, args.scores_directory)
            if os.path.exists(score_file):
              # compute HTER and AUC
              negatives, positives = bob.measure.load.split_four_column(score_file)
              far, frr = bob.measure.farfrr(negatives, positives, threshold)
              hter = (far + frr) / 2.

              roc = bob.measure.roc(negatives, positives, 500)
              auc = compute_auc(roc[0,:], roc[1,:])

              facereclib.utils.info("%s <sy = %+d, sx = %+d, seed = %d> HTER: %3.2f%%; AUC = %1.5f" % (algorithm, sy, sx, seed, hter*100., auc))
              output_file.write('\n%d,%d,%d,%.6f,%.6f' %(sx, sy, seed, hter, auc))

              hters[s,y,x] = hter
              aucs[s,y,x] = auc

            else:
              # score file does not (yet) exist
              facereclib.utils.info("%s <sy = %+d, sx = %+d, seed = %d> '%s' not found" % (algorithm, sy, sx, seed, score_file))

    # plot
    for s in range(len(args.seed_list)):
      pyplot.figure(hter_figure.number)
      hter_figure.add_subplot(len(args.algorithms), len(args.seed_list), plot_index)
      hter_img = pyplot.imshow(hters[s], cmap='gray', interpolation='none', vmin=0., vmax=.5, aspect='auto')

      pyplot.figure(auc_figure.number)
      auc_figure.add_subplot(len(args.algorithms), len(args.seed_list), plot_index)
      auc_img = pyplot.imshow(aucs[s], cmap='gray', interpolation='none', vmin=0.5, vmax=1., aspect='auto')
      plot_index += 1


  # finalize plot
  for figure, img, filename in ((hter_figure, hter_img, 'HTER_random.pdf'), (auc_figure, auc_img, 'AUC_random.pdf')):
    pyplot.figure(figure.number)

    # remove ticks
    index=1
    for a in range(len(args.algorithms)):
      for b in range(len(args.seed_list)):
        axis = pyplot.subplot(len(args.algorithms), len(args.seed_list), index)
        pyplot.xticks([])
        pyplot.yticks([])
        index += 1

    # add our own ticks
    yticks = [(i,str(y)) for i,y in enumerate(args.sy_list) if y in [1, 3, 5, 9]]
    for a in range(len(args.algorithms)):
      axis = pyplot.subplot(len(args.algorithms), len(args.seed_list), a * len(args.seed_list) + 1)
      pyplot.yticks([t[0] for t in yticks], [t[1] for t in yticks])
      axis.yaxis.tick_left()

    xticks = [(i,str(x)) for i,x in enumerate(args.sx_list) if x in [1, 3, 5, 9]]
    for a in range(len(args.seed_list)):
      axis = pyplot.subplot(len(args.algorithms), len(args.seed_list), len(args.seed_list) * (len(args.algorithms)-1) + a + 1)
      pyplot.xticks([t[0] for t in xticks], [t[1] for t in xticks])
      axis.xaxis.tick_bottom()

    # add labels
    for a in range(len(args.algorithms)):
      axis = pyplot.subplot(len(args.algorithms), len(args.seed_list), (a+1) * len(args.seed_list))
      pyplot.ylabel(LABELS[args.algorithms[a]], rotation=270, backgroundcolor='gray', labelpad=21)
      axis.yaxis.set_label_position('right')

    for a in range(len(args.seed_list)):
      axis = pyplot.subplot(len(args.algorithms), len(args.seed_list), a + 1)
      pyplot.xlabel("random seed: %d" % args.seed_list[a], backgroundcolor='gray', labelpad=7)
      axis.xaxis.set_label_position('top')

    # add plot legends and color bar
    axis = figure.add_subplot(111)
    axis.spines['top'].set_color('none')
    axis.spines['bottom'].set_color('none')
    axis.spines['left'].set_color('none')
    axis.spines['right'].set_color('none')
    axis.set_axis_bgcolor('none')
    axis.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
    axis.set_ylabel("$\\sigma_y$ Standard deviation along y-axis")
    axis.set_xlabel("$\\sigma_x$ Standard deviation along x-axis (in pixel units of $64\\times80$ normalized image)")

    # add color bar
    figure.subplots_adjust(left=0.08, right=0.87, top=0.95, bottom=0.08, wspace=0.03, hspace=0.05)
    cbar_ax = figure.add_axes([0.93, 0.3, 0.02, 0.4])
    figure.colorbar(img, cax=cbar_ax)

    pyplot.savefig(os.path.join(args.plots_directory, filename))
    print ("Successfully generated plot %s" % os.path.join(args.plots_directory, filename))


def plot_roc(args):
  # generate plots
  figure = pyplot.figure(figsize=(len(args.world_types)*4+1,len(args.algorithms)*3+1))

  fars = [math.pow(10., i * 0.05) for i in range(-80,0)] + [1.]
  plot_index = 1
  with open(os.path.join(args.plots_directory, 'roc.csv'), 'w') as output_file:
    # write header
    output_file.write("world_gallery,dev_probe,algname,far,tpr")
    for algorithm in args.algorithms:
      for world in args.world_types:
        rocs = []
        for probe in args.probe_types:
          # read the score file
          score_file = get_roc_score_file(world, probe, algorithm, args.scores_directory)
          if os.path.exists(score_file):
            # compute ROC
            negatives, positives = bob.measure.load.split_four_column(score_file)
            roc = bob.measure.roc_for_far(negatives, positives, fars)

            # write to output file
            for i in range(len(fars)) :
              output_file.write( '\n%s,%s,%s,%.6f,%.6f' %(world, probe, algorithm, roc[0,i], 1.0-roc[1,i]) )


            facereclib.utils.info("%s <world = %s, probe = %s> CAR@FAR 0.1%%: %3.2f%%" % (algorithm, world, probe, 100. - roc[1,20] * 100.))
            rocs.append(roc[1,:])

          else:
            # score file does not (yet) exist
            facereclib.utils.warn("%s <world = %s, probe = %s> '%s' not found" % (algorithm, world, probe, score_file))
            rocs.append(None)

        # plot
        pyplot.figure(figure.number)
        figure.add_subplot(len(args.algorithms), len(args.world_types), plot_index)
        for p, probe in enumerate(args.probe_types):
          if rocs[p] is not None:
            pyplot.semilogx([100.0*f for f in fars], [100. - 100.0*f for f in rocs[p]], label=probe, linewidth=3 if probe == world else 2, **STYLES[probe])
          pyplot.ylim(LIMITS[algorithm], 100)

          if plot_index == 1:
            pyplot.legend(title = "Eye Annotations For Probe", bbox_to_anchor=(0., 1.15, 1., .1), loc=3, ncol=4, )

        plot_index += 1


  # finalize plot
  pyplot.figure(figure.number)

  xticks = [0.1, 1, 10, 100]
  def yticks(alg):
    return range(LIMITS[alg], 101, (100-LIMITS[alg])/4)

  # remove ticks
  index=1
  for a in range(len(args.algorithms)):
    for w in range(len(args.world_types)):
      axis = pyplot.subplot(len(args.algorithms), len(args.world_types), index)
      pyplot.xticks(xticks, [])
      pyplot.yticks(yticks(args.algorithms[a]), [])
      pyplot.grid()
      index += 1

  # add ticks
  for a in range(len(args.algorithms)):
    axis = pyplot.subplot(len(args.algorithms), len(args.world_types), a * len(args.world_types) + 1)
    pyplot.yticks(yticks(args.algorithms[a]), ["%s\%%" % str(y) for y in yticks(args.algorithms[a])])
    axis.yaxis.tick_left()

  for a in range(len(args.world_types)):
    axis = pyplot.subplot(len(args.algorithms), len(args.world_types), len(args.world_types) * (len(args.algorithms)-1) + a + 1)
    pyplot.xticks(xticks, ["%s\%%" % str(x) for x in xticks])
    axis.xaxis.tick_bottom()

  # add labels
  for a in range(len(args.algorithms)):
    axis = pyplot.subplot(len(args.algorithms), len(args.world_types), (a+1) * len(args.world_types))
    pyplot.ylabel(LABELS[args.algorithms[a]], rotation=270, backgroundcolor='gray', labelpad=21)
    axis.yaxis.set_label_position('right')

  for a in range(len(args.world_types)):
    axis = pyplot.subplot(len(args.algorithms), len(args.world_types), a + 1)
    pyplot.xlabel("Train+Enroll: %s" % args.world_types[a], backgroundcolor='gray', labelpad=7)
    axis.xaxis.set_label_position('top')

  # add plot legends and color bar
  axis = figure.add_subplot(111)
  axis.spines['top'].set_color('none')
  axis.spines['bottom'].set_color('none')
  axis.spines['left'].set_color('none')
  axis.spines['right'].set_color('none')
  axis.set_axis_bgcolor('none')
  axis.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
  axis.set_xlabel("False Acceptence Rate in \%%", labelpad = 20)
  axis.set_ylabel("Correct Acceptance Rate in \%%", labelpad = 30)

  figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.07, wspace=0.2, hspace=0.3)

  pyplot.savefig(os.path.join(args.plots_directory, "ROCs.pdf"))
  print ("Successfully generated plot %s" % os.path.join(args.plots_directory, "ROCs.pdf"))


def main():
  args = command_line_options()

  # create output directory
  bob.io.base.create_directories_safe(args.plots_directory)

  # generate plots
  if 'fixed' in args.experiments:
    plot_fixed(args)

  if 'random' in args.experiments:
    plot_random(args)

  if 'roc' in args.experiments:
    plot_roc(args)
