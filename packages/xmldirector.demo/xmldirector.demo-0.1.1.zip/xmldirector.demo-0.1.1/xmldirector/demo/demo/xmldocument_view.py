# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
import lxml.html.clean
import zope.component
from Products.Five.browser import BrowserView
from xmldirector.plonecore.interfaces import ITransformerRegistry
from xmldirector.plonecore.transformation import Transformer


class XMLDocument(BrowserView):

    def xslt_transform(self, fieldname, family, stylesheet_name):
        """ Perform an XSLT registration for the XML stored on the current
            context object under a given registered XSLT transformation.
        """

        registry = zope.component.getUtility(ITransformerRegistry)
        xml = self.context.xml_get(fieldname)
        if not xml:
            return u''

        T = Transformer(steps=[(family, stylesheet_name)])
        html = T(xml, input_encoding='utf8')
        cleaner = lxml.html.clean.Cleaner()
        return cleaner.clean_html(html)

    def asHTML(self):
        """ Generate a demo PDF """
        return self.xslt_transform('xml_content', 'demo', 'shakespeare.xsl')
