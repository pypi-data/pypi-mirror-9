#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#Ivana Chingovska <ivana.chingovska@idiap.ch>
#Tue May 20 17:01:31 CEST 2014

from setuptools import setup, find_packages

packages = ['antispoofing'] + ['antispoofing.' + p for p in find_packages('antispoofing')]

# Define package version
version = open("version.txt").read().rstrip()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.clientspec',
    version=version,
    description='Building client-specific models for anti-spoofing',
    url='http://github.com/bioidiap/antispoofing.clientspec',
    license='LICENSE.txt',
    author='Ivana Chingovska',
    author_email='Ivana Chingovska <ivana.chingovska@idiap.ch>',
    #long_description=open('doc/howto.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),

    install_requires=[
        "argparse", # better option parsing
        "bob.db.replay", # Replay-Attack database
        "bob.db.casia_fasd", # CASIA FASd database
        "antispoofing.utils",  #Utils Package
    ],

    entry_points={
      'console_scripts': [
        'svm_clientspec_train.py = antispoofing.clientspec.script.svm_clientspec_train:main',
        'svm_clientspec_eval.py = antispoofing.clientspec.script.svm_clientspec_eval:main',
        'naive_modelling.py = antispoofing.clientspec.script.naive_modelling:main',
        'naive_likelihood.py = antispoofing.clientspec.script.naive_likelihood:main',
        'naive_likelihood_ratio.py = antispoofing.clientspec.script.naive_likelihood_ratio:main',
        'map_adapt_per_client.py = antispoofing.clientspec.script.map_adapt_per_client:main',
        'naive_likelihood_clientspecmodel.py = antispoofing.clientspec.script.naive_likelihood_clientspecmodel:main',
        'naive_likelihood_cohortmodels.py = antispoofing.clientspec.script.naive_likelihood_cohortmodels:main',
        'score_evaluation_crossdb.py = antispoofing.clientspec.script.score_evaluation_crossdb:main',
        'scores_box_plot.py = antispoofing.clientspec.script.scores_box_plot:main',
        ],
      },

)
