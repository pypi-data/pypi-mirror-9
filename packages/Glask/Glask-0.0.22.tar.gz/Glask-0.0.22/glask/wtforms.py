from flask.ext import wtf
# noinspection PyProtectedMember
from flask.ext.wtf.form import _is_hidden


class Form(wtf.Form):
    def fields(self):
        return tuple(f for f in self if not _is_hidden(f))
