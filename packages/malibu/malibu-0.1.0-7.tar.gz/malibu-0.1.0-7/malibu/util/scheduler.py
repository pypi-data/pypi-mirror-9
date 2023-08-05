#!/usr/bin/env python2.7

import datetime, traceback
from datetime import datetime, timedelta

class Scheduler(object):
    __instance = None
    
    @staticmethod
    def get_instance():
    
        if Scheduler.__instance is None:
            return Scheduler()
        else:
            return Scheduler.__instance

    def __init__(self):
    
        Scheduler.__instance = self
        
        self.__jobs = {}

    def create_job(self, name, function, delta, recurring = False):
    
        if name in self.__jobs:
            raise SchedulerException("Job already exists; remove it first.")
        if function is None:
            raise SchedulerException("Callback function is non-existent.")
        if not isinstance(delta, timedelta):
            raise SchedulerException("Argument 'delta' was not a timedelta instance.")
        
        job = SchedulerJob(name, function, delta, recurring)
        self.add_job(job)
        
        return job
    
    def add_job(self, job):
    
        if job in self.__jobs:
            raise SchedulerException("Job already exists; remove it first.")
        job.begin_ticking()
        self.__jobs.update({ job.get_name() : job })
    
    def remove_job(self, name):
    
        if not name in self.__jobs:
            raise SchedulerException("Job does not exist.")
        
        job = self.__jobs[name]
        
        self.__jobs.pop(name)
    
    def tick(self):
    
        now = datetime.now()
        
        for job in self.__jobs.values():
            if job.is_ready(now):
                try:
                    job.execute()
                    job.set_traceback(None)
                except:
                    job.set_traceback(traceback.extract_frame())
                if not job.is_recurring():
                    self.remove_job(job.get_name())
    
class SchedulerJob(object):

    def __init__(self, name, function, delta, recurring = False):

        self._scheduler = Scheduler.get_instance()
        self._name = name
        self._function = function
        self._delta = delta
        self._recurring = recurring
	self._last_traceback = None
        
        self._eta = delta
    
    def get_name(self):
    
        return self._name
    
    def get_eta(self):
    
        return self._eta

    def get_traceback(self):

        return self._last_traceback

    def set_traceback(self, stack):

        self._last_traceback = stack
    
    def is_recurring(self):
    
        return self._recurring
    
    def is_ready(self, time):
    
        if time >= self._eta:
            return True
        else:
            return False
    
    def begin_ticking(self):

        self._eta = datetime.now() + self._delta
    
    def execute(self):
    
        self._function()
        
        if self._recurring:
            self._eta += self._delta

class SchedulerException(Exception):

    def __init__(self, value):

        self.value = value
    
    def __str__(self):

        return repr(self.value)
