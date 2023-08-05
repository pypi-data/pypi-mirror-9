# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from Products.Five.browser import BrowserView


class BibleDocument(BrowserView):

    def asXML(self):
        """ Generate a demo PDF """
        return self.context.xml_get('xml_content')
