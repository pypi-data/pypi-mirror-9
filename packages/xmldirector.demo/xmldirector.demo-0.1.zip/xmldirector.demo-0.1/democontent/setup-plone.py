
import sys
import os
import lxml.etree
import plone.api
import grampg
import transaction
import pkg_resources
from Products.CMFPlone.factory import addPloneSite
from AccessControl.SecurityManagement import newSecurityManager
from xmldirector.plonecore.interfaces import IWebdavSettings
from pp.client.plone.interfaces import IPPClientPloneSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility



mode = sys.argv[-1]
if mode == 'docker':
    webdav_url = u'http://localhost:8080/exist/webdav/db'
elif mode == 'local':
    webdav_url = u'http://localhost:6080/exist/webdav/db'
else:
    raise ValueError('mode must be "local" or "docker"')


admin_pw = grampg.PasswordGenerator().of().between(100, 200, 'letters').done().generate()

uf = app.acl_users
user = uf.getUser('admin')

#uf._doChangeUser('admin', admin_pw, ('Manager',), ())
newSecurityManager(None, user.__of__(uf))
if 'xml-director' in app.objectIds():
    app.manage_delObjects('xml-director')

addPloneSite(app, 'xml-director', create_userfolder=True, extension_ids=['plonetheme.sunburst:default', 'xmldirector.demo:default', 'pp.client.plone:default'])
site = app['xml-director']
site.manage_delObjects(['events', 'news', 'Members'])
pr = site.portal_registration
pr.addMember('demo', 'demo', roles=('Site Administrator',))

registry = getUtility(IRegistry)
settings = registry.forInterface(IWebdavSettings)
settings.webdav_url = webdav_url
settings.webdav_username = u'admin'
settings.webdav_password = u'admin'

settings = registry.forInterface(IPPClientPloneSettings)
settings.server_url = u'https://pp-server.zopyx.com'
settings.server_username = u'demo'
settings.server_password = u'demo'

import_dir = os.path.join(pkg_resources.get_distribution('xmldirector.demo').location, 'democontent', 'images')

image = plone.api.content.create(type='Image', container=site, id='logo')
image.setImage(open(os.path.join(import_dir, 'xmldirector.png'), 'rb').read())
image.setExcludeFromNav(True)
image.reindexObject()


frontpage_text = """
<img src="logo" width="400" style="display: none"/>
<br/>
<br/>
<p>Login with username <b>demo</b> and password <b>demo</b>.</p>
<br/>
<p>
<ul>
<li><a href="http://pythonhosted.org/xmldirector.plonecore/demo.html">Demo documentation</a</li>
<li><a href="http://pythonhosted.org/xmldirector.plonecore/">Complete XML Director documentation</a</li>
<li><a href="http://www.xml-director.info">XML Director project site</a></li>
</ul>
</p>
"""

page = site['front-page']
page.setTitle('Welcome to the XML Director demo site')
page.setDescription(None)
page.setText(frontpage_text)
page.setPresentation(False)
page.reindexObject()

folder = plone.api.content.create(type='Folder', container=site, id='bible', title='Bible XML')
dok = plone.api.content.create(
    type='xmldirector.demo.bibledocument',
    container=folder,
    id='bible-en',
    title='Bible EN')

import_dir = os.path.join(pkg_resources.get_distribution('xmldirector.demo').location, 'democontent', 'bible')
bible_content = open(os.path.join(import_dir, 'index.xml')).read()
dok.xml_set('xml_content', unicode(bible_content, 'utf-8'))
dok.reindexObject()


folder = plone.api.content.create(type='Folder', container=site, id='shakespeare', title='Shakespeare XML')
import_dir = os.path.join(pkg_resources.get_distribution('xmldirector.demo').location, 'democontent', 'shakespeare')

for name in sorted(os.listdir(import_dir)):

    if not name.endswith('.xml'):
        continue

    fname = os.path.join(import_dir, name)
    with open(fname, 'rb') as fp:
        xml = unicode(fp.read(), 'utf8')
        root = lxml.etree.fromstring(xml.encode('utf8'))
        title = root.xpath('//title')[0].text
        dok = plone.api.content.create(
                type='xmldirector.demo.xmldocument',
                container=folder,
                id=name,
                title=title)

        dok.xml_set('xml_content', xml)
        dok.xml_xpath = u'field=xml_content,xpath=//title/text()'
        dok.reindexObject()
print 'commited'
transaction.commit()
