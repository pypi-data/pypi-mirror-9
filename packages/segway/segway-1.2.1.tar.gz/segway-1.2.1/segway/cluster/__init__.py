#!/usr/bin/env python
from __future__ import division, with_statement

__version__ = "$Revision$"

# Copyright 2009, 2011-2014 Michael M. Hoffman <michael.hoffman@utoronto.ca>

from collections import defaultdict
from heapq import heappop, heappush
from os import environ
import sys
from time import sleep

DRIVER_NAME_OVERRIDE = environ.get("SEGWAY_CLUSTER")

if DRIVER_NAME_OVERRIDE == "local":
    from .local import ExitTimeoutException, JobState, Session
else:
    try:
        from drmaa import ExitTimeoutException, JobState, Session
    except (ImportError, RuntimeError):
        DRIVER_NAME_OVERRIDE = "local"  # no DRMAA available
        from .local import ExitTimeoutException, JobState, Session

from .._util import constant

FAILED = JobState.FAILED
DONE = JobState.DONE

NA_FACTORY = constant("NA")

# CLEAN_PERIOD in lsb.params, after which jobs are removed from
# mbatchd's memory default is 3600, multiplying by 0.5 for a margin of
# error
# XXX: check lsb.params for real value of CLEAN_PERIOD
CLEAN_SAFE_TIME = int(3600 * 0.9)

# min time to wait between checking job status
# XXX: should be an option
try:
    MIN_JOB_WAIT_SLEEP_TIME = float(environ["MIN_JOB_WAIT_SLEEP_TIME"])
except KeyError:
    MIN_JOB_WAIT_SLEEP_TIME = 3.0

## credited for min time so that there is some buffer when considering
## whether to submit more jobs or not

NOMINAL_MIN_JOB_WAIT_SLEEP_TIME = MIN_JOB_WAIT_SLEEP_TIME + 3
MAX_JOB_WAIT_SLEEP_TIME = 10  # max time to wait between checking job status

# these settings limit job queueing to 360 at once


def get_driver_name(session):
    if DRIVER_NAME_OVERRIDE:
        return DRIVER_NAME_OVERRIDE

    drms_info = session.drmsInfo

    # XXX: find out what Son of Grid Engine and GridScheduler report
    if (drms_info.startswith("GE") or drms_info.startswith("SGE")
            or drms_info.startswith("UGE") or drms_info.startswith("OGS/GE")):
        return "sge" # XXX: should probably change to GE
    elif drms_info.startswith("Platform LSF"):
        return "lsf"
    elif drms_info.startswith("SLURM"):
        return "slurm"
    # not sure what PBS and PBS Pro return here.
    elif drms_info.startswith("Torque"):
        return "pbs"
    else:
        msg = ("unsupported distributed resource management system: %s"
               % drms_info)
        raise ValueError(msg)

# non-reentrant code
with Session() as _session:
    driver_name = get_driver_name(_session)

driver = __import__(driver_name, globals(), locals(), [driver_name], 1)
JobTemplateFactory = driver.JobTemplateFactory
make_native_spec = driver.make_native_spec


class RestartableJob(object):
    def __init__(self, session, job_tmpl_factory, global_mem_usage,
                 mem_usage_key):
        self.session = session
        self.job_tmpl_factory = job_tmpl_factory

        # last trial index tried
        self.trial_index = -1

        self.global_mem_usage = global_mem_usage
        self.mem_usage_key = mem_usage_key

        # (-num_segs, -num_frames) so minimum value will be largest
        # num_segs, num_frames
        self.sort_key = (-mem_usage_key[1], -mem_usage_key[2])

    def __repr__(self):
        return "<RestartableJob '%s'>" % self.job_tmpl_factory.template.jobName

    def run(self):
        job_tmpl_factory = self.job_tmpl_factory

        global_mem_usage = self.global_mem_usage
        mem_usage_key = self.mem_usage_key
        trial_index = global_mem_usage[mem_usage_key]

        #print >>sys.stderr, ("self.trial_index=%d; trial_index=%d"
        #                     % (self.trial_index, trial_index))

        # if this index was tried before and unsuccessful, increment
        # and set global_mem_usage, controlling for race conditions
        if self.trial_index == trial_index:
            with global_mem_usage.lock:
                choices = [global_mem_usage[mem_usage_key], trial_index + 1]
                trial_index = max(choices)

            global_mem_usage[mem_usage_key] = trial_index

        self.trial_index = trial_index

        job_template = job_tmpl_factory(trial_index)
        res = self.session.runJob(job_template)

        assert res

        res_req = job_tmpl_factory.res_req
        if not isinstance(res_req, basestring):
            res_req = " ".join(res_req)

        jobname = job_template.jobName

        print >>sys.stderr, "queued %s: %s (%s)" % (res, jobname, res_req)

        return res


class RestartableJobDict(dict):
    def __init__(self, session, job_log_file, *args, **kwargs):
        self.session = session
        self.job_log_file = job_log_file
        self.unqueued_jobs = []

        return dict.__init__(self, *args, **kwargs)

    def calc_sleep_time(self):
        # it's not a good idea to keep increasing the amount of sleep
        # time just because you have completed jobs. The problem is
        # that this can result in it taking more than 3600 seconds to
        # check a job again

        # XXX: we should calculate this against the maximum number of
        # submitted jobs rather than the current number. But for now
        # we should just stick to MIN_JOB_WAIT_SLEEP_TIME

        # +1 is to avoid dividing by zero when len(self) is 0
        clean_safe_sleep_time = CLEAN_SAFE_TIME / (len(self) + 1)

        return min(clean_safe_sleep_time, MAX_JOB_WAIT_SLEEP_TIME)

    def is_sleep_time_gt_min(self):
        sleep_time = self.calc_sleep_time()
        # maximum value: MAX_JOB_WAIT_SLEEP_TIME
        # minimum value: CLEAN_SAFE_TIME / (num jobs + 1)

        return sleep_time > NOMINAL_MIN_JOB_WAIT_SLEEP_TIME

    def _queue_unconditional(self, restartable_job):
        """queue unconditionally; don't do any checks

        if you unconditionally queue more jobs than you can poll on
        time, then we will lose track of jobs
        """
        jobid = restartable_job.run()
        self[jobid] = restartable_job

    def queue(self, restartable_job):
        # handle dry run case
        if restartable_job is None:
            return

        # protect against queuing more jobs than I want to poll
        if self.is_sleep_time_gt_min():
            self._queue_unconditional(restartable_job)
        else:
            sort_key = restartable_job.sort_key
            heappush(self.unqueued_jobs, (sort_key, restartable_job))

    def queue_unqueued_jobs(self):
        while self.unqueued_jobs and self.is_sleep_time_gt_min():
            self._queue_unconditional(heappop(self.unqueued_jobs)[1])

    def get_job_info_exit_status(self, job_info):
        if job_info.hasSignal:
            res = job_info.terminatedSignal
            # just in case this edge case ever happens
            if res == 0:
                return "hasSignal"

            return res
        elif job_info.wasAborted:
            return "wasAborted"
        elif job_info.hasExited:
            return job_info.exitStatus

        # this happens when the exit status is unknown
        return "noExit"

    def process_job(self, jobid, job_info):
        exit_status = self.get_job_info_exit_status(job_info)

        # if the job queue is already full, this will probably
        # result in the job going to unqueued jobs for now
        if exit_status != 0:
            self.queue(self[jobid])

        restartable_job = self[jobid]
        jobname = restartable_job.job_tmpl_factory.template.jobName

        prog, num_segs, num_frames = restartable_job.mem_usage_key

        resource_usage_orig = job_info.resourceUsage
        resource_usage = defaultdict(NA_FACTORY, resource_usage_orig)

        try:  # SGE
            maxvmem = resource_usage_orig["maxvmem"]
        except KeyError:  # non-SGE systems
            maxvmem = resource_usage["vmem"]

        cpu = resource_usage["cpu"]
        row = [jobid, jobname, prog, str(num_segs), str(num_frames),
               maxvmem, cpu, str(exit_status)]
        print >>self.job_log_file, "\t".join(row)
        self.job_log_file.flush()  # allow reading file now

        del self[jobid]

    def wait(self):
        session = self.session
        jobids = self.keys()

        while jobids:
            # check each job individually
            for jobid in jobids:
                # XXX: should be an improved
                # RestartableJobDict.calc_sleep_time()
                sleep(MIN_JOB_WAIT_SLEEP_TIME)

                try:
                    job_info = session.wait(jobid, session.TIMEOUT_NO_WAIT)
                except ExitTimeoutException:
                    # job isn't done yet
                    continue

                self.process_job(jobid, job_info)
                self.queue_unqueued_jobs()

                # XXX: should be able to check
                # session.jobStatus(jobid) but this has problems
                # 1. it returns DONE even with non-zero exit status
                # is this an SGE or DRMAA bug? shouldn't a
                # non-zero exit status be a failure? or is that
                # just LSF?
                # 2. sometimes I can't get the jobStatus() of a completed job:
                # InvalidJobException: code 18: The job specified
                # by the 'jobid' does not exist. see versions prior to
                # SVN r425 for code

            jobids = self.keys()
