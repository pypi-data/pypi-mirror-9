import traceback

try:
    import multiprocessing
    USE_MULTIPROCESSING = True
except ImportError:
    USE_MULTIPROCESSING = False

import platform
from datetime import datetime

class RaygunMessageBuilder:

    def __init__(self):
        self.raygunMessage = RaygunMessage()

    def new(self):
        return RaygunMessageBuilder()

    def build(self):
        return self.raygunMessage

    def set_machine_name(self, name):
        self.raygunMessage.details['machineName'] = name
        return self

    def set_environment_details(self):
        self.raygunMessage.details['environment'] = {
            "processorCount": (
                multiprocessing.cpu_count() if USE_MULTIPROCESSING else "n/a"
            ),
            "architecture": platform.architecture()[0],
            "cpu": platform.processor(),
            "oSVersion": "%s %s" % (platform.system(), platform.release())
        }
        return self

    def set_exception_details(self, raygunExceptionMessage):
        self.raygunMessage.details['error'] = raygunExceptionMessage
        return self

    def set_client_details(self):
        self.raygunMessage.details['client'] = {
            "name": "raygun4py",
            "version": "2.2.0",
            "clientUrl": "https://github.com/MindscapeHQ/raygun4py"
        }
        return self

    def set_customdata(self, userCustomData):
        if type(userCustomData) is dict:
            self.raygunMessage.details['userCustomData'] = userCustomData
        return self

    def set_tags(self, tags):
        if type(tags) is list or tuple:
            self.raygunMessage.details['tags'] = tags
        return self

    def set_request_details(self, request):
        if request:
            self.raygunMessage.details['request'] = {
              "hostName": request['hostName'],
              "url": request['url'],
              "httpMethod": request['httpMethod'],
              "queryString": request['queryString'],
              "form": request['form'],
              "headers": request['headers'],
              "rawData": request['rawData'],
            }

            if 'ipAddress' in request:
              self.raygunMessage.details['request']['iPAddress'] = request['ipAddress']
            elif 'iPAddress' in request:
              self.raygunMessage.details['request']['iPAddress'] = request['iPAddress']

        return self

    def set_version(self, version):
        self.raygunMessage.details['version'] = version
        return self

    def set_user(self, user):
        if user is not None:
            self.raygunMessage.details['user'] = user

        return self

class RaygunMessage:

    def __init__(self):
          self.occurredOn = datetime.utcnow()
          self.details = { }

class RaygunErrorMessage:

    def __init__(self, exc_type, exc_value, exc_traceback):
        self.className = exc_type.__name__
        self.message = "%s: %s" % (exc_type.__name__, exc_value)
        self.stackTrace = []
        traces = traceback.extract_tb(exc_traceback)

        if traces:
            for t in traces:
                self.stackTrace.append({
                    "lineNumber": t[1],
                    "className": t[2],
                    "fileName": t[0],
                    "methodName": t[3],
                })

        self.data = ""

        if isinstance(exc_value, Exception):
            nestedException = None

            if exc_value.__cause__:
                nestedException = exc_value.__cause__
            elif exc_value.__context__:
                nestedException = exc_value.__context__

            if nestedException is not None:
                self.innerError = RaygunErrorMessage(type(nestedException), nestedException, nestedException.__traceback__)