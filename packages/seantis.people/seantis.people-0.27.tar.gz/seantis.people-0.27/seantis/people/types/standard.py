from plone.directives import form
from seantis.people.types.base import PersonBase


class IStandard(form.Schema):
    form.model("standard.xml")


class Standard(PersonBase):
    pass
