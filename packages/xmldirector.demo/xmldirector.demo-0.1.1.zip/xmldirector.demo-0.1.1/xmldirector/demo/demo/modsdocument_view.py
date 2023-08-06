# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
from Products.Five.browser import BrowserView


class MODSDocument(BrowserView):

    def asHTML(self):
        """ Generate a demo PDF """
        return self.context.xml_get('xml_content')
