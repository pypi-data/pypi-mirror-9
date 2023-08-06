from plone.app.layout.globals.layout import LayoutPolicy

from seantis.people.interfaces import IList


class ListLayoutPolicy(LayoutPolicy):
    """ Adds the currently used type to the list view as body class."""

    def bodyClass(self, template, view):
        """Returns the CSS class to be used on the body tag.
        """
        if IList.providedBy(self.context):
            used_type = self.context.used_type()
        else:
            used_type = None

        body_class = LayoutPolicy.bodyClass(self, template, view)

        if used_type is not None:
            # e.g. seantis.people.standard becomes seantis-people-standard-list
            type_class = '{}-list'.format(used_type.id.replace('.', '-'))
            return ' '.join((body_class, type_class))
        else:
            return body_class
