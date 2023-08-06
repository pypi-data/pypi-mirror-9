################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from Products.Five.browser import BrowserView
from xmldirector.plonecore.dx.xpath_field import get_all_fields
from xmldirector.plonecore.dx.xml_field import XMLText

class Validation(BrowserView):

    @property
    def validator_registry(self):
        """ Return validators for dropdown """
        from zope.component import getUtility
        from xmldirector.plonecore.interfaces import IValidatorRegistry
        return  getUtility(IValidatorRegistry)

    def validators(self):
        """ Return validators for dropdown """
        return self.validator_registry.entries()

    def xml_fields(self):
        result = list()
        for name, field in get_all_fields(self.context).items():
            if isinstance(field, XMLText):
                result.append(name)
        return result

    def validate(self, fieldname, validator):
        """ Validate the content of the XMLText field ``fieldname``
            against the given ``validator`` (concatenated as "<family>::<name",
            see validation.pt.
        """
        validator = self.validator_registry.get_validator(*validator.split('::'))
        xml = self.context.xml_get(fieldname)
        result = validator.validate(xml)
        if not result:
            self.context.plone_utils.addPortalMessage('Validation failed ({})'.format(result.errors), 'error')
        else:
            self.context.plone_utils.addPortalMessage('Validation OK')
        self.request.response.redirect(self.context.absolute_url() + '/@@validation')
