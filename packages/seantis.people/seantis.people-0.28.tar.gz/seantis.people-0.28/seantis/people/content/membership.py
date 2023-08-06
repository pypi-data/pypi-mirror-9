from plone.dexterity.content import Container


class Membership(Container):

    def get_custom_title(self):
        person = self.person and self.person.to_object

        # this happens if the person is deleted along with its memberships
        # https://github.com/seantis/seantis.people/issues/27
        if not person:
            return self.role

        return u' '.join((self.role, person.title))
