import urllib3
import logging
import json

logging.basicConfig()
LOG = logging.getLogger("AclBaseClient")
LOG.setLevel(logging.DEBUG)


class AclClient(object):

    def __init__(self, base_url, username, password, ip_version=4,):
        LOG.info("Initializing new acl base client.")
        self.kind = ""
        self.acls = []
        self.headers = {}
        self.base_url = base_url
        self.username = username
        self.password = password
        self.ip_version = ip_version
        self._add_basic_athentication()

    def _add_basic_athentication(self,):
        LOG.info("Setting up authentication.")
        self.headers.update(urllib3.util.make_headers(basic_auth='{}:{}'.format(self.username,
            self.password)))

    def _add_content_type_json(self,):
        LOG.info("Setting up \"Content-Type\".")
        self.headers.update({'Content-Type': 'application/json'})

    def _make_request(self, http_verb, endpoint, payload=None,):
        LOG.info("Going to make a request.")

        endpoint = self.base_url + endpoint
        http = urllib3.PoolManager()

        LOG.debug("Requesting {} on {}".format(http_verb, endpoint))

        if http_verb == 'GET':
            response = http.request(method=http_verb, url=endpoint, headers=self.headers)
        else:
            self._add_content_type_json()

            if not type(payload) == str:
                payload = json.dumps(payload)

            LOG.info("JSON PAYLOAD: {}".format(payload))

            response = http.urlopen(method=http_verb, body=payload,
                url=endpoint, headers=self.headers)

        LOG.debug("Response {}".format(response.data))

        return response

    def register_acl(self, payload,):
        LOG.info("Registering new ACL.")
        endpoint = "api/ipv{}/acl".format(self.ip_version)
        response = self._make_request(http_verb="POST", endpoint=endpoint, payload= payload)

        return json.loads(response.data)

    def destroy_acl(self, payload,):
        LOG.info("Destroying ACL.")

        endpoint = "api/ipv{}/acl".format(self.ip_version)
        response = self._make_request(http_verb="DELETE", endpoint=endpoint,
            payload= payload)

        return json.loads(response.data)

    def list_acls_for(self, environment, vlan):
        LOG.info("Retrieving ACLs for {} on {}".format(vlan, environment))

        endpoint = "api/ipv{}/acl/{}/{}".format(self.ip_version, environment, vlan)
        response = self._make_request(http_verb="GET", endpoint=endpoint,)

        return json.loads(response.data)

    def grant_acl_for(self, environment, vlan, payload):
        LOG.info("GRANT ACLs for {} on {}".format(vlan, environment))
        LOG.debug("Payload: {}".format(payload))

        endpoint = "api/ipv{}/acl/{}/24".format(self.ip_version, self.get_ip_vlan(environment))
        response = self._make_request(http_verb="PUT",
            endpoint=endpoint, payload= json.dumps(payload))

        json_data = json.loads(response.data)
        LOG.debug("JSON request.DATA decoded: {}".format(json_data))

        return json_data

    def revoke_acl_for(self, environment, vlan, payload):
        LOG.info("REVOKE ACLs for {} on {}".format(vlan, environment))
        LOG.debug("Payload: {}".format(payload))

        endpoint = "api/ipv{}/acl/{}/24".format(self.ip_version, self.get_ip_vlan(environment))
        response = self._make_request(http_verb="PURGE", endpoint=endpoint, payload= payload)

        json_data = json.loads(response.data)
        LOG.debug("JSON request.DATA decoded: {}".format(json_data))

        return json_data

    def list_jobs(self):
        LOG.info("Retrieving Jobs list.")

        endpoint = "api/jobs"
        response = self._make_request(http_verb="GET", endpoint=endpoint,)

        return json.loads(response.data)

    def get_job(self, job_id):
        LOG.info("Retrieving job {}".format(job_id))

        endpoint = "api/jobs/{}".format(job_id)
        response = self._make_request(http_verb="GET", endpoint=endpoint,)

        return json.loads(response.data)

    def run_job(self, job_id):
        LOG.info("Run job {}".format(job_id))

        endpoint = "api/jobs/{}/run".format(job_id)
        response = self._make_request(http_verb="GET", endpoint=endpoint,)

        return json.loads(response.data)

    def get_next_job(self):
        LOG.info("Getting next job")

        endpoint = "api/jobs/next"
        response = self._make_request(http_verb="GET", endpoint=endpoint,)

        return json.loads(response.data)

    def get_ip_vlan(self,ip):
        return "{}.0".format(ip[:ip.rindex('.')])
