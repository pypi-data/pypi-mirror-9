# encoding:utf-8
from copy import deepcopy
from logging import getLogger

import requests
from schematics.models import Model
from schematics.types import BooleanType
from schematics.types.compound import ModelType


logger = getLogger('pipedrive.api')

BASE_URL = 'https://api.pipedrive.com/v1'


class PipedriveAPI(object):
    resource_registry = {}

    def __init__(self, api_token):
        self.api_token = api_token

    def __getattr__(self, item):
        try:
            return PipedriveAPI.resource_registry[item](self)
        except KeyError:
            raise AttributeError('No resource is registered under that name.')

    def send_request(self, method, path, params=None, data=None):
        params = params or {}
        params['api_token'] = self.api_token
        url = BASE_URL + path
        try:
            return requests.request(method, url, params=params, data=data)
        except Exception as err:
            logger.exception("Request failed: %s" % err.message)
            raise err

    @staticmethod
    def register_resource(resource_class):
        PipedriveAPI.resource_registry[
            resource_class.API_ACESSOR_NAME] = resource_class


class BaseResource(object):
    """Common ground for all api resources.

    Attributes:
        API_ACESSOR_NAME(str): The property name that this resource will be
            accessible from the Api object (i.e. "sms" ) api.sms.liist()
        LIST_REQ_PATH(str): The request path component for the list view
            (listing and creation)
        DETAIL_REQ_PATH(str): The request path component for the detail view
            (deletion, updating and detail)
    """

    MODEL_CLASS = Model
    API_ACESSOR_NAME = ''
    LIST_REQ_PATH = None
    DETAIL_REQ_PATH = None
    FIND_REQ_PATH = None

    def __init__(self, api):
        self.api = api
        setattr(self.api, self.API_ACESSOR_NAME, self)

    def send_request(self, method, path, params, data):
        response = self.api.send_request(method, path, params, data)
        if 200 <= response.status_code < 400:
            self.process_success(response)
        else:
            self.process_error(response)
        return response

    def process_success(self, data):
        pass

    def process_error(self, response):
        pass

    def _create(self, params=None, data=None):
        return self.send_request('POST', self.LIST_REQ_PATH, params, data)

    def _list(self, params=None, data=None):
        return self.send_request('GET', self.LIST_REQ_PATH, params, data)

    def _delete(self, resource_ids, params=None, data=None):
        url = self.DETAIL_REQ_PATH.format(id=resource_ids)
        return self.send_request('DELETE', url, params=None, data=None)

    def _update(self, resource_ids, params=None, data=None):
        url = self.DETAIL_REQ_PATH.format(id=resource_ids)
        return self.send_request('PUT', url, params=None, data=None)

    def _detail(self, resource_ids, params=None, data=None):
        url = self.DETAIL_REQ_PATH.format(id=resource_ids)
        return self.send_request('GET', url, params, data)

    def _find(self, term, params=None, data=None):
        params = params or {}
        params['term'] = term
        return self.send_request('GET', self.FIND_REQ_PATH, params, data)


class CollectionResponse(Model):
    items = []
    success = BooleanType()

    def __init__(self, response_data, model_class):
        """response_data can be either a Response object or a list containing
           the data for each returned object. Useful if the response must be
           processed before the CollectionResponse is built"""
        super(CollectionResponse, self).__init__()
        if isinstance(response_data, list):
            items = response_data
        else:
            serialized = response_data.json()
            items = serialized['data'] or []
        self.items = [dict_to_model(one, model_class) for one in items]


def dict_to_model(data, model_class):
    """Converts the json response to a full fledge model
    The schematics model constructor is strict. If it sees keys that it
    doesn't know about it will raise an exception. This is a problem, both
    because we won't model all of the data at first, but also because the
    lib would break on new fields being returned.
    Therefore we inspect the model class and remove all keys not present
    before constructing the model.
    Args:
        data(dict): The json response data as returned from the API.
        model_class(Model): The schematics model to instantiate
    Returns:
        Model: With the populated data
    """
    if data is None:
        return None
    data = deepcopy(data)
    fields = model_class.fields
    model_keys = set([fields[field_name].serialized_name or field_name\
        for field_name in fields])
    safe_keys = set(data.keys()).intersection(model_keys)
    safe_data = {key: data[key] for key in safe_keys}
    return model_class(raw_data=safe_data)
