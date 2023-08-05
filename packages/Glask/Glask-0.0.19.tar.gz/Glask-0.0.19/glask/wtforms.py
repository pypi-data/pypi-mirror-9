from flask.ext import wtf
# noinspection PyProtectedMember
from flask.ext.wtf.form import _is_hidden, _Auto
import inflection


class Form(wtf.Form):
    def __init__(self, formdata=_Auto, obj=None, prefix='', csrf_context=None,
                 secret_key=None, csrf_enabled=None, *args, **kwargs):
        self.form_id = inflection.underscore(self.__class__.__name__)
        if not prefix:
            prefix = self.form_id + '_'
        super(Form, self).__init__(formdata=formdata, obj=obj, prefix=prefix,
                                   csrf_context=csrf_context,
                                   secret_key=secret_key,
                                   csrf_enabled=csrf_enabled, *args, **kwargs)

    def fields(self):
        return tuple(f for f in self if not _is_hidden(f))
