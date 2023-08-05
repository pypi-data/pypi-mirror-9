class PredicSisError(Exception):    
    def __init__(self, message=None, http_body=None, http_status=None, json_body=None):
        super(PredicSisError, self).__init__(message)
        if http_body and hasattr(http_body, 'decode'):
            try:
                http_body = http_body.decode('utf-8')
            except:
                http_body = ('Could not decode body as utf-8. ')
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body