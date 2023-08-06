====================================================
 Optical Flow Counter-Measures for Spoofing Attacks
====================================================

This package contains our published Optical Flow algorithm for face recognition
anti-spoofing. This document explains how to install it and use it to produce
our paper results.

If you use this package and/or its results, please cite the following
publications:

1. The original paper with the counter-measure explained in details (under
   review)::

    @article{Anjos_IETBMT_2013,
      author = {Anjos, Andr{\'{e}} and Murali Mohan Chakka and Marcel, S{\'{e}}bastien},
      keywords = {Attack, Counter-Measures, Counter-Spoofing, Disguise, Dishonest Acts, Face Recognition, Face Verification, Forgery, Liveness Detection, Replay, Spoofing, Trick, Optical Flow},
      month = apr,
      title = {Motion-Based Counter-Measures to Photo Attacks in Face Recognition},
      journal = {Institution of Engineering and Technology - Biometrics},
      year = {2013},
    }

2. Bob as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
      author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
      title = {Bob: a free signal processing and machine learning toolbox for researchers},
      year = {2012},
      month = oct,
      booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
      publisher = {ACM Press},
      url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
    }

.. 3. To use the REPLAY-ATTACK database, you should also mention the following
   paper, where it is introduced::

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

The data used in the paper is publicly available and should be downloaded and
installed **prior** to try using the programs described in this package. Visit
`the PHOTO-ATTACK database portal <https://www.idiap.ch/dataset/photoattack>`_
for more information.

Installation
------------

.. note::

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.optflow
  <http://pypi.python.org/pypi/antispoofing.optflow>`_ to download the latest
  stable version of this package.

There are 2 options you can follow to get this package installed and
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install antispoofing.optflow

You can also do the same with ``easy_install``::

  $ easy_install antispoofing.optflow

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/antispoofing.optflow>`_ and unpack it in your
working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::

  $ python bootstrap.py
  $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and
get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob
  <http://idiap.github.com/bob>`_, you must make sure that the ``bootstrap.py``
  script is called with the **same** interpreter used to build Bob, or
  unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``buildout`` and edit or
  add the line ``prefixes`` to point to the directory where Bob is installed or
  built. For example::

    [buildout]
    ...
    prefixes=/Users/crazyfox/work/bob/build

User Guide
----------

It is assumed you have followed the installation instructions for the package
and got this package installed and the PHOTO-ATTACK database downloaded and
uncompressed in a directory. You should have all required utilities sitting
inside a binary directory depending on your installation strategy (utilities
will be inside the ``bin`` if you used the buildout option). We expect that the
video files downloaded for the PHOTO-ATTACK database are installed in a
sub-directory called ``database`` at the root of the package.  You can use a
link to the location of the database files, if you don't want to have the
database installed on the root of this package::

  $ ln -s /path/where/you/installed/the/photo-attack-database database

If you don't want to create a link, use the ``--input-dir`` flag to specify
the root directory containing the database files. That would be the directory
that *contains* the sub-directories ``train``, ``test``, ``devel`` and
``face-locations``.

Paper Layout: How to Reproduce our Results
==========================================

The paper studies 4 algorithms (the first 3 are published elsewhere and are
**not** a contribution to this paper):

Reference System 1 (RS1) - Kollreider's Optical Flow anti-spoofing::

  @article{Kollreider_2009,
    author={K. Kollreider AND H. Fronthaler AND J. Bigun},
    title={Non-intrusive liveness detection by face images},
    volume={27},
    number={3},
    journal={Image and Vision Computing},
    publisher={Elsevier B.V.},
    year={2009},
    pages={233--244},
  }

Reference System 2 (RS2) - Bao's Optical Flow anti-spoofing::

  @inproceedings{Bao_2009,
    author={Wei Bao AND H. Li AND Nan Li AND Wei Jiang},
    title={A liveness detection method for face recognition based on optical flow field},
    booktitle={2009 International Conference on Image Analysis and Signal Processi
  ng},
    publisher={IEEE},
    year={2009},
    pages={233--236},
  }

Reference System 3 (RS3) - Our own Frame Difference's based anti-spoofing::

  @inproceedings{Anjos_IJCB_2011,
    author = {Anjos, Andr{\'{e}} and Marcel, S{\'{e}}bastien},
    keywords = {Attack, Counter-Measures, Counter-Spoofing, Disguise, Dishonest Acts, Face Recognition, Face Verification, Forgery, Liveness Detection, Replay, Spoofing, Trick},
    month = oct,
    title = {Counter-Measures to Photo Attacks in Face Recognition: a public database and a baseline},
    booktitle = {International Joint Conference on Biometrics 2011},
    year = {2011},
    url = {http://publications.idiap.ch/downloads/papers/2011/Anjos_IJCB_2011.pdf}
  }

The final algorithm based on Optical Flow Correlation (OFC) **represents our
contribution in this paper**.

To reproduce the results for RS3, you can follow the instructions on `its own
satellite package for Bob <http://pypi.python.org/pypi/antispoofing.motion>`_.
The scripts for that package should be auto-generated and made available for
you under your ``bin`` as well (this package depends on that one).

In this manual, we address how to extract results for RS1, 2 and OFC, which
operate on the top of a previously estimated Optical Flow (OF) field.  OF is,
therefore, the first topic in this manual.

Extract the Optical Flow Features
=================================

We ship this package with a preset to use `Ce Liu's OF framework
<http://pypi.python.org/pypi/xbob.optflow.liu>`_. This is of course not
required, but it is the framework we have tested our method with, therefore the
one we recommend you to start using. This framework estimates the *dense* OF
field between any two successive frames. It is quite slow. Be warned, it may
take quite some time to get through all the videos. To run the extraction
sequentially, for all videos, use the following command::

  $ ./bin/optflow_estimate.py --verbose /root/of/database results/flows replay --protocol=photo

.. note::

  The command line above is going to take a lot of time to complete. You may
  need to parallelize the job. If you are Idiap, you can use the ``gridtk``
  package, which should be downloaded and installed on your current
  environment::

    $ ./bin/jman submit --array=800 --queue=q1d ./bin/optflow_estimate.py --verbose /root/of/database results/flows replay --protocol=photo

  The ``magic`` number of ``800`` entries can be found by executing::

    $ ./bin/optflow_estimate.py --grid-count replay --protocol=photo

  Which just prints the number of jobs it requires for the grid execution. Each
  job is consuming less than 2 gigabytes of RAM, but more than 1 gigabyte.
  Therefore, you must choose the right queue and may need to set memory
  requirements for the machines you will be running at.

.. note::

  In case you want to replace this phase by another algorithm of your own.
  Notice that the output format is 1 HDF5 file per input video in the database,
  organized in the same way as in the original database. Each input video
  should contain a single 4D 64-bit float point array which has the following
  shape: (frames, u+v, height, width). The second dimension corresponds to the
  U (horizontal) and V (vertical) velocities as output by your algorithm, for
  every pixel in the image. If you have not used a dense OF estimator, please
  extrapolate yourself the values before calling the next scripts.

  If you respect this requirement, than you can test the results of this
  framework with any OF estimation technique of your choice.

Once you are in possession of the flow fields. You can start calculating the
scores required by each of the methods reviewed in the paper. It can help in
terms of processing speed to have the features located on a local hard-drive.
The HDF5 files tend to be huge.

.. important::

  Depending on the version of FFmpeg you have installed on your platform when
  you estimate the OF, you may get slightly different results at this step.
  These are due to imprecisions on the video decoding.

  You can also use the Matlab version of Ce Liu's code directly to produce the
  flow fields. In this case, you may also find small differences on the
  estimated velocities. The differences are due to the movie decoding and
  gray-scale conversion, which are different than Bob's.

  In any of these conditions, our tests show these do not affect the overall
  performance of our method. It may slightly change the final results you can
  obtain.

Reference System 1: Scores from Kollreider's
============================================

To calculate scores using Kollreider's method, use the script
``optflow_kollreider.py`` in the following way::

  $ ./bin/optflow_kollreider.py --verbose /root/of/database results/flows results/kollreider replay --protocol=photo

You can modify the :math:`\tau` parameter required by the method with the
program option ``--tau=<float-value>``. By default, this parameter is set to
``1.0``. Refer to the original paper by Kollreider to understand the meaning
and how to tune this parameter. If you tune the parameter and execute the error
analysis as explained below, you will get to the results shown on Table 1 of
our paper.

.. note::

  The above program can be somewhat slow, even if it is much faster than the
  flow field estimation itself. If you want to speed things, up, just run it on
  the grid::

    $ ./bin/jman submit --array=800 ./bin/optflow_kollreider.py --verbose /root/of/database results/flows results/kollreider replay --protocol=photo

  The program ``optflow_kollreider.py`` can also print the number of jobs it can
  be broken into with the ``--grid-count`` option::

    ./bin/optflow_kollreider.py --grid-count replay --protocol=photo

.. important::

  We estimate the position of the face center and the ears based on the
  bounding-box provided by the face locations. This way, we could compare all
  algorithms using the same input set. We have not tested if specialized
  key-point localizers would give better results than ours for this method.

Besides generating output for the tests in the paper, you can also generate an
annotated video, showing how our extrapolation of the face bounding boxes work
for finding out the regions of interest to apply Kollreider's work on. To do
this, use the script `optflow_kollreider_annotate.py`. It works on a similar
way to the above script and will process the whole database if not told
otherwise. This can be somewhat long as well, but you can grid-fy it if you
wish or use filtering options for the database to limit the number of videos
analysed. For example::

  $ bin/optflow_kollreider_annotate.py -v /idiap/group/replay/database/protocols/replayattack-database tmp replay --protocol=photo --client=101 --light=adverse

Reference System 2: Scores from Bao's
=====================================

To calculate scores for Bao's method, use the script
``optflow_bao.py`` in the following way::

  $ ./bin/optflow_bao.py --verbose /root/of/database results/flows results/bao replay --protocol=photo

You can modify the border parameter required by the method with the program
option ``--border=<integer-value>``. By default, this parameter is set to ``5``
(pixels). The original paper by Bao and others does not suggest such a
parameter or mention how does the face bounding-boxes are set. We assume a
default value of pixels surrounding our detected face. In the paper, we scan
this value from ``0`` (zero) to a number of pixels to test the method. If you
tune the parameter and execute the error analysis as explained below, you will
get to the results shown on Table 2 of our paper.

.. note::

  The above program can be somewhat slow, even if it is much faster than the
  flow field estimation itself. If you want to speed things, up, just run it on
  the grid::

    $ ./bin/jman submit --array=800 ./bin/optflow_bao.py --verbose /root/of/database results/flows results/bao replay --protocol=photo

  The program ``optflow_bao.py`` can also print the number of jobs it can
  be broken into with the ``--grid-count`` option::

    ./bin/optflow_bao.py --grid-count replay --protocol=photo

Reference System 3: Frame-differences
=====================================

As mentioned before, you should follow the instructions on `its own satellite
package for Bob`_. The scripts for that package should be auto-generated and
made available for you under your ``bin`` as well (this package depends on that
one).

Optical Flow Correlation (OFC)
==============================

To reproduce the results on our paper, you will need first to generate the
scores for the :math:`\chi^2` comparison for every frame in the sequence.
Frames with no faces detected generate a score valued ``numpy.NaN``, similar to
other counter-measures implemented by our group. To generate each score per
frame, you can use the application ``optflow_histocomp.py``::

  $ ./bin/optflow_histocomp.py --verbose /root/of/database results/flows results/histocomp replay --protocol=photo

.. note::

  The above program can be somewhat slow, even if it is much faster than the
  flow field estimation itself. If you want to speed things, up, just run it on
  the grid::

    $ ./bin/jman submit --array=800 ./bin/optflow_histocomp.py --verbose /root/of/database results/flows results/histocomp replay --protocol=photo

  The program ``optflow_histocomp.py`` can also print the number of jobs it can
  be broken into with the ``--grid-count`` option::

    ./bin/optflow_histocomp.py --grid-count replay --protocol=photo

You can generate the results in Figure 5 and 6 of our paper by setting 2
parameters on the above script:

  ``--number-of-bins``
    This changes the parameter :math:`Q`, explained on the paper, related to
    the quantization of the angle space. (see results in Figure 5.)

  ``--offset``
    This changes the offset for the quantization. Its effect is studied in
    Figure 6, for ``--number-of-bins=2``, as explained in the paper.

By modifying the above parameters and executing an error analysis as
explained bellow, with ``--window-size=220``, you will get to the results
plotted.

Error Analysis
==============

Once the scores you want to analyze are produced by one of the methods above,
you can calculate the error on the database using the application
``score_analysis.py``. This program receives one directory (containing the
scores output by a given method) and produces a console analysis of such a
method, which is used by the paper::

  $ ./bin/score_analysis.py results/histocomp replay --protocol=photo

That command will calculate a development set threshold at the Equal Error Rate
(EER) and will apply it to the test set, reporting errors on both sets. A
typical output would be like this::

  Input data: /idiap/temp/aanjos/spoofing/scores/optflow_histocomp
  Thres. at EER of development set: 6.9459e-02
  [EER @devel] FAR: 37.04% (15601 / 42120) | FRR: 37.04% (8312 / 22440) | HTER: 37.04%
  [HTER @test] FAR: 37.11% (20843 / 56160) | FRR: 35.75% (10696 / 29920) | HTER: 36.43%

The error analysis program considers, by default, every frame analyzed as **an
individual (independent) observation** and calculates the error rates based on
the overall set of frames found on the whole development and test sets. The
numbers printed inside the parentheses indicate how many frames were evaluated
in each set (denominator) and how many of those contributed to the percentage
displayed (numerator). The Half-Total Error Rate (HTER) is evaluated for both
the development set and test sets. The HTER for the develpment set is equal to
the EER on the same set, naturally.

The ``score_analysis.py`` script contains 2 parameters that can be used to
fine-tune the program behaviour, to be known:

  ``--window-size=<integer>``

    Defines a window size to which the scores are going to be averaged to,
    within the same score sequence. So, for example, if one of the files
    produced by ``optflow_histocomp.py`` contains a sequence of scores that
    reads like ``[1.0, 2.0, 1.5, 3.5, 0.5]``, and the window-size parameter is
    set to 2, then, the scores evaluated by this procedure are ``[1.5, 1.75,
    2.5, 2.0]``, which represent the averages of ``[1.0, 2.0]``, ``[2.0,
    1.5]``, ``[1.5, 3.5]`` and ``[3.5, 0.5]``.

  ``--overlap=<integer>``

    Controls the amount of overlap between the windows. If not set, the default
    overlap is set to ``window-size - 1``. You can modify this behaviour by
    setting this parameter to a different value. Taking the example above, if
    you set the window-size to 2 and the overlap to zero, then the score set
    produced by this analysis would be ``[1.5, 2.5]``. Notice that the frame
    value ``0.5`` (the last of the sequence) is ignored.

You will observe the effect of setting the window-size on the score analysis by
looking at the number of *averaged frames* analyzed::

  $ ./bin/score_analysis.py --window-size=220 --overlap=80 results/histocomp replay --protocol=photo

And the output::

  Input data: /idiap/temp/aanjos/spoofing/scores/optflow_histocomp
  Window size: 220 (overlap = 80)
  Thres. at EER of development set: 1.4863e-01
  [EER @devel] FAR: 2.78% (5 / 180) | FRR: 2.50% (3 / 120) | HTER: 2.64%
  [HTER @test] FAR: 2.92% (7 / 240) | FRR: 1.88% (3 / 160) | HTER: 2.40%

You can generate the results in Figure 7 and Table III on the paper just by
manipulating this program.

Our paper also shows a break-down analysis (by device attack type and support)
on Figure 8 (last figure). To generate such a figure, one must produce the
break-down analysis per device (Figure 8.a) and attack support (Figure 8.b). To
do this, pass the ``--breakdown`` option to the ``score_analysis.py`` script::

  $ ./bin/score_analysis.py --window-size=220 --overlap=80 --breakdown results/histocomp replay --protocol=photo

Our paper also discusses the impact of skipping the OF calculation on certain
frames (see Discussion section) in the interest of saving computational
resources. You can generate the table presented at the paper by playing with
the ``--skip`` parameter of ``score_analysis.py``. By default, we don't skip
any frames, if you set this parameter to 1, then we'd skip every other frame.
If you set it to 2, then we only consider 1 in every 3 frames, and so on.

Problems
--------

In case of problems, please contact any of the authors of the paper.
