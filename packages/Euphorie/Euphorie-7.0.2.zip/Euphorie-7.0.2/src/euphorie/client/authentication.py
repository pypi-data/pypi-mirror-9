import logging
import traceback
import urllib
import sqlalchemy.exc
from z3c.saconfig import Session
from Acquisition import aq_parent
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from zope.publisher.interfaces.browser import IBrowserView
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.interfaces.plugins \
        import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin
from Products.PluggableAuthService.interfaces.plugins \
        import IUserEnumerationPlugin
from Products.PluggableAuthService.interfaces.plugins import IUserFactoryPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from .interfaces import IClientSkinLayer
from . import model
from .api.authentication import authenticate_token as authenticate_client_token
from ..content.api.authentication \
        import authenticate_token as authenticate_cms_token


log = logging.getLogger(__name__)


class NotImplementedError(Exception):

    def __init__(self, message):
        self.message = message


def graceful_recovery(default=None, log_args=True):
    """Decorator to safely use SQLAlchemy in PAS plugins. This decorator
    makes sure SQL exceptions are caught and logged.

    Code from Malthe Borch's pas.plugins.sqlalchemy package.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                value = func(*args, **kwargs)
            except sqlalchemy.exc.SQLAlchemyError as e:
                if log_args is False:
                    args = ()
                    kwargs = {}

                formatted_tb = traceback.format_exc()

                try:
                    exc_str = str(e)
                except:
                    exc_str = "<%s at 0x%x>" % (e.__class__.__name__, id(e))

                log.critical(
                    "caught SQL-exception: "
                    "%s (in method ``%s``; arguments were %s)\n\n%s" % (
                    exc_str,
                    func.__name__, ", ".join(
                        [repr(arg) for arg in args] +
                        ["%s=%s" % (name, repr(value))
                         for (name, value) in kwargs.items()]
                        ), formatted_tb))
                return default
            return value
        return wrapper
    return decorator


manage_addEuphorieAccountPlugin = PageTemplateFile(
        "templates/addPasPlugin", globals(),
        __name__="manage_addEuphorieAccountPlugin")


def addEuphorieAccountPlugin(self, id, title='', REQUEST=None):
    """Add an EuphorieAccountPlugin to a Pluggable Authentication Service.
    """
    p = EuphorieAccountPlugin(id, title)
    self._setObject(p.getId(), p)

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect("%s/manage_workspace"
                "?manage_tabs_message=Euphorie+Account+Manager+plugin+added." %
                self.absolute_url())


class EuphorieAccountPlugin(BasePlugin):
    meta_type = "Euphorie account manager"
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._setId(id)
        self.title = title

    #
    # IExtractionPlugin implementation
    #
    def extractCredentials(self, request):
        token = request.getHeader('X-Euphorie-Token')
        if token:
            return {'api-token': token}
        else:
            return {}

    #
    # IAuthenticationPlugin implementation
    #
    @security.private
    def _authenticate_token(self, credentials):
        token = credentials.get('api-token')
        if not token:
            return None
        account = authenticate_client_token(token)
        if account is None:
            account = authenticate_cms_token(self, token)
        return account

    @security.private
    def _authenticate_login(self, credentials):
        login = credentials.get('login')
        password = credentials.get('password')
        account = authenticate(login, password)
        if account is not None:
            return (str(account.id), account.loginname)
        else:
            return None

    @security.private
    def _get_survey_session(self):
        for parent in self.REQUEST.other['PARENTS']:
            if isinstance(parent, model.SurveySession):
                return parent
        else:
            return None

    @security.private
    @graceful_recovery(log_args=False)
    def authenticateCredentials(self, credentials):
        uid_and_login = self._authenticate_login(credentials)
        if uid_and_login is None:
            uid_and_login = self._authenticate_token(credentials)
        if uid_and_login is not None:
            session = self._get_survey_session()
            if session is not None:
                # Verify if current session matches the user. This prevents
                # a cookie hijack attack.
                if str(session.account_id) != uid_and_login[0]:
                    return None
            return uid_and_login
        else:
            return None

    #
    # IUserFactoryPlugin implementation
    @graceful_recovery()
    def createUser(self, user_id, name):
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return None
        return Session().query(model.Account).get(user_id)

    #
    # IUserEnumerationPlugin implementation
    #
    @graceful_recovery()
    def enumerateUsers(self, id=None, login=None, exact_match=False,
                       sort_by=None, max_results=None, **kw):
        if not exact_match:
            return []

        query = Session().query(model.Account)
        if id is not None:
            try:
                query = query.filter(model.Account.id == int(id))
            except ValueError:
                return []
        if login:
            query = query.filter(model.Account.loginname == login)
        account = query.first()
        if account is not None:
            return [{'id': str(account.id), 'login': account.loginname}]
        return []

    def updateUser(self, user_id, login_name ):
        """ Changes the user's username. New method available since Plone 4.3.
            Euphorie doesn't support this.
        """
        return False

    def updateEveryLoginName(self, quit_on_first_error=True):
        """Update login names of all users to their canonical value.

        This should be done after changing the login_transform
        property of PAS.

        You can set quit_on_first_error to False to report all errors
        before quitting with an error.  This can be useful if you want
        to know how many problems there are, if any.
        """
        raise NotImplementedError(
                "updateEveryLoginName method is not implemented by Euphorie")

    #
    # IChallengePlugin implementation
    #
    def challenge(self, request, response):
        if not IClientSkinLayer.providedBy(request):
            return False

        current_url = request.get("ACTUAL_URL", "")
        query = request.get("QUERY_STRING")
        if query:
            if not query.startswith("?"):
                query = "?" + query
            current_url += query

        context = request.PUBLISHED
        if IBrowserView.providedBy(context):
            context = aq_parent(context)

        login_url = "%s/@@login?%s" % (context.absolute_url(),
                urllib.urlencode(dict(came_from=current_url)))
        response.redirect(login_url, lock=True)
        return True


def authenticate(login, password):
    """Try to authenticate a user using the given login and password.

    :param unicode login: login name
    :param unicode password: users password
    :return: :py:class:`Account <euphorie.client.model.Account>` instance

    If the credentials are valid the matching account is returned. For invalid
    credentials None is returned instead.
    """
    if not login or not password:
        return None

    login = login.lower()
    account = Session().query(model.Account)\
            .filter(model.Account.loginname == login)\
            .filter(model.Account.password == password).first()
    return account


classImplements(
    EuphorieAccountPlugin,
    IAuthenticationPlugin,
    IChallengePlugin,
    IExtractionPlugin,
    IUserEnumerationPlugin,
    IUserFactoryPlugin)

InitializeClass(EuphorieAccountPlugin)
