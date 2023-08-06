import json

import requests

from pycloudhub.utils import check_not_blank


class ApplicationInfoError(Exception):
    """
    An exception thrown in case of an issue with accessing CloudHub application information.
    """

    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


class ApplicationNotFoundError(ApplicationInfoError):
    """
    An exception thrown in case of an HTTP 404 Not Found response status code.
    """

    def __init__(self, message='Application Not Found', status_code=404):
        super().__init__(message, status_code)


class ApplicationDeploymentError(Exception):
    """
    An exception thrown in case of an issue with deploying CloudHub application.
    """

    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code

class CloudHubApp:
    BASE_URL = 'https://cloudhub.io/api/applications/'

    def __init__(self, name, user_name, password):
        check_not_blank(name, 'The application name must not be blank')
        check_not_blank(user_name, 'The user name must not be blank')
        check_not_blank(password, 'The password must not be blank')

        self.name = name
        self.user_name = user_name
        self.password = password
        self.base_url = CloudHubApp.BASE_URL

    def _make_url(self, path):
        return self.base_url + path

    def _get(self, path):
        return requests.get(self._make_url(path), auth=(self.user_name, self.password))

    def _put(self, path, **kwargs):
        return requests.put(self._make_url(path), auth=(self.user_name, self.password), **kwargs)

    def get_app_info(self):

        response = self._get(self.name)
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 404:
            raise ApplicationNotFoundError("Application [{0}] doesn't exist".format(self.name))
        else:
            code = response.status_code
            raise ApplicationInfoError(
                'Unable to retrieve information for application [{0}] (Status Code: {1})'.format(self.name, code),
                code
            )

    def deploy(self, file):

        app_info = self.get_app_info()

        payload = {
            "muleVersion": app_info["muleVersion"],
            "workers": str(app_info["workers"]),
            "workerType": app_info["workerType"]
        }

        properties = app_info["properties"]

        for prop in properties:
            payload["properties." + prop] = properties[prop]

        response = self._put(self.name, data=payload, files={'file': file})
        if response.status_code != 200:
            raise ApplicationDeploymentError(
                "Failed to deploy application [{0}] (Status Code: {1}".format(self.name, response.status_code),
                response.status_code
            )