# Copyright (c) 2015 Scott Christensen
#
# This file is part of condorpy
#
# condorpy is free software: you can redistribute it and/or modify it under
# the terms of the BSD 2-Clause License. A copy of the BSD 2-Clause License
# should have be distributed with this file.

#TODO: add ability to get stats about the job (i.e. number of jobs, run time, etc.)
#TODO: add ability to submit to remote schedulers

import os, subprocess, re
from collections import OrderedDict

class Job(object):
    """classdocs

    http://research.cs.wisc.edu/htcondor/manual/v7.8/condor_submit.html#man-condor-submit

    """


    def __init__(self, name, attributes=None, executable=None, arguments=None, num_jobs=1):
        """Constructor

        """
        object.__setattr__(self, '_name', name)
        if attributes:
            assert isinstance(attributes, dict)
        object.__setattr__(self, '_attributes', attributes or OrderedDict())
        object.__setattr__(self, '_num_jobs', int(num_jobs))
        object.__setattr__(self, '_cluster_id', 0)
        object.__setattr__(self, '_job_file', '')
        self.job_name = name
        self.executable = executable
        self.arguments = arguments


    def __str__(self):
        """docstring

        """

        return '\n'.join(self._list_attributes()) + '\n\nqueue %d\n' % (self.num_jobs)

    def __repr__(self):
        """docstring

        """
        return '<Job: name=%s, num_jobs=%d, cluster_id=%s>' % (self.name, self.num_jobs, self.cluster_id)

    def __copy__(self):
        """

        :return:
        """
        copy = Job(self.name)
        copy.__dict__.update(self.__dict__)
        return copy

    def __deepcopy__(self, memo):
        """

        :return:
        """
        from copy import deepcopy
        copy = self.__copy__()
        copy._attributes = deepcopy(self.attributes, memo)
        return copy

    def __getattr__(self, item):
        """

        :param item:
        :return:
        """
        return self.get(item)

    def __setattr__(self, key, value):
        """

        :param key:
        :param value:
        :return:
        """
        if  key in self.__dict__ or '_' + key in self.__dict__:
            object.__setattr__(self, key, value)
        else:
            self.set(key, value)

    @property
    def name(self):
        """

        :return:
        """
        self._name = self.get('job_name')
        return self._name

    @name.setter
    def name(self,name):
        """

        :param name:
        :return:
        """
        self.set('job_name', name)

    @property
    def attributes(self):
        """

        :return:
        """
        return self._attributes

    @property
    def num_jobs(self):
        """

        :return:
        """
        return self._num_jobs

    @num_jobs.setter
    def num_jobs(self, num_jobs):
        """

        :param num_jobs:
        :return:
        """
        self._num_jobs = int(num_jobs)

    @property
    def cluster_id(self):
        """

        :return:
        """
        return self._cluster_id

    @property
    def job_file(self):
        """

        :return:
        """
        #TODO: should the job file be just the name or the name and initdir?
        job_file_name = '%s.job' % (self.name)
        job_file_path = os.path.join(self.initial_dir, job_file_name)
        self._job_file = job_file_path
        return self._job_file

    @property
    def log_file(self):
        """

        :return:
        """
        #TODO: should the log file be just the name or the name and initdir?
        log_file = self.get('log')
        if not log_file:
            log_file = '%s.log' % (self.name)
            self.set('log', log_file)
        return self._resolve_attribute('log')

    @property
    def initial_dir(self):
        """

        :return:
        """
        initial_dir = self._resolve_attribute('initialdir')
        if not initial_dir:
            initial_dir = os.getcwd()
        return initial_dir

    def submit(self, queue=None, options=[]):
        """docstring

        """

        if not self.executable:
            raise NoExecutable('You cannot submit a job without an executable')

        self._num_jobs = queue or self.num_jobs

        self._write_job_file()

        args = ['condor_submit']
        args.extend(options)
        args.append(self.job_file)

        process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = process.communicate()

        if err:
            if re.match('WARNING',err):
                print(err)
            else:
                raise Exception(err)
        print(out)
        try:
            self._cluster_id = int(re.search('(?<=cluster |\*\* Proc )(\d*)', out).group(1))
        except:
            self._cluster_id = -1
        return self.cluster_id

    def remove(self, options=[], job_num=None):
        """docstring

        """
        args = ['condor_rm']
        args.extend(options)
        job_id = '%s.%s' % (self.cluster_id, job_num) if job_num else self.cluster_id
        args.append(job_id)
        process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = process.communicate()
        print(out,err)

    def edit(self):
        """interface for CLI edit commands

        """
        raise NotImplementedError("This method is not yet implemented")

    def status(self):
        """docstring

        """
        raise NotImplementedError("This method is not yet implemented")

    def wait(self, options=[], job_num=None):
        """

        :return:
        """
        args = ['condor_wait']
        args.extend(options)
        job_id = '%s.%s' % (self.cluster_id, job_num) if job_num else str(self.cluster_id)
        abs_log_file = os.path.join(self.initial_dir, self.log_file)
        args.extend([abs_log_file, job_id])
        print args
        process = subprocess.Popen(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()

    def get(self, attr, value=None):
        """get attribute from job file

        """
        try:
            value = self.attributes[attr]
        except KeyError:
            pass
        return value

    def set(self, attr, value):
        """set attribute in job file

        """
        self.attributes[attr] = value

    def delete(self, attr):
        """delete attribute from job file
        :param attr:
        :return:none
        """
        self.attributes.pop(attr)


    def _write_job_file(self):
        self._make_job_dirs()
        job_file = open(self.job_file, 'w')
        job_file.write(self.__str__())
        job_file.close()

    def _list_attributes(self):
        list = []
        for k,v in self.attributes.iteritems():
            if v:
                list.append(k + ' = ' + str(v))
        return list

    def _make_dir(self, dir_name):
        """docstring

        """
        try:
            os.makedirs(dir_name)
        except OSError:
            pass

    def _make_job_dirs(self):
        """docstring

        """
        self._make_dir(self.initial_dir)
        log_dir = self._resolve_attribute('logdir')
        if log_dir:
            self._make_dir(os.path.join(self.initial_dir, log_dir))

    def _resolve_attribute(self, attribute):
        """

        :return:
        """
        value = self.get(attribute)
        if not value:
            return None
        resolved_value = re.sub('\$\((.*?)\)',self._resolve_attribute_match, value)
        return resolved_value

    def _resolve_attribute_match(self, match):
        """

        :param match:
        :return:
        """
        if match.group(1) == 'cluster':
            return str(self.cluster_id)

        return self.get(match.group(1), match.group(0))



class NoExecutable(Exception):
    """docstring

    """
    pass



