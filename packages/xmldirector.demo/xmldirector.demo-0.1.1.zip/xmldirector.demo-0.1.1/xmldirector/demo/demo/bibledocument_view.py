# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


import lxml.etree
from Products.Five.browser import BrowserView


class BibleDocument(BrowserView):

    def asHTML(self):
        """ Generate a demo PDF """
        xml = self.context.xml_get('xml_content')
        root = lxml.etree.fromstring(xml)
        for book in root.xpath('//BIBLEBOOK')[1:]:
            book.getparent().remove(book)
        return lxml.etree.tostring(root)
