__version__ = '0.1.0'

from flask.ext.wtf import Form
import wtforms
from wtforms_alchemy import model_form_factory

from project import db


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    """
    wtforms-alchemy Flask-WTF compatible base model form.
    Copied from:
    http://wtforms-alchemy.readthedocs.org/en/latest/advanced.html#using-wtforms-alchemy-with-flask-wtf
    """

    @classmethod
    def get_session(self):
        return db.session


BaseModelWtfForm = model_form_factory(wtforms.Form)


class ModelWtfForm(BaseModelWtfForm):
    """
    Same as ModelForm (also defined in this file), but inherited
    from regular wtforms base class, instead of Flask-WTF base
    class (for when one wants a non-Flask-WTF wtforms form that
    works with wtforms-alchemy).
    """

    @classmethod
    def get_session(self):
        return db.session


class ModelFieldList(wtforms.FieldList):
    """
    Flask-WTF FieldLists with Dynamic Entries.
    Copied from:
    https://gist.github.com/kageurufu/6813878
    """

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop("model", None)
        super(ModelFieldList, self).__init__(*args, **kwargs)
        if not self.model:
            raise ValueError("ModelFieldList requires model to be set")

    def populate_obj(self, obj, name):
        while len(getattr(obj, name)) < len(self.entries):
            newModel = self.model()
            db.session.add(newModel)
            getattr(obj, name).append(newModel)
        while len(getattr(obj, name)) > len(self.entries):
            db.session.delete(getattr(obj, name).pop())
        super(ModelFieldList, self).populate_obj(obj, name)
