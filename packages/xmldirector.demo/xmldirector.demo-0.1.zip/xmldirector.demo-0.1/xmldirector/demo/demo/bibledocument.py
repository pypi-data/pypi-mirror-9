# -*- coding: utf-8 -*-

################################################################
# xmldirector.plonecore
# (C) 2014,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

"""
A sample Dexterity content-type implementation using
all XML field types.
"""


from zope.interface import implements
from plone.dexterity.content import Item
from plone.supermodel import model

from xmldirector.plonecore.i18n import MessageFactory as _

from xmldirector.plonecore.dx import dexterity_base
from xmldirector.plonecore.dx.xml_field import XMLText


class IBibleDocument(model.Schema):

    xml_content = XMLText(
        title=_(u'XML Content'),
        required=False
    )


class BibleDocument(Item, dexterity_base.Mixin):

    implements(IBibleDocument)
