from collections import namedtuple
from job_executor import Executor
import base64
import httplib
import json
import requests


class Client(object):

    def __init__(self, username, password, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.auth64 = base64.b64encode("{}:{}".format(username, password))
        self.session.verify = False
        self.jobs = []

    def add_acl(self, environment, vlan=None, name=None, path=None):
        """
        Records an ACL on ACL API.

        environment: environment identifier where the ACL is going to
        be recorded. it may also be an ip with a network mask.
        vlan: integer. VLAN number on network equipament. not needed when
        environment is ip/mask.

        Raises an exception in case of error.
        Returns the response.
        """
        url = "{}/api/ipv4/acl".format(self.base_url)
        body = {
            "kind": "collection#acl",
            "acls": [{"environment": environment}]
        }

        if vlan:
            body["acls"][0]["num_vlan"] = vlan
        if name:
            body["acls"][0]["name"] = name
        if path:
            body["acls"][0]["path"] = path

        resp = self.session.post(url, data=json.dumps(body))
        self._raises_on_error(resp, body)
        self.jobs.append(resp.headers["location"])

        return resp

    def remove_acl(self, environment, vlan):
        """
        Removes an ACL from ACL API.
        """
        url = "{}/api/ipv4/acl".format(self.base_url)
        body = {
            "kind": "collection#acl",
            "acls": [{"environment": environment}]
        }

        if vlan:
            body["acls"][0]["num_vlan"] = vlan

        resp = self.session.delete(url, data=json.dumps(body))
        self._raises_on_error(resp, body)

        return resp

    def _raises_on_error(self, response, body):
        if response.status_code >= 400:
            error = json.loads(response.content)
            msg = "{}\nRequest body is: {}".format(error["message"], body)
            raise ValueError(msg)

    def add_tcp_permit_access(self, desc, source, dest, l4_opts):
        body = {
            "kind": "object#acl",
            "rules": [
                {
                    "protocol": "tcp",
                    "source": source,
                    "destination": dest,
                    "action": "permit",
                    "l4-options": l4_opts.to_dict()
                }
            ]
        }
        url = "{}/api/ipv4/acl/{}".format(self.base_url, source)
        resp = self.session.put(url, data=json.dumps(body))
        self._raises_on_error(resp, body)
        self.jobs.append(resp.headers["location"])
        return resp

    def remove_tcp_permit_access(self, desc, source, dest, l4_opts):
        body = {
            "kind": "object#acl",
            "rules": [
                {
                    "protocol": "tcp",
                    "source": source,
                    "destination": dest,
                    "action": "permit",
                    "l4-options": l4_opts.to_dict()
                }
            ]
        }
        path = "/api/ipv4/acl/{}".format(source)
        conn = httplib.HTTPSConnection(self.base_url.replace("https://", ""))
        headers = {"Content-Type": "application/json", "Authorization": "Basic {}".format(self.auth64)}
        conn.request("PURGE", path, json.dumps(body), headers)
        resp = conn.getresponse()
        if resp.status >= 400:
            error = json.loads(resp.read())
            if "message" in error:
                raise ValueError(error["message"])
            else:
                raise ValueError(error["result"])
        self.jobs.append(resp.getheader("location"))
        resp = namedtuple("Response", ["status_code", "content"])(resp.status, resp.read())
        return resp

    def commit(self):
        e = Executor(self.base_url, self.jobs, self.session.auth)
        workers = e.execute()
        return workers
