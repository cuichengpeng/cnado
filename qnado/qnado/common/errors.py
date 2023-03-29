from qnado.common import enums

class ApiException(Exception):
    def __init__(self, errmsg=None, data=None, code=None):
        self.message = errmsg or ""
        self.data = data
        self.code = code if code else enums.AJAX_FAIL_NORMAL
    
    def __str__(self):
        return self.message
