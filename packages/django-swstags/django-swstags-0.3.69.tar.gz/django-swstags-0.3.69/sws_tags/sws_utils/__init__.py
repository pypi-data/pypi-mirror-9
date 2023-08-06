import os
# import datetime
from decimal import Decimal

from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django.utils import simplejson as json
from django_tools.middlewares import ThreadLocal
from datetime import datetime
from datetime import date as datetimedate
from decimal import Decimal
from django.core.serializers import serialize
from django.http import HttpResponse
from django.utils.functional import Promise
import os
# import datetime
from decimal import Decimal

from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django_tools.middlewares import ThreadLocal
from datetime import datetime
from decimal import Decimal
from django.core.serializers import serialize
from django.http import HttpResponse
from django.utils.functional import Promise
import platform

import os
# import datetime
from decimal import Decimal

from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils.encoding import force_unicode
from django_tools.middlewares import ThreadLocal
from datetime import datetime
from decimal import Decimal
from django.core.serializers import serialize
from django.http import HttpResponse
from django.utils.functional import Promise
import platform
from django.utils import simplejson as json

def json_encode(data):
    """
    The main issues with django's default json serializer is that properties that
    had been added to an object dynamically are being ignored (and it also has 
    problems with some models).
    """

    class ComplexEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, complex):
                return [obj.real, obj.imag]
            # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)



    request = ThreadLocal.get_current_request()
    def _any(data):
        ret = None
        # Opps, we used to check if it is of type list, but that fails 
        # i.e. in the case of django.newforms.utils.ErrorList, which extends
        # the type "list". Oh man, that was a dumb mistake!
        if isinstance(data, list):
            ret = _list(data)
        # Same as for lists above.
        elif isinstance(data, dict):
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        # here we need to encode the string as unicode (otherwise we get utf-16 in the json-response)
        elif isinstance(data, basestring):
            ret = unicode(data)
        # see http://code.djangoproject.com/ticket/5868
        elif isinstance(data, Promise):
            ret = force_unicode(data)
        elif isinstance(data, datetime):
            try:
                data=request.session['django_timezone'].normalize(data).strftime('%Y-%m-%d %H:%M:%S')
                ret = force_unicode(data)
            except:
                ret = force_unicode(data)
        elif isinstance(data,datetimedate):
        # elif type(data) == date:
            ret=str(data)
        else:
            ret = data
        return ret
    
    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields if k != '_state']
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret
    
    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret
    
    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret
    
    ret = _any(data)
    return json.dumps(ret, cls=ComplexEncoder) #DateTimeAwareJSONEncoder  #ComplexEncoder

def json_response(data):
    return HttpResponse(json_encode(data), content_type='application/json')

def json_template(data, template_name, template_context):
    """Old style, use JSONTemplateResponse instead of this.
    """
    html = render_to_string(template_name, template_context)
    data = data or {}
    data['html'] = html
    return HttpResponse(json_encode(data), content_type='application/json')


class JSONTemplateResponse(TemplateResponse):
    
    def __init__(self, *args, **kwargs):
        """There are extra arguments in kwargs:
            `data` dict for extra JSON data
            `html_varname` string for specify where rendered template will be
                stored, by default "html"

        Example:
        
            Py-code:
            return JSONTemplateResponse(request, template_name, template_context,
                data={'status': 'ok', 'user': request.user})

            This line will create response:
            {
                "status": "ok",
                "user": {
                    "username": "frol",
                    "first_name": "",
                    "last_name": "",
                    "is_active": true,
                    "email": "qq@qq.qq",
                    "is_superuser": true,
                    "is_staff": true,
                    "last_login": "2012-01-24 18:59:55",
                    "password": "sha1$fffff$1b4d68b3731ec29a797d61658c716e2400000000",
                    "id": 1,
                    "date_joined": "2011-07-09 05:57:21"
                },
                "html": "<rendered HTML>"
            }
            
        WARNING: Be carefull with serialization of model objects. As you can
        see in example, password hash has been serialized.
        """
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'application/json'
        self.data = kwargs.pop('data', dict())
        self.html_varname = kwargs.pop('html_varname', 'html')
        super(JSONTemplateResponse, self).__init__(*args, **kwargs)

    @property
    def rendered_content(self):
        html = super(JSONTemplateResponse, self).rendered_content
        self.data[self.html_varname] = html
        return json_encode(self.data)
