===========================================================
 Client-specific classification for Biometric Anti-spoofing  
===========================================================

This package implements scripts to train **client-specific** classifiers for biometric anti-spoofing. For comparison purposes, this package also explains how to generate the results for the corresponding **client-independent** approaches based on the same classification technique. 

The methods are tried out with the Replay-Attack face spoofing database and each script of the package includes interface to connect to this database. So, reproducing results on Replay-Attack is very straight-forward. The package can be also used with CASIA-FASD database, but it uses a modified protocol to the database. The modified protocol is available at our interface to `CASIA-FASD <https://github.com/bioidiap/xbob.db.casia_fasd>`_

If you use this package and/or its results, please cite the following
publications:

1. The `original paper <http://publications.idiap.ch/downloads/papers/2015/Chingovska_IEEETIFSSI_2015.pdf>`_ with the client-specific counter-measure explained in details::

    @ARTICLE{Chingovska_IEEETIFSSI_2015,
        author = {Chingovska, Ivana and Anjos, Andr{\'{e}}},
        title = {On the use of client identity information for face anti-spoofing},
        journal = {IEEE Transactions on Information Forensics and Security, Special Issue on Biometric Anti-spoofing},
        year = {2015},
    }
 
2. `Bob <http://www.idiap.ch/software/bob>`_ as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
        author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
        title = {Bob: a free signal processing and machine learning toolbox for researchers},
        year = {2012},
        month = oct,
        booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
        publisher = {ACM Press},
    }

If you wish to report problems or improvements concerning this code, please
contact the authors of the above mentioned papers.

Raw data
--------

The Replay-Attack data used in the paper is publicly available and should be downloaded and
installed **prior** to try using the programs described in this package. Visit
`the REPLAY-ATTACK database portal
<https://www.idiap.ch/dataset/replayattack>`_ for more information.


Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.clientspec
  <http://pypi.python.org/pypi/antispoofing.clientspec>`_ to download the latest
  stable version of this package. Then, extract the .zip file to a folder of your choice.

The ``antispoofing.clientspec`` package is a satellite package of the free signal processing and machine learning library Bob_. This dependency has to be downloaded manually. This version of the package depends on Bob_ version 2 or greater. To install `packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_, please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_. For Bob_ to be able to work properly, some dependent Bob packages are required to be installed. Please make sure that you have read the Dependencies for your operating system.

The most simple solution is to download and extract ``antispoofing.clientspec`` package, then to go to the console and write::

  $ cd antispoofing.clientspec
  $ python bootstrap-buildout.py
  $ bin/buildout

This will download all required dependent Bob_ and other packages and install them locally. 

User Guide
----------

This section explains how to use the package, in order to reproduce the results from the paper. It focuses on the following things:

1. Generating the features used in the paper.

2. Generating scores for **client-independent SVM-based discriminative** baselines. They are generated using other satellite packages.

3. Generating scores for **client-specific SVM-based discriminative** approach.

4. Generating scores for **client-independent GMM-based generative** baselines.

5. Generating scores for **client-specific GMM-based generative** approach.

6. Computing the error rates.

Each step consists of several sub-steps.

Generating the features
=======================

The paper uses three types of features: LBP, LBP-TOP and MOTION. They can be generated with three different satellite packages.

1. `LBP <http://pypi.python.org/pypi/antispoofing.lbp>`_ . We use the simplest regular uniform LBP\ :sub:`8,1` :sup:`u2`\. The features are extracted from the face bounding box, normalized to 64x64. To compute these features, run the following command from `http://pypi.python.org/pypi/antispoofing.lbp <http://pypi.python.org/pypi/antispoofing.lbp>`_ ::

   $ ./bin/calcframelbp.py -v replaydir -d lbp/dir-features --ff 50 -c replay

   You need to run this command once again with the ``-e`` option to extract the features for the enrollment videos of the database.

2. `LBP-TOP <http://pypi.python.org/pypi/antispoofing.lbptop>`_ . We use the simplest regular uniform LBP\ :sub:`8,8,8,1,1,1` :sup:`u2`\. The features are extracted from the face bounding box, normalized to 64x64. To compute these features, run the following command from `http://pypi.python.org/pypi/antispoofing.lbp <http://pypi.python.org/pypi/antispoofing.lbp>`_ ::

   $ ./bin/calcframelbp.py -v replaydir -d lbp-top/dir-features --ff 50 -cXY -cXT -cYT -sC replay

   Again, you need to run this command once again with the ``-e`` option to extract the features for the enrollment videos of the database.

3. `MOTION <http://pypi.python.org/pypi/antispoofing.motion>`_ . We used the default parameters to extract these features. Please refer to the satellite package `http://pypi.python.org/pypi/antispoofing.motion <http://pypi.python.org/pypi/antispoofing.motion>`_ for instructions how to generate the features. You need to run just the commands: ``./bin/motion_framediff.py`` and ``./bin/motion_diffcluster.py``. Don't forget to run the commands with ``-e`` option as well, in order to extract the features for the enrollment videos of the database.

Please take a look at the correposnding satellite packages about their requirements, installation etc.

Generating scores for baseline client-independent SVM 
=====================================================

To generate the baseline results, we used SVM classifiers, which are provided within the satellite packages providing the features. The only exception is the MOTION features, which, in the original paper were classified using MLP, while in our case are classified using the SVM classifier used to classify LBP. In the following, we give the exact commands and parameters to generate the baseline results for the grandtest protocol of Replay-Attack.

1. LBP: we used `http://pypi.python.org/pypi/antispoofing.lbp <http://pypi.python.org/pypi/antispoofing.lbp>`_ satellite package. The SVM is trained with NO PCA reduction (hence, on the whole data), and after min-max normalization of the data. Note that, in the case of these features, we use min-max normalization as it gives better results than standard normalization::::
   
   $ ./bin/svmtrain_lbp.py -v lbp/dir-features -d lbp/dir-machines --min-max-normalize replay --protocol grandtest

   If you want to generate the machine for different Replay-Attack protocol, just set the ``--protocol`` option. More then one protocol can be specified.
   
   To do the classification, call::

   $ ./bin/svmeval_lbp.py -v lbp/dir-features -i lbp/dir-machines/svm_machine.hdf5 -d lbp/dir-scores replay
   
After this, you will have all the baseline scores for LBP in the directory``lbp/dir-scores``. The scores will be written as an array in .hdf files with the name of the video, and one score per frame.
    
2. LBP-TOP: we used `http://pypi.python.org/pypi/antispoofing.lbptop <http://pypi.python.org/pypi/antispoofing.lbptop>`_ satellite package. The SVM is trained with NO PCA reduction (hence, on the whole data), and after min-max normalization of the data. Note that, in the case of these features, we use min-max normalization as it gives better results than standard normalization::

   $ ./bin/lbptop_svmtrain.py -i lbp-top/dir-features -d lbp-top/dir-machines -n replay --protocol grandtest

   If you want to generate the machine for different Replay-Attack protocol, just set the ``--protocol`` option. More then one protocol can be specified.
   
   To do the classification, call::

   $ ./bin/lbptop_make_scores.py -f lbp-top/dir-features -m lbp-top/dir-machine/svm_machine_XY-XT-YT-plane.txt -n lbp-top/dir-machine/svm_normalization_XY-XT-YT-plane.txt -o lbp-top/dir-scores -l XY-XT-YT -v -a SVM replay
   
   After this, you will have all the baseline scores for LBP in the directory``lbp-top/dir-scores``. The scores will be written as an array in .hdf files with the name of the video, and one score per frame.   
   
   Note that any of these steps can take a very long time, so if you are at Idiap, consider using the SGE GRID. Refer to the satellite package about how to use it.   
   
3. MOTION: we used `http://pypi.python.org/pypi/antispoofing.lbp <http://pypi.python.org/pypi/antispoofing.lbp>`_ satellite package, as the original satellite pacakge for MOTION features, does not contain SVM classification utilities. The SVM is trained with NO PCA reduction (hence, on the whole data), and after standard normalization of the data. Note that, in the case of these features, we use standard normalization as it gives better results than min-max normalization::
   
   $ ./bin/svmtrain_lbp.py -v motion/dir-features -d motion/dir-machines --min-max-normalize replay --protocol grandtest

   If you want to generate the machine for different Replay-Attack protocol, just set the ``--protocol`` option. More then one protocol can be specified.
   
   To do the classification, call::

   $ ./bin/svmeval_lbp.py -v motion/dir-features -i motion/dir-machines/svm_machine.hdf5 -d motion/dir-scores replay
   
   After this, you will have all the baseline scores for LBP in the directory``motion/dir-scores``. The scores will be written as an array in .hdf files with the name of the video, and one score per frame.

   

Generating scores for client-specific SVM
=========================================

Generating the client-specific results consists of 2 steps: training an SVM for each client and calculating the scores for each client. Below we give how to perform these steps for LBP features and grandtest protocol of Replay-Attack. The steps for the other type of features are analogous.

1. Generate client-specific SVM. In our results, we were training SVM with NO PCA on the original features and after a standard normalization. To train a client-specific SVM for the clients in the test set and for LBP features, call::

   $ ./bin/svm_clientspec_train.py --featname lbp --outdir lbp/dir-machines --group test lbp/dir-features -n replay --protocol grandtest
   
   This step needs to be run three times: for the training, development and test subset. The above examples shows how to run it for the test set. The SVM machines, as well as the normalization parameters (and PCA parameters, if needed) will be stored in the ``test`` subdirectory of the output directory, in separate files for each client. The command works analogously for the devel and train set. The parameter ``--featname`` can be any custom name that you choose to give to your features, but pay attention to use it consistently through the calls of all the other scripts. Type ``--help`` after the command to see all its available options.
   
2. Compute the client-specific scores. 

   $ ./bin/svm_clientspec_eval.py --featname lbp -svmdir lbp/dir-machines --group test -outdir lbp/dir-scores lbp/dir-features replay
   
   This step needs to be run three times: for the training, development and test subset. The above examples shows how to run it for the test set. The SVM machines, as well as the normalization parameters (and PCA parameters, if needed) will be stored in the ``test`` subdirectory of the output directory, in separate files for each client. The command work analogously for the devel and train set. Type ``--help`` after the command to see all its available options.

   After this, you will have all the baseline scores for LBP in the directory``lbp/dir-scores``. The scores will be written as an array in .hdf files with the name of the video, and one score per frame.


Generating scores for baseline client-independent GMM
=====================================================

Generating the baseline results can be done in 5 steps. The values of the hyper-parameters (number of Gaussians) which are given in the commands below are optimized for the grandtest set of Replay-Attack. Please find a table at the end of the section for the parameter values optimized for other Replay-Attack protocols. Note that the models are created for features which are **normalized** using standard normalization and *PCA reduced*.

1. **Create model for Real Accesses** (LBP, LBP-TOP and MOTION features)::

   $ ./bin/naive_modelling.py --featname lbp --gaussians 5 --modeltype real -n -r -c -j -o lbp/dir-models/real lbp/dir-features replay --protocol grandtest
   $ ./bin/naive_modelling.py --featname lbp-top --gaussians 5 --modeltype real -n -r -c -j -o lbp-top/dir-models/real lbptop/dir-features replay --protocol grandtest
   $ ./bin/naive_modelling.py --featname motion --gaussians 10 --modeltype real -n -r -c -j -e 0.995 -o motion/dir-models/real motion/dir-features replay --protocol grandtest
   
   Note the parameter ``-e 0.995`` denoting the kept energy during PCA reduction for the MOTION features. We use the default for LBP and LBP-TOP. The parameter ``--featname`` can be any custom name that you choose to give to your features, but pay attention to use it consistently through the calls of all the scripts. Don't forget to change the protocol (``--protocol``) to the corresponding protocol of Replay-Attack that you want to use. Specifying several protocols is possible. Type ``--help`` after the command to see all its available options.

2. **Create model for Attacks** (LBP, LBP-TOP and MOTION features)::

   $ ./bin/naive_modelling.py --featname lbp --gaussians 10 --modeltype attack -n -r -c -j -o lbp/dir-models/attack lbp/dir-features replay --protocol grandtest
   $ ./bin/naive_modelling.py --featname lbp-top --gaussians 50 --modeltype attack -n -r -c -j -o lbp-top/dir-models/attack lbptop/dir-features replay --protocol grandtest
   $ ./bin/naive_modelling.py --featname motion --gaussians 300 --modeltype attack -n -r -c -j -e 0.995 -o motion/dir-models/attack motion/dir-features replay --protocol grandtest
   
   Note the parameter ``-e 0.995`` denoting the kept energy during PCA reduction for the MOTION features. We use the default for LBP and LBP-TOP. Don't forget to change the protocol to the corresponding protocol of Replay-Attack that you want to use. Specifying several protocols is possible. Type ``--help`` after the command to see all its available options.

3. **Calculate likelihoods to real access model** ::

   ./bin/naive_likelihood.py --featname lbp --gaussians 5 --modeldir lbp/dir-models/real -o lbp/dir-likelihoods/real lbp/dir-features replay
   
   Generating the likelihoods for the other features is analogous. Just change the ``--gaussians`` parameter to the corresponding value. Type ``--help`` after the command to see all its available options. 

4. **Calculate likelihoods to attack model** ::

   ./bin/naive_likelihood.py --featname lbp --gaussians 10 --modeldir lbp/dir-models/attack -o lbp/dir-likelihoods/attack lbp/dir-features replay
   
   Generating the likelihoods for the other features is analogous. Just change the ``--gaussians`` parameter to the corrsponding value. Type ``--help`` after the command to see all its available options.

5. **Calculate likelihood ratios** ::

   ./bin/naive_likelihood_ratio.py --dirreal lbp/dir-likelihoods/real/GMM-5 --dirattack lbp/dir-likelihoods/attack/GMM-10 -o lbp/likelihood_ratio/GMM-5/GMM-10/llr_real.vs.attack replay
   
   Generating the likelihood ratios for other features is analogous. You just need to change the number of Gaussians in the input and output folders to the corresponding values. Type ``--help`` after the command to see all its available options.

   After this, you will have scores for all the videos of Replay-Attack in the directory ``lbp/likelihood_ratio/GMM-5/GMM-10/llr_real.vs.attack`` (or analogous for the other features). The scores will be written as an array in .hdf files with the name of the video, and one score per frame. 

**The optimized values (obtained via grid search) for the number of Gaussians for each of the protocols of Replay-Atatck are given in the following table**:

=================  ====== ====== ====== ====== ====== ======
  features              LBP         LBP-TOP       MOTION     
-----------------  ------------- ------------- -------------
  protocol          real  attack  real  attack  real  attack
=================  ====== ====== ====== ====== ====== ======
**grandtest**         5     10      5     50     10     300 
**print**            250    235     5     10     35     5  
**digital**          15     35      10    15    100     115 
**video**             5     20      5     30     10     60  
**print+digital**     5     10      5     25     45    165   
**print+video**       5     15      10    75     10     240 
**digital+video**     5     10      5     30    100     295 
=================  ====== ====== ====== ====== ====== ====== 


Generating scores for client-specific GMM
=========================================

Generating the client-specific results can be done in 7 steps. The values of the hyper-parameters (number of Gaussians and relevance factor) which are given in the commands below are optimized for the grandtest set of Replay-Attack. Please find a table at the end of the section for the parameter values optimized for other Replay-Attack protocols. Note that the models are created for features which are **normalized** using standard normalization and *PCA reduced*.
   
1. **Create model for Real Accesses**. This step is exactly the same as step 1 of the previous section. Just replace the values of the number of Gaussians optimized for the client-specific models, which are given in the table at the end of the section.

2. **Create model for Attacks**. This step is exactly the same as step 2. of the previous section. Just replace the values of the number of Gaussians optimized for the client-specific models, which are given in the table at the end of the section.
   
3. **Enroll clients from the Real Access model using MAP adaptation** ::

   $ ./bin/map_adapt_per_client.py --featname lbp --modelfile lbp/dir-models/real/GMM-275.hdf5 -o lbp/dir-map-models/TEST/GMM-275/reals.hdf5 --group test --rel 1 --clss enroll lbp/dir-features replay

   This step needs to be run three times: for the training, development and test subset. The above examples shows how to run it for the test set. The class of samples using for the MAP adaptation is specified with ``--clss`` parameter and needs to be the *enrollment* samples in this case. The output is an .hdf5 file where the MAP adapted models are stored for each client of the particular subset.

   Generating the MAP models for the other features is analogous. Just change the number of Gaussians in the model filename and the output directory. Type ``--help`` after the command to see all its available options.    
   
4. **Create cohort models from the Attack model using MAP adaptation** ::

   $ ./bin/map_adapt_per_client.py --featname lbp --modelfile lbp/dir-models/attack/GMM-25.hdf5 -o lbp/dir-map-models/TRAIN/GMM-25/attacks.hdf5 --group train --rel 1 --clss attack lbp/dir-features replay --protocol grandtest

   This step needs to be run only once, because the cohorts are created from the training set. The class of samples using for the MAP adaptation is specified with ``--clss`` parameter and needs to be the *attack* samples in this case. Don't forget to change the protocol (``--protocol``) to the corresponding protocol of Replay-Attack that you want to use. The output is an .hdf5 file where all the cohort models are stored.

   Generating the cohort models for the other features is analogous. Just change the number of Gaussians in the model filename and the output directory. Type ``--help`` after the command to see all its available options.    

5. **Calculate likelihoods to real access client-specific models** :: 

   $ ./bin/naive_likelihood_clientspecmodel.py --featname lbp --mapmodelfile lbp/dir-map-models/TEST/GMM-275/reals.hdf5 -o lbp/dir-likelihood-clientspec/GMM-275 --group test lbp/dir-features replay

   This step needs to be run three times: for the training, development and test subset. The above examples shows how to run it for the test set. Generating the likelihoods for other features is analogous. Just change the number of Gaussians in the MAP model filename and the output directory. Type ``--help`` after the command to see all its available options.    
   
6. **Calculate likelihoods to attack cohort models** ::

   $ ./bin/naive_likelihood_cohortmodels.py --featname lbp --cohortfile lbp/dir-map-models/TRAIN/GMM-25/attacks.hdf5 -o lbp/dir-likelihood-cohort/likelihood-cohort-all/GMM-25 --group test lbp/dir-features replay

   This step needs to be run three times: for the training, development and test subset. The above examples shows how to run it for the test set. Generating the likelihoods for other features is analogous. Just change the number of Gaussians in the MAP model filename and the output directory. Note that you can specify the number N of cohorts that you want to use to compute the likelihood, using the ``-s`` option. In such a case, the highest N cohorts will be taken into account only. Type ``--help`` after the command to see all its available options.    
   
7. **Calculate the likelihood ratio** ::
  
   $ ./bin/naive_likelihood_ratio.py --dirreal lbp/dir-likelihood-clientspec/GMM-275 --dirattack lbp/dir-likelihood-cohort/likelihood-cohort-all/GMM-25 -o lbp/likelihood_ratio/GMM-275/GMM-25/llr_clientspec.vs.cohortall replay

   Generating the likelihood ratios for other features is analogous. You just need to change the number of Gaussians in the input and output folders to the corresponding values. Type ``--help`` after the command to see all its available options.

   After this, you will have scores for all the videos of Replay-Attack in the directory ``lbp/likelihood_ratio/GMM-275/GMM-25/llr_clientspec.vs.cohortall`` (or analogous for the other features). The scores will be written as an array in .hdf files with the name of the video, and one score per frame. 

**The optimized values (via grid search) for the number of Gaussians and the MAP relevance factor for each of the protocols of Replay-Attack are given in the following table**:

=================  ====== ====== === ====== ====== === ====== ====== ===
  features                 LBP            LBP-TOP            MOTION     
-----------------  ----------------- ----------------- -----------------
  protocol          real  attack rel  real  attack rel  real  attack rel
=================  ====== ====== === ====== ====== === ====== ====== ===
**grandtest**        275    25    1    295    100   5    10      45   5 
**print**            160    20    1    300    210   1    70      10   1
**digital**          250     5    4    300     35   3   100     165   1
**video**            275    15    5    295     55   5    15     230   5  
**print+digital**    275    20    1    295     60   5    50     100   1    
**print+video**      280    15    3    240     80   5    15      90   5
**digital+video**    250    10    3    240     85   5    45      65   2 
=================  ====== ====== === ====== ====== === ====== ====== ===

   
Computing the error rates
=========================   

After the scores have been generated, you can use the script ``./bin/score_evaluation_crossdb.py`` to compute the error rates. For example, to compute the error rates for the scores obtained using the client-specific SVM approach, call::

   $ ./bin/score_evaluation_crossdb.py --devel-scores-dir lbp/dir-scores --test_scores-dir lbp/dir-scores --dev-set replay --test-set replay --attack-devel grandtest --attack-test grandtest --verbose

The same command used for computing the scores obtained using the client-specific GMM approach, will look like::
 
   $ ./bin/score_evaluation_crossdb.py --devel-scores-dir lbp/likelihood_ratio/GMM-275/GMM-25/llr_clientspec.vs.cohortall --test_scores-dir lbp/likelihood_ratio/GMM-275/GMM-25/llr_clientspec.vs.cohortall --dev-set replay --test-set replay --attack-devel grandtest --attack-test grandtest --verbose


Type ``--help`` after the command to see all its available options. Note that with the options ``--sd`` and ``--st`` you can specify the directiories with the scores of the development and test set, respectively. Note that this script can be used to use one database for computing the threshold and another one for evaluation (specify the names of the databases with the ``-d`` and ``-t`` parameters). For the cross-protocol evaluation (that is described in the paper), you can specify separate protocols used for decision threshoold and evaluation (use ``--ad`` and ``--at`` parameters). In such a case, most likely the values of the parameters ``--sd`` and ``--st`` will be different too.

Plotting the box plots
======================

Here is an example how to plot the box plots of the scores for each users, for the scores obtained using the client-specific GMM approach::

   $ ./bin/scores_box_plot.py --devel-scores-dir lbp/likelihood_ratio/GMM-275/GMM-25/llr_clientspec.vs.cohortall --test_scores-dir lbp/likelihood_ratio/GMM-275/GMM-25/llr_clientspec.vs.cohortall --dev-set replay --test-set replay --attack-devel grandtest --attack-test grandtest --normalization --reject-outlier --verbose

Type ``--help`` after the command to see all its available options. It is recommended that the scores are always normalized (``--normalization`` option) with outliers rejected during the normalization (``--reject-outlier`` option).  

Problems
--------

In case of problems, please contact ivana.chingovska@idiap.ch (or any of the authors of the paper).
