====================================================
 Motion-Based Counter-Measures for Spoofing Attacks
====================================================

This package implements a motion-based counter-measure to spoofing attacks to
face recognition systems as described at the paper `Counter-Measures to Photo
Attacks in Face Recognition: a public database and a baseline`, by Anjos and
Marcel, International Joint Conference on Biometrics, 2011.

If you use this package and/or its results, please cite the following
publications:

1. The original paper with the counter-measure explained in details::

    @inproceedings{Anjos_IJCB_2011,
      author = {Anjos, Andr{\'{e}} and Marcel, S{\'{e}}bastien},
      keywords = {Attack, Counter-Measures, Counter-Spoofing, Disguise, Dishonest Acts, Face Recognition, Face Verification, Forgery, Liveness Detection, Replay, Spoofing, Trick},
      month = oct,
      title = {Counter-Measures to Photo Attacks in Face Recognition: a public database and a baseline},
      booktitle = {International Joint Conference on Biometrics 2011},
      year = {2011},
      url = {http://publications.idiap.ch/downloads/papers/2011/Anjos_IJCB_2011.pdf}
    }

2. Bob as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
      author = {A. Anjos and L. El Shafey and R. Wallace and M. G\"unther and C. McCool and S. Marcel},
      title = {Bob: a free signal processing and machine learning toolbox for researchers},
      year = {2012},
      month = oct,
      booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
      publisher = {ACM Press},
      url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
    }

3. If you decide to use the REPLAY-ATTACK database, you should also mention the
   following paper, where it is introduced::

    @inproceedings{Chingovska_BIOSIG_2012,
      author = {Chingovska, Ivana and Anjos, Andr{\'{e}} and Marcel, S{\'{e}}bastien},
      keywords = {Attack, Counter-Measures, Counter-Spoofing, Face Recognition, Liveness Detection, Replay, Spoofing},
      month = sep,
      title = {On the Effectiveness of Local Binary Patterns in Face Anti-spoofing},
      booktitle = {IEEE Biometrics Special Interest Group},
      year = {2012},
      url = {http://publications.idiap.ch/downloads/papers/2012/Chingovska_IEEEBIOSIG2012_2012.pdf},
    }

If you wish to report problems or improvements concerning this code, please
contact the authors of the above mentioned papers.

Raw data
--------

This method was originally conceived to work with the `the PRINT-ATTACK
database <https://www.idiap.ch/dataset/printattack>`_, but has since evolved to
work with the whole of the `the REPLAY-ATTACK database
<https://www.idiap.ch/dataset/replayattack>`_, which is a super-set of the
PRINT-ATTACK database. You are allowed to select protocols in each of the
applications described in this manual. To generate the results for the paper,
just select `print` as protocol option where necessary. Detailed comments about
specific results or tables are given where required.

The data used in the paper is publicly available and should be downloaded and
installed **prior** to try using the programs described in this package. The
root directory of the database installation is used by the first program in the
Antispoofing-Motion toolchain.

Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.motion
  <http://pypi.python.org/pypi/antispoofing.motion>`_ to download the latest
  stable version of this package. Then, extract the .zip file to a folder of your choice.

The ``antispoofing.motion`` package is a satellite package of the free signal processing and machine learning library Bob_. This dependency has to be downloaded manually. This version of the package depends on Bob_ version 2 or greater. To install `packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_, please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_. For Bob_ to be able to work properly, some dependent Bob packages are required to be installed. Please make sure that you have read the Dependencies for your operating system.

The most simple solution is to download and extract ``antispoofing.motion`` package, then to go to the console and write::

  $ cd antispoofing.motion
  $ python bootstrap-buildout.py
  $ bin/buildout

This will download all required dependent Bob_ and other packages and install them locally. 

User Guide
----------

It is assumed you have followed the installation instructions for the package
and got this package installed and the REPLAY-ATTACK (or PRINT-ATTACK) database
downloaded and uncompressed in a directory to which you have read access.
Through this manual, we will call this directory ``/root/of/database``. That
would be the directory that *contains* the sub-directories ``train``, ``test``,
``devel`` and ``face-locations``.

Note for Grid Users
===================

At Idiap, we use the powerful Sun Grid Engine (SGE) to parallelize our job
submissions as much as we can. At the Biometrics group, we have developed a
`little toolbox <http://pypi.python.org/pypi/gridtk>` that can submit and
manage jobs at the Idiap computing grid through SGE.  If you are at Idiap, you
can download and install this toolset by adding ``gridtk`` at the ``eggs``
section of your ``buildout.cfg`` file, if it is not already there. If you are
not, you still may look inside for tips on automated parallelization of
scripts.

The following sections will explain how to reproduce the paper results in
single (non-gridified) jobs. A note will be given where relevant explaining how
to parallalize the job submission using ``gridtk``.

Calculate Frame Differences
===========================

The first stage of the process is to calculate the normalized frame differences
using video sequences. The program that will do that should be sitting in
``bin/motion_framediff.py``. It can calculate normalize frame differences in distinct
parts of the scene (given you provide face locations for each of the frames in
all video sequences to be analyzed).

To execute the frame difference process to all videos in the REPLAY-ATTACK
database, just execute::

  $ ./bin/motion_framediff.py /root/of/database results/framediff replay

There are more options for the ``motion_framediff.py`` script you can use (such
as the sub-protocol selection for the Replay Attack database). Note that, by
default, all applications are tunned to work with the **whole** of the
database.  Just type ``--help`` **after** the keyword ``replay`` at the command
line for instructions.

.. note::

  To parallelize this job, do the following::

    $ ./bin/jman submit --array=1200 ./bin/motion_framediff.py /root/of/database results/framediff replay

  The `magic` number of `1200` entries can be found by executing::

    $ ./bin/motion_framediff.py --grid-count replay

  Which just prints the number of jobs it requires for the grid execution.

Calculate the 5 Quantities
==========================

The second step in calculating the frame differences is to compute the set of 5
quantities that are required for the detection process. To reproduce the
results in the paper, we accumulate the results in windows of 20 frames,
without overlap::

  $ ./bin/motion_diffcluster.py results/framediff results/quantities replay

There are more options for the `motion_diffcluster.py` script you can use (such
as the sub-protocol selection). Just type `--help` at the command line for
instructions.

.. note::

  This job is very fast and normally does not require parallelization. You can
  still do it with::

    $ ./bin/jman submit --array=1200 ./bin/motion_diffcluster.py results/framediff results/quantities replay

Training with Linear Discriminant Analysis (LDA)
================================================

Training a linear machine to perform LDA should go like this::

  $ ./bin/motion_ldatrain.py --verbose results/quantities results/lda replay

This will create a new linear machine train it using the training data.
Evaluation based on the EER on the development set will be performed by the end
of the training::

  Performance evaluation:
   -> EER @ devel set threshold: 8.11125e-02
   -> Devel set results:
       * FAR : 16.204% (175/1080)
       * FRR : 16.174% (558/3450)
       * HTER: 16.189%
   -> Test set results:
       * FAR: 16.389% (236/1440)
       * FRR: 18.641% (856/4592)
       * HTER: 17.515%

The resulting linear machine will be saved in the output directory called
``results/lda``.

Training an MLP
===============

Training MLPs to perform discrimination should go like this::

  $ ./bin/motion_rproptrain.py --verbose --epoch=10000 --batch-size=500 --no-improvements=1000000 --maximum-iterations=10000000 results/quantities results/mlp replay

This will create a new MLP and train it using the data produced by the
"clustering" step. The training can take anywhere from 20 to 30 minutes (or
even more), depending on your machine speed. You should see some debugging
output with the partial results as the training go along::

  ...
  iteration: RMSE:real/RMSE:attack (EER:%) ( train | devel )
  0: 9.1601e-01/1.0962e+00 (60.34%) | 9.1466e-01/1.0972e+00 (58.71%)
  0: Saving best network so far with average devel. RMSE = 1.0059e+00
  0: New valley stop threshold set to 1.2574e+00
  10000: 5.6706e-01/4.2730e-01 (8.29%) | 7.6343e-01/4.3836e-01 (11.90%)
  10000: Saving best network so far with average devel. RMSE = 6.0089e-01
  10000: New valley stop threshold set to 7.5112e-01
  20000: 5.6752e-01/4.2222e-01 (8.21%) | 7.6444e-01/4.3515e-01 (12.07%)
  20000: Saving best network so far with average devel. RMSE = 5.9979e-01
  20000: New valley stop threshold set to 7.4974e-01

The resulting MLP will be saved in the output directory called
``results/mlp``. The resulting directory will also contain performance
analysis plots. The results derived after this step are equivalent to the
results shown at Table 2 and Figure 3 at the paper.

To get results for specific supports as shown at the first two lines of Table
2, just select the support using the ``--support=hand`` or ``--support=fixed``
as a flag to ``motion_rproptrain.py``. Place this flags **after** the keyword
``replay`` at the command line. At this point, it is adviseable to use
different output directories using the ``--output-dir`` flag as well. If you
need to modify or regenerate Figure 3 at the paper, just look at
``antispoofing/motion/ml/perf.py``, which contains all plotting and analysis
routines.

.. note::

  If you think that the training is taking too long, you can interrupt it by
  pressing ``CTRL-C``. This will cause the script to quit gracefully and still
  evaluate the best MLP network performance to that point. 

.. note::

  To execute this script in the grid environment, just set the output directory
  to depend on the SGE_TASK_ID environment variable::

    $ ./bin/jman submit --array=10 ./bin/motion_rproptrain.py --verbose --epoch=10000 --batch-size=500 --no-improvements=1000000 --maximum-iterations=10000000 results/quantities 'results/mlp.%(SGE_TASK_ID)s' replay

Dumping Machine (MLP or LDA) Scores
===================================

You should now dump the scores for every input file in the
``results/quantities`` directory using the ``motion_make_scores.py`` script,
for example, to dump scores produced with by an MLP::

  $ ./bin/motion_make_scores.py --verbose results/quantities results/mlp/mlp.hdf5 results/mlp-scores replay

This should give you the detailed output of the machine for every input file in
the training, development and test sets. You can use these score files in your
own score analysis routines, for example.

.. note::

  The score file format is an HDF5 file with a single array, which contains the
  scores for every frame in the input video. Values which are marked as NaN
  should be ignored by your procedure. The reason varies: it may mean no valid
  face was detected on such a frame or that the motion-detection procedure
  decided to skip (on user configuration) the analysis of that frame.

Running the Time Analysis
=========================

The time analysis is the end of the processing chain, it fuses the scores of
instantaneous outputs to give out a better estimation of attacks and
real-accesses **for a set of frames**. You can used with the scores output by
MLPs or linear machines (LDA training). To use it, write something like::

  $ ./bin/motion_time_analysis.py --verbose results/mlp-scores results/mlp-time replay

The 3 curves on Figure 4 at the paper relate to the different support types.
Just repeat the procedure for every system trained with data for a particular
support (equivalent for then entries in Table 2). To set the support use
``--help`` after the keyword ``replay`` on the command-line above to find out
how to specify the support to this program. The output for this script is
dumped in PDF (plot) and text (``.rst`` file) on the specified directory.

Merging Scores
==============

If you wish to create a single `5-column format file
<http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/measure/index.html?highlight=five#bob.measure.load.five_column>`_
by combining this counter-measure scores for every video into a single file
that can be fed to external analysis utilities such as our
`antispoofing.evaluation <http://pypi.python.org/pypi/antispoofing.evaluation>`
package, you should use the script ``motion_merge_scores.py``. You will have to
specify how many of the scores in every video you will want to average and the
input directory containing the scores files that will be merged.

The output of the program consists of three 5-column formatted files with the
client identities and scores for **every video** in the input directory. A line
in the output file corresponds to a video from the database.

You run this program on the output of ``motion_make_scores.py``. So, it should
look like this if you followed the previous example::

  $ ./bin/motion_merge_scores.py results/mlp-scores results/mlp-merged replay

The above commandline examples will generate 3 files containing the training,
development and test scores, accumulated over each video in the respective
subsets, for input scores in the given input directory.

Problems
--------

In case of problems, please contact any of the authors of the paper.

.. _Bob: http://www.idiap.ch/software/bob