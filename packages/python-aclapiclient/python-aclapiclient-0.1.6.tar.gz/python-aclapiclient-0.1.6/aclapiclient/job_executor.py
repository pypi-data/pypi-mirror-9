import multiprocessing as mp
import requests
import syslog


class Executor(object):

    def __init__(self, url, jobs, auth):
        self.jobs = jobs
        self.url = url
        self.auth = auth

    def execute(self):
        workers = []
        for job in self.jobs:
            w = mp.Process(target=request_worker, args=(self.url, job, self.auth))
            w.start()
            workers.append(w)

        return workers


def request_worker(url, job, auth):
    full_url = "{}{}/run".format(url, job)
    resp = requests.get(full_url, verify=False, auth=auth)
    if resp.status_code != 200:
        # fail recovery?
        syslog.syslog(syslog.LOG_ERR, "Error while processing job: {}".format(resp.content))
