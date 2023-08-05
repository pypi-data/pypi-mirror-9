from zope.interface import Interface, Attribute
from seantis.people.interfaces import ISeantisPeopleSpecific


class ISeantisKantonsratSpecific(ISeantisPeopleSpecific):
    pass


class IMotion(Interface):

    title = Attribute("Title of the motion.")
    url = Attribute("Url pointing to the motion.")


class IMotionsProvider(Interface):
    """ Manages a list of motions external to the module. Those motions are
    currently available if seantis.kantonsrat is used in conjuction with
    https://github.com/4teamwork/geschaeftsverzeichnis/

    """

    def motions_by_entity(self, entity_uuid):
        """ Returns a list of motions providing IMotion. The entity_uuid
        may be a any uuid though it would currently be one of either a
        Kantonsrat or an organization.

        """
