from AccessControl import ClassSecurityInfo
from AccessControl.SpecialUsers import nobody
from AccessControl.class_init import InitializeClass
from AccessControl.requestmethod import postonly
from DateTime import DateTime
from DocumentTemplate.DT_Util import html_quote
from OFS import Folder
from OFS.interfaces import IOrderedContainer
from PNLBase import PNLContentBase
from PNLPermissions import ChangeNewsletter
from PNLPermissions import ChangeNewsletterTheme
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import ListFolderContents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDefault.SkinnedFolder import SkinnedFolder
from Products.CMFPlone.PloneFolder import OrderedContainer
from Products.CMFPlone.utils import safe_unicode
from Products.PloneGazette import _
from Products.PloneGazette.interfaces import INewsletter
from elementtree import ElementTree
from elementtree import HTMLTreeBuilder
from email.Header import Header
from urlparse import urlparse
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements
from zope.structuredtext import stx2html as format_stx

import StringIO
import cStringIO
import email.Message
import email.Utils
import logging
import re
import traceback
import transaction

logger = logging.getLogger('PloneGazette')

#################
## The factory ##
#################


def addNewsletter(self, id, title='', REQUEST={}):
    """
    Factory method for a Newsletter object
    """
    obj = Newsletter(id, title)
    self._setObject(id, obj)
    getattr(self, id)._post_init()
    if 'RESPONSE' in REQUEST:
        return REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_main')

#################################
## The Newsletter content type ##
#################################

lynx_file_url = re.compile(r'file://localhost[^%]+%\(url\)s')


class Newsletter(SkinnedFolder, OrderedContainer, DefaultDublinCoreImpl, PNLContentBase):
    """Newsletter class"""

    # if hasZopeOrderedSupport:
    #     __implements__ = (IOrderedContainer, IZopeOrderedContainer)
    # else:
    __implements__ = (IOrderedContainer,)

    ########################################
    ## Registration info for portal_types ##
    ########################################

    factory_type_information = {
        'id': 'Newsletter',
        'portal_type': 'Newsletter',
        'meta_type': 'Newsletter',
        'description': 'A newletter (has no sense oudside a NewsletterTheme object)',
        'content_icon': 'Newsletter.gif',
        'product': 'PloneGazette',
        'factory': 'addNewsletter',
        'immediate_view': 'folder_listing',
        'global_allow': 0,
        'filter_content_types': 1,
        'allowed_content_types': ('Section', 'Topic', 'NewsletterReference', 'NewsletterRichReference'),
        'actions': (
            {
                'id': 'view',
                'name': 'View',
                'action': 'string:${object_url}/Newsletter_view',
                'permissions': (View, ),
                'category': 'object'
                },
            {
                'id': 'edit',
                'name': 'Edit',
                'action': 'string:${object_url}/Newsletter_editForm',
                'permissions': (ChangeNewsletter,),
                'category': 'object'
                },
            {
                'id': 'test',
                'name': 'Test',
                'action': 'string:${object_url}/Newsletter_testForm',
                'permissions': (ChangeNewsletter,),
                'category': 'object'
                },

            {
                'id': 'send',
                'name': 'Send',
                'action': 'string:${object_url}/Newsletter_sendForm',
                'permissions': (ChangeNewsletter,),
                'category': 'object'
                },
            ),
            'aliases': {
                '(Default)': 'Newsletter_view',
                'view': 'Newsletter_view',
                'index.html': '',
                'edit': 'base_edit',
                'properties': 'base_metadata',
                'sharing': 'folder_localrole_form',
            },
        }

    ###########################
    ## Basic class behaviour ##
    ###########################
    implements(INewsletter)
    meta_type = factory_type_information['meta_type']
    manage_options = Folder.Folder.manage_options

    # Standard security settings
    security = ClassSecurityInfo()
    security.declareObjectProtected(View)
    #security.declareProtected(ChangeNewsletter, "dummyMethod_editPermission")

    _stx_level = 1
    cooked_text = text = text_format = ''
    _new_object = False
    _dynamic_content = None

    # Init method
    security.declarePrivate('__init__')
    def __init__(self, id, title='', description='', text_format='', text='', dateEmitted=None):
        """__init__(self, id, title='')"""

        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title
        self.description = description
        self._edit(text=text, text_format=text_format)
        self.setFormat(text_format)
        self.dateEmitted = dateEmitted
        self._new_object = True
        self._dynamic_content = None
        return

    security.declarePrivate('_post_init')
    def _post_init(self):
        """
        _post_init(self) => Post-init method (that is, method that is called AFTER the class has been set into the ZODB)
        """

        self.indexObject()
        return

    #############################
    ## Content editing methods ##
    #############################

    def _edit(self, text, text_format=''):
        """
        """
        level = self._stx_level
        if not text_format:
            text_format = self.text_format

        if self.text_format:
            self.text_format = text_format
        if text_format == 'html':
            self.text = self.cooked_text = text
        elif text_format == 'plain':
            self.text = text
            self.cooked_text = html_quote(text).replace('\n', '<br />')
        else:
            self.cooked_text = format_stx(text, level=level)
            self.text = text

    # Edit method (change this to suit your needs)
    # This edit method should only change attributes that are neither 'id' or metadatas.
    security.declareProtected(ChangeNewsletter, 'edit')
    def edit(self, title='', text='', dateEmitted=None, text_format=''):
        """
        edit(self, text = '') => object modification method
        """
        # level = self._stx_level
        # Change attributes
        if title:
            self.title = title
        if not dateEmitted:
            # if dateEmitted is cleared, clear dynamic content attribute
            # to render newsletter again
            self._dynamic_content = None
        else:
            try:
                self.dateEmitted = DateTime(dateEmitted)
            except:
                self.dateEmitted = None

        self.setFormat(text_format)
        self._edit(text=text, text_format=text_format)

        if self._new_object and title:
            plone_tool = getToolByName(self, 'plone_utils')
            newid = plone_tool.normalizeString(title)
            parent = self.aq_parent
            if newid not in parent.objectIds():
                transaction.savepoint(optimistic=True)
                self._v_cp_refs = 1
                parent.manage_renameObject(self.id, newid)
                self._setId(newid)

        self._new_object = False

        # Reindex
        self.reindexObject()
        return

    security.declareProtected(View, 'CookedBody')
    def CookedBody(self, stx_level=None, setLevel=0):
        """
        """
        if (self.text_format == 'html' or self.text_format == 'plain'
            or (stx_level is None)
            or (stx_level == self._stx_level)):
            return self.cooked_text
        else:
            cooked = format_stx(self.text, stx_level)
            if setLevel:
                self._stx_level = stx_level
                self.cooked_text = cooked
            return cooked

    security.declareProtected(View, 'Format')
    def Format(self):
        """
        """
        if self.text_format == 'html':
            return 'text/html'
        else:
            return 'text/plain'

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat(self, format):
        """
        """
        value = str(format)
        if value == 'text/html' or value == 'html':
            self.text_format = 'html'
        elif value == 'text/plain':
            if self.text_format not in ('structured-text', 'plain'):
                self.text_format = 'structured-text'
        elif value == 'plain':
            self.text_format = 'plain'
        else:
            self.text_format = 'structured-text'

    ############################
    ## portal_catalog support ##
    ############################

    security.declareProtected(View, 'SearchableText')
    def SearchableText(self):
        "Returns a concatination of all searchable text"

        ret = "%s %s %s" % (self.Title(),
                          self.Description(),
                          self.text)
        return ret

    ###################
    security.declarePrivate('changeRelativeToAbsolute')
    def changeRelativeToAbsolute(self, text):
        """
            Kupu, TinyMCE and other editors insert relative URLS for links, images and anchors in content.
            Those links don't work in certain mailclients. This is where this method comes in.
            This changes relative links to absolute ones, without base-tags, because that doesn't work
            in all mailclients.
        """
        tree = HTMLTreeBuilder.TreeBuilder(encoding='utf-8')

        # add a root node for the parser
        tree.feed('<div>%s</div>' % text)
        rootnode = tree.close()

        # add /view to current_url so all links are correct
        current_url = "%s/view" % self.absolute_url()
        parsed_url = urlparse(current_url)

        for x in rootnode.getiterator():
            current_keys = x.keys()
            # fix links and anchors
            if x.tag == "a" and 'href' in current_keys:
                # Ignore mailto links
                if x.attrib['href'].startswith('mailto:'):
                    continue
                # internal-link is not always set as a class on internal-links..
                # Or, there was a period where it wasn't set by everything at least.
                if "href" in current_keys:
                    linksToParent = x.attrib['href'].startswith('../')
                if "href" in current_keys and ("class" in current_keys or linksToParent):
                    if linksToParent or x.attrib['class'] == "internal-link":
                        href = x.attrib['href']
                        relative_part = "/".join(parsed_url[2].split('/')[0:(len(parsed_url[2].split('/')) - len(href.split("../")))])
                        x.attrib['href'] = "%s://%s%s/%s" % (parsed_url[0], parsed_url[1], relative_part, href.split("../")[-1])

                elif "href" in current_keys:
                    # plone 2.5 uses .# for anchors, so we replace this with #
                    if ".#" in x.attrib['href']:
                        x.attrib['href'] = x.attrib['href'].replace('.#', '#')
                    else:
                        # Plone 2.5. and later version does not mark internal links with internal-link class
                        href = x.attrib['href']
                        if href.find('http://') != 0 and not href.find('https://') == 0:
                            relative_part = "/".join(parsed_url[2].split('/')[0:(len(parsed_url[2].split('/')) - len(href.split("../")))])
                            x.attrib['href'] = "%s://%s%s/%s" % (parsed_url[0], parsed_url[1], relative_part, href.split("../")[-1])

            # fix images
            elif x.tag == "img":
                if "src" in current_keys:
                    src = x.attrib['src']

                    # fix only relative links
                    if src.find('http://') != 0 and not src.find('https://') == 0:
                        relative_part = "/".join(parsed_url[2].split('/')[0:(len(parsed_url[2].split('/')) - len(src.split("../")))])
                        x.attrib['src'] = "%s://%s%s/%s" % (parsed_url[0], parsed_url[1], relative_part, src.split("../")[-1])

        tree = ElementTree.ElementTree(rootnode)
        output = StringIO.StringIO()
        try:
            tree.write(output)
        except TypeError:
            raise TypeError("Could not serialize ElementTree around:\n%s" %
                            '\n'.join(output.getvalue().splitlines()[-2:]))
        text = output.getvalue()
        output.close()

        return text

    security.declarePublic('renderTextHTML')
    def renderTextHTML(self, html=True, force=False, footer_url=None, REQUEST=None):
        """Makes the HTML part for MUA of the newsletter
        """
        theme = self.getTheme()
        template = theme.getRenderTemplate()

        vars = {'header': theme.newsletterHeader,
                'footer': theme.newsletterFooter}

        if footer_url is None:
            footer_url = '%(url)s'

        for key in vars:
            try:
                vars[key] = vars[key] % {
                    'url': footer_url,
                    'newsletter_url': self.absolute_url(),
                    'title': self.title,
                    }
            except ValueError:
                pass

        # fix relative links
        text = self.changeRelativeToAbsolute(self.cooked_text)

        data = template(id=self.id, body=text,
                        description=self.description,
                        newsletterHeader=vars['header'],
                        newsletterFooter=vars['footer'],
                        newsletterStyle=self.newsletterStyle,
                        html=html, date=self.dateEmitted, force=force)

        data = safe_unicode(data)

        if theme.alternative_portal_url:
            portal_url = getToolByName(self, 'portal_url')()
            data = data.replace(portal_url, theme.alternative_portal_url)

        if REQUEST is not None:
            # Called directly from the web; set content-type
            # The publisher will then re-encode for us
            charset = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
            REQUEST.RESPONSE.setHeader(
                'content-type',
                'text/html; charset={0}'.format(charset)
            )

        return data

    security.declarePublic('renderTextPlain')
    def renderTextPlain(self, force=False, footer_url=None, REQUEST=None):
        """Makes the text/plain part for MUA of the newsletter"""
        html = self.renderTextHTML(html=False, force=force, footer_url=footer_url)
        charset = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        # portal_tranforms (at least lynx transform) requires encoded data
        html = html.encode(charset)  # encodes everything, good enough

        # Convert to text/html, preferring lynx_dump if available
        transform_tool = getToolByName(self, 'portal_transforms')
        lynxAvailable = (
            'lynx_dump' in transform_tool.objectIds() and
            transform_tool.lynx_dump.title != 'BROKEN')
        if lynxAvailable:
            # Hackery ahead! We'll tell lynx what encodings to use
            # TODO: fix portal_transforms to deal with encodings
            if not hasattr(transform_tool.lynx_dump, '_v_transform'):
                transform_tool.lynx_dump._load_transform()
            transform = transform_tool.lynx_dump._v_transform
            oldargs = transform.binaryArgs
            transform.binaryArgs += ' -assume_charset={0}'.format(charset)
            transform.binaryArgs += ' -display_charset={0}'.format(charset)

            text = transform_tool('lynx_dump', html)

            transform.binaryArgs = oldargs

            if footer_url is None:
                # fixup URL references
                text = lynx_file_url.sub('%(url)s', text)
            text = safe_unicode(text).replace('References', self.translate(_(u'References')))
        else:
            text = transform_tool.convertToData('text/plain', html)

        if REQUEST is not None:
            # called directly from the web; set content-type
            # The publisher will then re-encode for us
            REQUEST.RESPONSE.setHeader(
                'Content-Type',
                'text/plain; charset={0}'.format(charset)
            )

        return safe_unicode(text)

    security.declarePublic('renderTextHTMLEncoded')
    def renderTextHTMLEncoded(self, html=True, force=False, footer_url=None, REQUEST=None):
        return self.renderTextHTML(html=html, force=force, footer_url=footer_url, REQUEST=REQUEST).encode(self.ploneCharset())

    security.declarePublic('renderTextPlainEncoded')
    def renderTextPlainEncoded(self, html=True, force=False, footer_url=None, REQUEST=None):
        return self.renderTextPlain(html=html, force=force, footer_url=footer_url, REQUEST=REQUEST).encode(self.ploneCharset())

    security.declareProtected(ChangeNewsletter, 'testSendToMe')
    def testSendToMe(self, REQUEST=None):
        """Sends HTML/mixed and plain text newsletter to the author"""
        if REQUEST is None:
            REQUEST = self.REQUEST
        theme = self.getTheme()
        email = theme.testEmail
        editurl = theme.absolute_url() + '/xxx'

        # We want to test the unsubscribe url too and we asume the test subscriber is locade in the theme
        for subscriber in theme.objectValues('Subscriber'):
            if subscriber.Title() == email:
                si = subscriber.mailingInfo()
                # si is None if user is inactive
                if si is not None:
                    editurl = si[2]
                break

        recipients = [(email, 'HTML', editurl), (email, 'Text', editurl)]
        # force fresh rendering of the template - do not use dynamic content stored in instance.
        errors = self.sendToRecipients(recipients, force=True)
        return self.Newsletter_testForm(errors=errors, sent=1)

    ########################
    ## Sending newsletter ##
    ########################

    security.declareProtected(ChangeNewsletter, 'sendToRecipients')
    def sendToRecipients(self, recipients, force=False):
        """Send the newsletter to a list of recipients

        switched to email.Message.Message
        recipients is a list of tuples in the form:
        [(email, format, editurl),...]
        email is the mail address
        format is 'HTML' to receive HTML/mixed mail
        editurl is the user preference URL"""

        htmlTpl = self.renderTextHTML(force=force)
        hasurl = '%(url)s' in htmlTpl
        plaintextTpl = self.renderTextPlain(force=force)
        theme = self.getTheme()
        mailFrom = theme.authorEmail
        charset = getUtility(ISiteRoot).getProperty('email_charset', 'utf-8')
        errors = []

        mailMethod = theme.sendmail

        titleForMessage = str(Header(safe_unicode(self.title), charset))

        portal_url = getToolByName(self, 'portal_url')()
        for mailTo, format, editurl in recipients:
            if theme.alternative_portal_url:
                editurl = editurl.replace(portal_url,
                                          theme.alternative_portal_url)
            mainMsg = email.Message.Message()
            mainMsg["To"] = mailTo
            mainMsg["From"] = mailFrom
            mainMsg["Subject"] = titleForMessage
            mainMsg["Date"] = email.Utils.formatdate(localtime=1)
            mainMsg["Message-ID"] = email.Utils.make_msgid()
            mainMsg["Mime-version"] = "1.0"

            if format == 'HTML':
                new_htmlTpl = htmlTpl
                if hasurl:
                    new_htmlTpl = new_htmlTpl.replace('%(url)s', editurl)

                new_plaintextTpl = plaintextTpl
                if hasurl:
                    new_plaintextTpl = new_plaintextTpl.replace('%(url)s', editurl)
                mainMsg["Content-type"] = "multipart/alternative"
                #mainMsg.preamble="This is the preamble.\n"
                mainMsg.epilogue = "\n"  # To ensure that message ends with newline

                # plain
                secondSubMsg = email.Message.Message()
                secondSubMsg.add_header("Content-Type", "text/plain", charset=charset)
                secondSubMsg["Content-Disposition"] = "inline"
                secondSubMsg.set_payload(safe_unicode(new_plaintextTpl).encode(charset), charset)
                mainMsg.attach(secondSubMsg)
                # html
                subMsg = email.Message.Message()
                subMsg.add_header("Content-Type", "text/html", charset=charset)
                subMsg["Content-Disposition"] = "inline"
                subMsg.set_payload(safe_unicode(new_htmlTpl).encode(charset), charset)
                mainMsg.attach(subMsg)
            else:
                new_plaintextTpl = plaintextTpl
                if hasurl:
                    new_plaintextTpl = new_plaintextTpl.replace('%(url)s', editurl)
                mainMsg["Content-type"] = "text/plain"
                mainMsg.set_payload(safe_unicode(new_plaintextTpl).encode(charset), charset)
                mainMsg.epilogue = "\n"  # To ensure that message ends with newline

            try:
                mailMethod(mailFrom, (mailTo,), mainMsg, subject=titleForMessage)
            except Exception, e:
                errors.append(mailTo)
                tbfile = cStringIO.StringIO()
                traceback.print_exc(file=tbfile)
                logger.warning('Error when sending to %s\n%s' % (mailTo, tbfile.getvalue()))
                tbfile.close()
        return errors

    security.declareProtected(ChangeNewsletter, 'sendToSubscribers')
    @postonly
    def sendToSubscribers(self, REQUEST=None):
        """Sends that newsletter to all subscribers and extra recipients"""
        theme = self.getTheme()
        recipients = theme.mailingInfos()
        # we are sending to all recipients. Render dynamic content and store it persistently
        self._dynamic_content = self.render_dynamic_content(html=True)
        errors1 = self.sendToRecipients(recipients)
        recipients = theme.getExtraRecipients()
        errors2 = self.sendToRecipients(recipients)
        self.dateEmitted = DateTime()
        if REQUEST is not None:
            if errors1 or errors2:
                statusMsg = translate(u'SMTP server related errors', domain='plonegazette', context=REQUEST)  # !: display recipient
            else:
                statusMsg = translate(u'The newsletter has been sent.', domain='plonegazette', context=REQUEST)
            self.plone_utils.addPortalMessage(statusMsg)
            return self.Newsletter_sendForm(errors1=errors1, errors2=errors2)
        else:
            return (errors1, errors2)

    ###############
    ## Utilities ##
    ###############

    security.declarePublic('getObjects')
    def getObjects(self):
        """
        """
        hasPermission = nobody.has_permission
        objects = [object for object in self.objectValues(('Section', 'NewsletterTopic', 'NewsletterReference', 'NewsletterRichReference')) if hasPermission('View', object)]
        objects.sort(lambda a, b: cmp(self.getObjectPosition(a.getId()), self.getObjectPosition(b.getId())))
        return objects

    security.declareProtected(View, 'renderedDynamicContent')
    def renderedDynamicContent(self, force=False):
        if force:
            return None
        else:
            return self._dynamic_content

    security.declareProtected(ListFolderContents, 'listFolderContents')
    def listFolderContents(self, spec=None, contentFilter=None, suppressHiddenFiles=0):
        """
        Hook around 'contentValues' to let 'folder_contents'
        be protected.  Duplicating skip_unauthorized behavior of dtml-in.

        In the world of Plone we do not want to show objects that begin with a .
        So we have added a simply check.  We probably dont want to raise an
        Exception as much as we want to not show it.

        """
        ctool = getToolByName(self, 'portal_catalog')
        items = ctool(path={'query': '/'.join(self.getPhysicalPath()), 'depth': 1},
                      sort_on='sortable_title')
        return items

    # For plone 2.1+ to show unindexed content
    security.declareProtected(ChangeNewsletterTheme, 'getFolderContents')
    def getFolderContents(self, contentFilter=None, batch=False, b_size=100, full_objects=False):
        """Override getFolderContents to show all objects"""
        contents = self.listFolderContents(contentFilter=contentFilter)
        if batch:
            from Products.CMFPlone import Batch
            b_start = self.REQUEST.get('b_start', 0)
            batch = Batch(contents, b_size, int(b_start), orphan=0)
            return batch
        return contents


# Class instanciation
InitializeClass(Newsletter)
