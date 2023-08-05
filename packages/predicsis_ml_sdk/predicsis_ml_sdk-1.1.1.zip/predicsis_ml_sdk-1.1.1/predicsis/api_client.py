import requests
import predicsis
from predicsis.error import PredicSisError
from xml.dom import minidom
import json

verify_ssl_certs = False
ssl_certs_path='./predicsis.com.crt'

class APIClient(object):
    
    @classmethod
    def request(cls, method, resource, post_data=None):
        predicsis.log(method.upper() + ' ' + predicsis.api_url + resource+ ' [' + str(post_data) + ']', 2)
        headers = {'Accept': 'application/json'}
        if (method == 'post') or (method == 'patch'):
            headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Bearer ' + predicsis.api_token;
        content, code, json = cls.request_full(method, predicsis.api_url + resource, headers, post_data)
        return cls._interpret_response(content, code, json)
        
    @classmethod
    def request_full(cls, method, url, headers, post_data=None, files=None):
        kwargs = {}
        if verify_ssl_certs:
            kwargs['verify'] = ssl_certs_path
        else:
            kwargs['verify'] = False
            try:
                requests.packages.urllib3.disable_warnings()
            except AttributeError:
                predicsis.log('Impossible to shut down the SSL-related warnings - check the version of python and/or requests package.', 0)
        try:
            try:
                result = requests.request(method, url, headers=headers, data=post_data, files=files, timeout=80, **kwargs)
            except TypeError, e:
                raise TypeError('Your "requests" library may be out of date. Error was: %s' % (e,))
            content = result.content
            status_code = result.status_code
            if files == None and not method=='delete':
                jsonn = result.json()
            else:
                jsonn = result
        except Exception, e:
            cls._handle_request_error(e)
        predicsis.log('return status: ' + str(status_code), 2)
        if files==None and not method=='delete':
            predicsis.log(json.dumps(jsonn, indent=4), 3)
        elif not method=='delete':
            xmlResponse = minidom.parseString(result.content)
            predicsis.log(xmlResponse.toprettyxml(indent="\t"), 3)
        return content, status_code, jsonn
    
    @classmethod
    def request_direct(cls, url):
        return requests.get(url)
        
    @classmethod
    def _interpret_response(cls, content, code, json):
        if not (200 <= code < 300):
            cls._handle_api_error(content, code, json)
        return json
        
    @classmethod
    def _handle_api_error(cls, content, code, json):
        msg = ""
        try:
            msg = json['message']
        except KeyError:
            msg = json['error']
        raise PredicSisError(str(json['status']) +' '+ msg, content, code, json)
    
    @classmethod
    def _handle_request_error(cls, e):
        if isinstance(e, requests.exceptions.RequestException):
            msg = ('Unexpected error communicating with PredicSis API. If this problem persists, let us know at support@predicsis.com.')
            err = "%s: %s" % (type(e).__name__, str(e))
        else:
            msg = ('Unexpected error communicating with PredicSis API (looks like a configuration issue). If this problem persists, let us know at support@predicsis.com.')
            err = "A %s was raised" % (type(e).__name__,)
        if str(e):
            err += " with error message %s" % (str(e),)
        else:
            err += " with no error message"
        msg = msg + "\n\n(Network error: %s)" % (err,)
        raise PredicSisError(msg)
