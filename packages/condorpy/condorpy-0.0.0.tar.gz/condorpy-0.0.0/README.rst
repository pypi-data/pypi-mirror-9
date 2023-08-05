===================
CondorPy v0.0.0
===================
:condorpy: Python interface for high throughput computing with HTCondor
:Version: 0.0.0
:Author: Scott Christensen
:Team: CI-Water
:Homepage: http://ci-water.org
:License: BSD 2-Clause

Description:
============
Condorpy is a wrapper for the command line interface (cli) of HTCondor and enables creating submitting and monitoring HTCondor jobs from Python. HTCondor must be installed to use condorpy.

Installing:
============
::

    $ pip install condorpy


Code Example:
============
::

    >>> from condorpy import Job, Templates
    >>> job = Job('job_name', Templates.vanilla_transfer_files)
    >>> job.executable = 'job_script'
    >>> jobs.arguments = 'input_1 input_2'
    >>> job.transfer_input_files = 'input_1 input_2'
    >>> job.transfer_output_files = 'output'
    >>> job.submit()

