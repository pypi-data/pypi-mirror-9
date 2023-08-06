import flask
from flask import current_app
from robot.libdocpkg.htmlwriter import DocToHtml

jobs = {}

def add_endpoints(blueprint):
    blueprint.add_url_rule("/jobs/", view_func=get_jobs)
    blueprint.add_url_rule("/jobs/<jobid>", view_func=get_job)

class ApiEndpoint(object):
    def __init__(self, blueprint):
        blueprint.add_url_rule("/jobs/", view_func=self.get_jobs)
        blueprint.add_url_rule("/jobs/<jobid>", view_func=self.get_job)
        
    ##
    ## Jobs
    ##
    def get_jobs(self):
        print "flask request:", flask.request

        if flask.request.method == "GET":
            result = {
                "jobs": jobs
            }

        elif flask.request.method == "POST":
            request = flask.request
            print "request headers:", request.headers

            try:
                print "json?", flask.request.get_json(force=True)
            except Exception as e:
                print "bummer:", e

            jobid = len(jobs)+1
            jobs[jobid] = {
                "running": True,
                "status": None,
                "config": {
                    "cwd": "<unknown>",
                    "command": ["unknown"],
                    "comments": "whatver"
                }
            }
            result = {"jobid": jobid}

        return flask.jsonify(result)

    def get_job(self, jobid):
        result = {
            "running": False,
            "status": 0,
            "config": {
                "command": ["python","-m","robot.run","--help"],
                "user": None,
                "comments": "pybot help"
            }
        }
        return flask.jsonify(result)



