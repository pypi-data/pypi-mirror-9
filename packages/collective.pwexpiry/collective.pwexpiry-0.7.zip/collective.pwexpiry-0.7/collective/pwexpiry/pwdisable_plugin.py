from DateTime import DateTime
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from AccessControl.SecurityManagement import noSecurityManager

from zope.component import getUtility
from zope.interface import implements
from plone import api
from plone.registry.interfaces import IRegistry
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PlonePAS.interfaces.plugins import IUserManagement
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from collective.pwexpiry.utils import days_since_event
from collective.pwexpiry.config import _

manage_addPwDisablePluginForm = PageTemplateFile('www/addPwDisablePlugin',
    globals(), __name__='manage_addPwDisablePlugin')

def addPwDisablePlugin(self, id, title='', REQUEST=None):
    """
    Add PwDisable plugin
    """
    o = PwDisablePlugin(id, title)
    self._setObject(o.getId(), o)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_main'
            '?manage_tabs_message=PwDisable+Plugin+added.' %
            self.absolute_url())


class PwDisablePlugin(BasePlugin):
    """
    Password disable plugin
    """
    meta_type = 'Password Disable Plugin'
    security = ClassSecurityInfo()
    implements(IChallengePlugin, IUserManagement)

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    # IChallengePlugin implementation
    security.declarePrivate('challenge')
    def challenge(self, request, response, **kw):
        """
        Challenge the user for credentials
        """
        user_disabled = response.getHeader('user_disabled')
        if user_disabled:
            user_disabled_time = response.getHeader('user_disabled_time')
            IStatusMessage(self.REQUEST).add(
                _(u'Your account has been locked due to too many invalid '
                   'attempts to login with a wrong password. Your account will '
                   'remain blocked for the next %s hours. You can reset your '
                   'password, or contact an administrator to unlock it, using '
                   'the Contact form.' %
                   user_disabled_time), type='error'
            )
            response.redirect('login_form', lock=1)
            return 1
        return 0

    # IUserManagement implementation
    security.declarePrivate('doChangeUser')
    def doChangeUser(self, principal_id, password):
        """
        When changing user's password, reset the login count restriction
        """
        user = api.user.get(username=principal_id)
        user.setMemberProperties({'account_locked': False,
                                  'password_tries': 0})

InitializeClass(PwDisablePlugin)
