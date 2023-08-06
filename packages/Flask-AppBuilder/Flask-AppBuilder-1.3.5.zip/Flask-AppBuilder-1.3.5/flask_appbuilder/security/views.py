import datetime
import logging

from flask import flash, redirect, session, url_for, request, g
from werkzeug.security import generate_password_hash
from wtforms import validators, PasswordField
from wtforms.validators import EqualTo
from flask_babelpkg import lazy_gettext
from flask_login import login_user, logout_user

from ..views import ModelView, SimpleFormView, expose
from ..baseviews import BaseView
from ..charts.views import DirectByChartView
from ..fieldwidgets import BS3PasswordFieldWidget
from ..actions import action
from .._compat import as_unicode
from .forms import LoginForm_db, LoginForm_oid, ResetPasswordForm
from .decorators import has_access


log = logging.getLogger(__name__)


class PermissionModelView(ModelView):
    route_base = '/permissions'
    base_permissions = ['can_list']

    list_title = lazy_gettext('List Base Permissions')
    show_title = lazy_gettext('Show Base Permission')
    add_title = lazy_gettext('Add Base Permission')
    edit_title = lazy_gettext('Edit Base Permission')

    label_columns = {'name': lazy_gettext('Name')}


class ViewMenuModelView(ModelView):
    route_base = '/viewmenus'
    base_permissions = ['can_list']

    list_title = lazy_gettext('List View Menus')
    show_title = lazy_gettext('Show View Menu')
    add_title = lazy_gettext('Add View Menu')
    edit_title = lazy_gettext('Edit View Menu')

    label_columns = {'name': lazy_gettext('Name')}


class PermissionViewModelView(ModelView):
    route_base = '/permissionviews'
    base_permissions = ['can_list']

    list_title = lazy_gettext('List Permissions on Views/Menus')
    show_title = lazy_gettext('Show Permission on Views/Menus')
    add_title = lazy_gettext('Add Permission on Views/Menus')
    edit_title = lazy_gettext('Edit Permission on Views/Menus')

    label_columns = {'permission': lazy_gettext('Permission'), 'view_menu': lazy_gettext('View/Menu')}
    list_columns = ['permission', 'view_menu']
    show_columns = ['permission', 'view_menu']
    search_columns = ['permission', 'view_menu']


class ResetMyPasswordView(SimpleFormView):
    """
        View for resetting own user password
    """
    route_base = '/resetmypassword'
    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    redirect_url = '/'
    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        self.appbuilder.sm.reset_password(g.user.id, form.password.data)
        flash(as_unicode(self.message), 'info')


class ResetPasswordView(SimpleFormView):
    """
        View for reseting all users password
    """
    route_base = '/resetpassword'
    form = ResetPasswordForm
    form_title = lazy_gettext('Reset Password Form')
    redirect_url = '/'
    message = lazy_gettext('Password Changed')

    def form_post(self, form):
        pk = request.args.get('pk')
        self.appbuilder.sm.reset_password(pk, form.password.data)
        flash(as_unicode(self.message), 'info')


class UserModelView(ModelView):
    route_base = '/users'

    list_title = lazy_gettext('List Users')
    show_title = lazy_gettext('Show User')
    add_title = lazy_gettext('Add User')
    edit_title = lazy_gettext('Edit User')

    label_columns = {'get_full_name': lazy_gettext('Full Name'),
                     'first_name': lazy_gettext('First Name'),
                     'last_name': lazy_gettext('Last Name'),
                     'username': lazy_gettext('User Name'),
                     'password': lazy_gettext('Password'),
                     'active': lazy_gettext('Is Active?'),
                     'email': lazy_gettext('EMail'),
                     'roles': lazy_gettext('Role'),
                     'last_login': lazy_gettext('Last login'),
                     'login_count': lazy_gettext('Login count'),
                     'fail_login_count': lazy_gettext('Failed login count'),
                     'created_on': lazy_gettext('Created on'),
                     'created_by': lazy_gettext('Created by'),
                     'changed_on': lazy_gettext('Changed on'),
                     'changed_by': lazy_gettext('Changed by')}

    description_columns = {'first_name': lazy_gettext('Write the user first name or names'),
                           'last_name': lazy_gettext('Write the user last name'),
                           'username': lazy_gettext(
                               'Username valid for authentication on DB or LDAP, unused for OID auth'),
                           'password': lazy_gettext(
                               'Please use a good password policy, this application does not check this for you'),
                           'active': lazy_gettext('Its not a good policy to remove a user, just make it inactive'),
                           'email': lazy_gettext('The users email, this will also be used for OID auth'),
                           'roles': lazy_gettext(
                               'The user role on the application, this will associate with a list of permissions'),
                           'conf_password': lazy_gettext('Please rewrite the users password to confirm')}

    list_columns = ['first_name', 'last_name', 'username', 'email', 'active', 'roles']

    show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'roles', 'login_count']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
        (lazy_gettext('Audit Info'),
         {'fields': ['last_login', 'fail_login_count', 'created_on',
                     'created_by', 'changed_on', 'changed_by'], 'expanded': False}),
    ]

    user_show_fieldsets = [
        (lazy_gettext('User info'),
         {'fields': ['username', 'active', 'roles', 'login_count']}),
        (lazy_gettext('Personal Info'),
         {'fields': ['first_name', 'last_name', 'email'], 'expanded': True}),
    ]

    search_columns = ['first_name', 'last_name', 'username', 'email', 'roles', 'active',
                      'created_by', 'changed_by', 'changed_on', 'changed_by', 'login_count']

    add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'roles']
    edit_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'roles']
    user_info_title = lazy_gettext("Your user information")


    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        widgets = self._get_show_widget(g.user.id, show_fieldsets=self.user_show_fieldsets)
        self.update_redirect()
        return self.render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder)


class UserOIDModelView(UserModelView):
    """
        View that add OID specifics to User view.
        Override to implement your own custom view.
        Then override useroidmodelview property on SecurityManager
    """
    pass


class UserLDAPModelView(UserModelView):
    """
        View that add LDAP specifics to User view.
        Override to implement your own custom view.
        Then override userldapmodelview property on SecurityManager
    """
    pass


class UserOAuthModelView(UserModelView):
    """
        View that add OAUTH specifics to User view.
        Override to implement your own custom view.
        Then override userldapmodelview property on SecurityManager
    """
    pass


class UserRemoteUserModelView(UserModelView):
    """
        View that add REMOTE_USER specifics to User view.
        Override to implement your own custom view.
        Then override userldapmodelview property on SecurityManager
    """
    pass


class UserDBModelView(UserModelView):
    """
        View that add DB specifics to User view.
        Override to implement your own custom view.
        Then override userdbmodelview property on SecurityManager
    """
    add_form_extra_fields = {'password': PasswordField(lazy_gettext('Password'),
                                                       description=lazy_gettext(
                                                           'Please use a good password policy, this application does not check this for you'),
                                                       validators=[validators.DataRequired()],
                                                       widget=BS3PasswordFieldWidget()),
                             'conf_password': PasswordField(lazy_gettext('Confirm Password'),
                                                            description=lazy_gettext(
                                                                'Please rewrite the users password to confirm'),
                                                            validators=[EqualTo('password', message=lazy_gettext(
                                                                'Passwords must match'))],
                                                            widget=BS3PasswordFieldWidget())}

    add_columns = ['first_name', 'last_name', 'username', 'active', 'email', 'roles', 'password', 'conf_password']


    @expose('/show/<pk>', methods=['GET'])
    @has_access
    def show(self, pk):
        actions = {}
        actions['resetpasswords'] = self.actions.get('resetpasswords')
        widgets = self._get_show_widget(pk, actions=actions)
        self.update_redirect()
        return self.render_template(self.show_template,
                               pk=pk,
                               title=self.show_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder,
                               related_views=self._related_views)


    @expose('/userinfo/')
    @has_access
    def userinfo(self):
        actions = {}
        actions['resetmypassword'] = self.actions.get('resetmypassword')
        widgets = self._get_show_widget(g.user.id, actions=actions, show_fieldsets=self.user_show_fieldsets)
        self.update_redirect()
        return self.render_template(self.show_template,
                               title=self.user_info_title,
                               widgets=widgets,
                               appbuilder=self.appbuilder,
        )

    @action('resetmypassword', lazy_gettext("Reset my password"), "", "fa-lock", multiple=False)
    def resetmypassword(self, item):
        return redirect(url_for('ResetMyPasswordView.this_form_get'))

    @action('resetpasswords', lazy_gettext("Reset Password"), "", "fa-lock", multiple=False)
    def resetpasswords(self, item):
        return redirect(url_for('ResetPasswordView.this_form_get', pk=item.id))

    def pre_update(self, item):
        item.changed_on = datetime.datetime.now()
        item.changed_by_fk = g.user.id

    def pre_add(self, item):
        item.password = generate_password_hash(item.password)


class UserStatsChartView(DirectByChartView):
    chart_title = lazy_gettext('User Statistics')
    label_columns = {'username': lazy_gettext('User Name'),
                     'login_count': lazy_gettext('Login count'),
                     'fail_login_count': lazy_gettext('Failed login count')
    }

    search_columns = UserModelView.search_columns

    definitions = [
        {
            'label': 'Login Count',
            'group': 'username',
            'series': ['login_count']
        },
        {
            'label': 'Failed Login Count',
            'group': 'username',
            'series': ['fail_login_count']
        }

    ]


class RoleModelView(ModelView):
    route_base = '/roles'

    list_title = lazy_gettext('List Roles')
    show_title = lazy_gettext('Show Role')
    add_title = lazy_gettext('Add Role')
    edit_title = lazy_gettext('Edit Role')

    label_columns = {'name': lazy_gettext('Name'), 'permissions': lazy_gettext('Permissions')}
    list_columns = ['name', 'permissions']
    show_columns = ['name', 'permissions']
    order_columns = ['name']
    search_columns = ['name']

    @action("Copy Role", lazy_gettext('Copy Role'), lazy_gettext('Copy the selected roles?'), icon='fa-copy', single=False)
    def copy_role(self, items):
        self.update_redirect()
        for item in items:
            new_role = item.__class__()
            new_role.name = item.name
            new_role.permissions = item.permissions
            new_role.name = new_role.name + ' copy'
            self.datamodel.add(new_role)
        return redirect(self.get_redirect())


class AuthView(BaseView):
    route_base = ''
    login_template = ''

    invalid_login_message = lazy_gettext('Invalid login. Please try again.')

    title = lazy_gettext('Sign In')

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        pass

    @expose('/logout/')
    def logout(self):
        logout_user()
        return redirect(self.appbuilder.get_url_for_index)


class AuthDBView(AuthView):
    login_template = 'appbuilder/general/security/login_db.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect('/')
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.appbuilder.sm.auth_user_db(form.username.data, form.password.data)
            if not user:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect(self.appbuilder.get_url_for_login)
            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)
        return self.render_template(self.login_template,
                               title=self.title,
                               form=form,
                               appbuilder=self.appbuilder)


class AuthLDAPView(AuthView):
    login_template = 'appbuilder/general/security/login_ldap.html'

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):
        if g.user is not None and g.user.is_authenticated():
            return redirect(self.appbuilder.get_url_for_index)
        form = LoginForm_db()
        if form.validate_on_submit():
            user = self.appbuilder.sm.auth_user_ldap(form.username.data, form.password.data)
            if not user:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect(self.appbuilder.get_url_for_login)
            login_user(user, remember=False)
            return redirect(self.appbuilder.get_url_for_index)
        return self.render_template(self.login_template,
                               title=self.title,
                               form=form,
                               appbuilder=self.appbuilder)


class AuthOIDView(AuthView):
    login_template = 'appbuilder/general/security/login_oid.html'
    oid_ask_for = ['email']
    oid_ask_for_optional = []

    def __init__(self):
        super(AuthOIDView, self).__init__()


    @expose('/login/', methods=['GET', 'POST'])
    def login(self, flag=True):
        @self.appbuilder.sm.oid.loginhandler
        def login_handler(self):
            if g.user is not None and g.user.is_authenticated():
                return redirect(self.appbuilder.get_url_for_index)
            form = LoginForm_oid()
            if form.validate_on_submit():
                session['remember_me'] = form.remember_me.data
                return self.appbuilder.sm.oid.try_login(form.openid.data, ask_for=self.oid_ask_for,
                                                        ask_for_optional=self.oid_ask_for_optional)
            return self.render_template(self.login_template,
                                   title=self.title,
                                   form=form,
                                   providers=self.appbuilder.sm.openid_providers,
                                   appbuilder=self.appbuilder
            )

        @self.appbuilder.sm.oid.after_login
        def after_login(resp):
            if resp.email is None or resp.email == "":
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect('login')
            user = self.appbuilder.sm.auth_user_oid(resp.email)
            if user is None:
                flash(as_unicode(self.invalid_login_message), 'warning')
                return redirect('login')
            remember_me = False
            if 'remember_me' in session:
                remember_me = session['remember_me']
                session.pop('remember_me', None)

            login_user(user, remember=remember_me)
            return redirect(self.appbuilder.get_url_for_index)

        return login_handler(self)


class AuthOAuthView(AuthView):
    login_template = 'appbuilder/general/security/login_oauth.html'

    @expose('/login/')
    def login(self):
        provider = request.args.get('provider')
        if g.user is not None and g.user.is_authenticated():
            return redirect(self.appbuilder.get_url_for_index)
        if provider is None:
            return self.render_template(self.login_template,
                               providers = self.appbuilder.sm.oauth_providers,
                               title=self.title,
                               appbuilder=self.appbuilder)
        else:
            self.appbuilder.sm.oauth_handler = \
                self.appbuilder.sm.oauth.authorize(callback=url_for('oauth_authorized',
                    next=request.referrer, provider=provider))

    @expose('/oauth-authorized')
    def oauth_authorized(self):
        """
        #provider = request.args['provider']
        remote_app = self.appbuilder.sm.oauth.remote_apps['twitter']
        print "OAUTH AUTHORIZED {0} {1}".format(remote_app)
        if 'oauth_verifier' in request.args:
            resp = remote_app.handle_oauth1_response()
        elif 'code' in request.args:
            resp = remote_app.handle_oauth2_response()
        else:
            resp = remote_app.handle_unknown_response()
            remote_app.free_request_token()
        print "OAUTH AUTORIZED {0}".format(resp)
        next_url = request.args.get('next') or url_for('index')
        if resp is None:
            flash(u'You denied the request to sign in.')
            return redirect(next_url)

        session[self.appbuilder.sm.oauth.name] = (
            resp['oauth_token'],
            resp['oauth_token_secret']
        )
        user = self.appbuilder.sm.auth_user_remote_user(resp['screen_name'])
        if user is None:
            flash(as_unicode(self.invalid_login_message), 'warning')
        else:
            login_user(user)
        return redirect(next_url)
        """


class AuthRemoteUserView(AuthView):
    login_template = ''

    @expose('/login/')
    def login(self):
        username = request.environ.get('REMOTE_USER')
        if g.user is not None and g.user.is_authenticated():
            return redirect(self.appbuilder.get_url_for_index)
        if username:
            user = self.appbuilder.sm.auth_user_remote_user(username)
            if user is None:
                flash(as_unicode(self.invalid_login_message), 'warning')
            else:
                login_user(user)
        else:
            flash(as_unicode(self.invalid_login_message), 'warning')
        return redirect(self.appbuilder.get_url_for_index)

