#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue Jul 19 11:50:08 2011 +0200
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

"""This example shows how to use the Iris Flower (Fisher's) Dataset to create
3-class classifier based on Neural Networks (Multi-Layer Perceptrons - MLP).
"""

from __future__ import print_function

import os
import sys
import bob.io
import bob.db
import bob.measure
import bob.learn.mlp
import bob.learn.activation
import optparse
import tempfile #for package tests
import numpy

def choose_matplotlib_iteractive_backend():
  """Little logic to get interactive plotting right on OSX and Linux"""

  import platform
  import matplotlib
  if platform.system().lower() == 'darwin': #we are on OSX
    matplotlib.use('macosx')
  else:
    matplotlib.use('GTKAgg')

def generate_testdata(data, target):
  """Concatenates all data in a single 2D array. Examples are encoded row-wise,
  features, column-wise. The same for the targets.
  """
  destsize = 0
  for d in data: destsize += len(d)
  retval = numpy.zeros((destsize, 4), 'float64')
  t_retval = numpy.zeros((destsize, target[0].shape[0]), 'float64')
  retval.fill(0)
  cur = 0
  for k, d in enumerate(data):
    retval[cur:(cur+len(d)),:] = numpy.vstack(d)
    for i in range(len(d)):
      t_retval[i+cur,:] = target[k]
    cur += len(d)
  return retval, t_retval

def create_machine(data, training_steps):
  """Creates the machine given the training data"""

  mlp = bob.learn.mlp.MLP((4, 4, len(data)))
  mlp.hidden_activation = bob.learn.activation.HyperbolicTangent()
  mlp.output_activation = bob.learn.activation.HyperbolicTangent()
  mlp.randomize() #reset weights and biases to a value between -0.1 and +0.1
  BATCH = 50
  trainer = bob.learn.mlp.MLPBackPropTrainer(BATCH, bob.learn.mlp.SquareError(mlp.output_activation), mlp)
  trainer.trainBiases = True #this is the default, but just to clarify!
  trainer.momentum = 0.1 #some momenta

  targets = [ #we choose the approximate Fisher response!
      numpy.array([+1., -1., -1.]), #setosa
      numpy.array([-1., +1., -1.]), #versicolor
      numpy.array([-1., -1., +1.]), #virginica
      ]

  # Associate the data to targets, by setting the arrayset order explicetly
  datalist = [data['setosa'], data['versicolor'], data['virginica']]

  # All data, as 2 x 2D arrays containing data and targets
  AllData, AllTargets = generate_testdata(datalist, targets)

  # A helper to select and shuffle the data
  S = bob.learn.mlp.DataShuffler(datalist, targets)

  # We now iterate for several steps, look for the convergence
  retval = [bob.learn.mlp.MLP(mlp)]

  for k in range(training_steps):

    input, target = S(BATCH)

    # We use "train_" which is unchecked and faster. Use train() if you want
    # checks! See the MLPBackPropTrainer documentation for details on this
    # before choosing the wrong approach.
    trainer.train_(mlp, input, target)
    print("|RMSE| @%d:" % (k,), end=' ')
    print(numpy.linalg.norm(bob.measure.rmse(mlp(AllData), AllTargets)))
    retval.append(bob.learn.mlp.MLP(mlp))

  return retval #all machines => nice plotting!

def process_data(machine, data):
  """Iterates over classes and passes data through the trained machine"""

  output = {}
  for cl in data.keys():
    output[cl]=machine.forward(data[cl])

  return output

def plot(output):
  """Plots each of the outputs, with the classes separated by colors.
  """

  import matplotlib.pyplot as mpl

  histo = [{}, {}, {}]
  for k in output.keys():
    for i in range(len(histo)):
      histo[i][k] = numpy.vstack(output[k])[:,i]

  order = ['setosa', 'versicolor', 'virginica']
  color = ['green', 'blue', 'red']

  FAR = []
  FRR = []
  THRES = []

  # Calculates separability
  for i, O in enumerate(order):
    positives = histo[i][O].copy() #make it C-style contiguous
    negatives = numpy.hstack([histo[i][k] for k in order if k != O])
    # note: threshold a posteriori! (don't do this at home, kids ;-)
    thres = bob.measure.eer_threshold(negatives, positives)
    far, frr = bob.measure.farfrr(negatives, positives, thres)
    FAR.append(far)
    FRR.append(frr)
    THRES.append(thres)

  # Plots the class histograms
  plot_counter = 0
  for O, C in zip(order, color):
    for k in range(len(histo)):
      plot_counter += 1
      mpl.subplot(len(histo), len(order), plot_counter)
      mpl.hist(histo[k][O], bins=20, color=C, range=(-1,+1), label='Setosa', alpha=0.5)
      mpl.vlines((THRES[k],), 0, 60, colors=('red',), linestyles=('--',))
      mpl.axis([-1.1,+1.1,0,60])
      mpl.grid(True)
      if k == 0: mpl.ylabel("Data %s" % O.capitalize())
      if O == order[-1]: mpl.xlabel("Output %s" % order[k].capitalize())
      if O == order[0]: mpl.title("EER = %.1f%%" % (100*(FAR[k] + FRR[k])/2))

def fig2bzarray(fig):
  """
  @brief Convert a Matplotlib figure to a 3D blitz array with RGB channels and
  return it
  @param fig a matplotlib figure
  @return a blitz 3D array of RGB values
  """
  import numpy

  # draw the renderer
  fig.canvas.draw()

  # Get the RGB buffer from the figure, re-shape it adequately
  w,h = fig.canvas.get_width_height()
  buf = numpy.fromstring(fig.canvas.tostring_rgb(),dtype=numpy.uint8)
  buf.shape = (h,w,3)
  buf = numpy.transpose(buf, (2,0,1))

  return numpy.array(buf)

def makemovie(machines, data, filename=None):
  """Plots each of the outputs, with the classes separated by colors.
  """

  if not filename:
    choose_matplotlib_iteractive_backend()
  else:
    import matplotlib
    if not hasattr(matplotlib, 'backends'): matplotlib.use('Agg')

  import matplotlib.pyplot as mpl

  output = None
  orows = 0
  ocols = 0
  if not filename: #start interactive plot animation
    mpl.ion()
  else:
    # test output size
    processed = process_data(machines[0], data)
    plot(processed)
    refimage = fig2bzarray(mpl.gcf())
    orows = int(2*(refimage.shape[1]/2))
    ocols = int(2*(refimage.shape[2]/2))
    output = bob.io.VideoWriter(filename, orows, ocols, 5) #5 Hz
    print("Saving %d frames to %s" % (len(machines), filename))

  for i, k in enumerate(machines):
    # test output size
    processed = process_data(k, data)
    mpl.clf()
    plot(processed)
    mpl.suptitle("Fisher Iris DB / MLP Training step %d" % i)
    if not filename: mpl.draw() #updates ion drawing
    else:
      image = fig2bzarray(mpl.gcf())
      output.append(image[:,:orows,:ocols])
      sys.stdout.write('.')
      sys.stdout.flush()

  if filename:
    sys.stdout.write('\n')
    sys.stdout.flush()

def main(user_input=None):

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("-t", "--steps", dest="steps", default=10, type=int,
      help="how many training times to train the MLP",
      metavar="INT")
  parser.add_argument("-f", "--file", dest="filename", default=None,
      help="write plot movie to FILE (implies non-interactiveness)",
      metavar="FILE")
  parser.add_argument("--self-test", action="store_true", dest="selftest",
      default=False, help=argparse.SUPPRESS)

  args = parser.parse_args(args=user_input)

  # Loads the dataset and performs LDA
  data = bob.db.iris.data()
  machines = create_machine(data, args.steps)

  if args.selftest:
    (fd, filename) = tempfile.mkstemp('.avi', 'bobtest_')
    os.close(fd)
    os.unlink(filename)
    makemovie(machines, data, filename)
    os.unlink(filename)
  else:
    makemovie(machines, data, args.filename)

  return 0
