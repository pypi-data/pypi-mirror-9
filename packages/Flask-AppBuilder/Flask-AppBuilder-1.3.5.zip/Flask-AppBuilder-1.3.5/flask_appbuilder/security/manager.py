import datetime
import logging
from flask import url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user
from flask_openid import OpenID
from flask_babelpkg import lazy_gettext as _

from ..basemanager import BaseManager

log = logging.getLogger(__name__)

# Constants for supported authentication types
AUTH_OID = 0
AUTH_DB = 1
AUTH_LDAP = 2
AUTH_REMOTE_USER = 3
AUTH_OAUTH = 4


class AbstractSecurityManager(BaseManager):
    """
        Abstract SecurityManager class, declares all methods used by the
        framework. There is no assumptions about security models or auth types.
    """
    def add_permissions_view(self, base_permissions, view_menu):
        """
            Adds a permission on a view menu to the backend

            :param base_permissions:
                list of permissions from view (all exposed methods): 'can_add','can_edit' etc...
            :param view_menu:
                name of the view or menu to add
        """
        raise NotImplementedError

    def add_permissions_menu(self, view_menu_name):
        """
            Adds menu_access to menu on permission_view_menu

            :param view_menu_name:
                The menu name
        """
        raise NotImplementedError

    def register_views(self):
        """
            Generic function to create views
        """
        raise NotImplementedError

    def is_item_public(self, permission_name, view_name):
        """
            Check if view has public permissions

            :param permission_name:
                the permission: can_show, can_edit...
            :param view_name:
                the name of the class view (child of BaseView)
        """
        raise NotImplementedError

    def has_access(self, permission_name, view_name):
        """
            Check if current user or public has access to view or menu
        """
        raise NotImplementedError

    def security_cleanup(self, baseviews, menus):
        raise NotImplementedError


class BaseSecurityManager(AbstractSecurityManager):

    auth_view = None
    """ The obj instance for authentication view """
    user_view = None
    """ The obj instance for user view """
    registeruser_view = None
    """ The obj instance for registering user view """
    lm = None
    """ Flask-Login LoginManager """
    oid = None
    """ Flask-OpenID OpenID """
    oauth = None
    """ Flask-OAuth """
    oauth_handler = None
    """ OAuth handler, you can use this to use OAuth API's on your app """

    userdbmodelview = None
    """ Override if you want your own user db view """
    userldapmodelview = None
    """ Override if you want your own user ldap view """
    useroidmodelview = None
    """ Override if you want your own user OID view """
    useroauthmodelview = None
    """ Override if you want your own user OAuth view """
    userremoteusermodelview = None
    """ Override if you want your own user REMOTE_USER view """
    authdbview = None
    """ Override if you want your own Authentication DB view """
    authldapview = None
    """ Override if you want your own Authentication LDAP view """
    authoidview = None
    """ Override if you want your own Authentication OID view """
    authoauthview = None
    """ Override if you want your own Authentication OAuth view """
    authremoteuserview = None
    """ Override if you want your own Authentication OAuth view """
    registeruserdbview = None
    """ Override if you want your own register user db view """
    registeruseroidview = None
    """ Override if you want your own register user db view """
    resetmypasswordview = None
    """ Override if you want your own reset my password view """
    resetpasswordview = None
    """ Override if you want your own reset password view """
    rolemodelview = None
    permissionmodelview = None
    userstatschartview = None
    viewmenumodelview = None
    permissionviewmodelview = None

    def __init__(self, appbuilder):
        super(BaseSecurityManager, self).__init__(appbuilder)
        app = self.appbuilder.get_app
        # Base Security Config
        app.config.setdefault('AUTH_ROLE_ADMIN', 'Admin')
        app.config.setdefault('AUTH_ROLE_PUBLIC', 'Public')
        app.config.setdefault('AUTH_TYPE', AUTH_DB)
        # Self Registration
        app.config.setdefault('AUTH_USER_REGISTRATION', False)
        app.config.setdefault('AUTH_USER_REGISTRATION_ROLE', self.auth_role_public)
        # LDAP Config
        app.config.setdefault('AUTH_LDAP_SEARCH', '')
        app.config.setdefault('AUTH_LDAP_BIND_FIELD', 'cn')
        app.config.setdefault('AUTH_LDAP_UID_FIELD', 'uid')
        app.config.setdefault('AUTH_LDAP_FIRSTNAME_FIELD', 'givenName')
        app.config.setdefault('AUTH_LDAP_LASTNAME_FIELD', 'sn')
        app.config.setdefault('AUTH_LDAP_EMAIL_FIELD', 'mail')

        if self.auth_type == AUTH_LDAP:
            if 'AUTH_LDAP_SERVER' not in app.config:
                raise Exception("No AUTH_LDAP_SERVER defined on config with AUTH_LDAP authentication type.")
        if self.auth_type == AUTH_OID:
            self.oid = OpenID(app)
        if self.auth_type == AUTH_OAUTH:
            from flask_oauth import OAuth
            self.oauth = OAuth

        self.lm = LoginManager(app)
        self.lm.login_view = 'login'
        self.lm.user_loader(self.load_user)

    @property
    def get_url_for_registeruser(self):
        return url_for('%s.%s' % (self.registeruser_view.endpoint, self.registeruser_view.default_view))

    @property
    def auth_type(self):
        return self.appbuilder.get_app.config['AUTH_TYPE']

    @property
    def auth_role_admin(self):
        return self.appbuilder.get_app.config['AUTH_ROLE_ADMIN']

    @property
    def auth_role_public(self):
        return self.appbuilder.get_app.config['AUTH_ROLE_PUBLIC']

    @property
    def auth_ldap_server(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_SERVER']

    @property
    def auth_user_registration(self):
        return self.appbuilder.get_app.config['AUTH_USER_REGISTRATION']

    @property
    def auth_user_registration_role(self):
        return self.appbuilder.get_app.config['AUTH_USER_REGISTRATION_ROLE']

    @property
    def auth_ldap_search(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_SEARCH']

    @property
    def auth_ldap_bind_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_BIND_FIELD']

    @property
    def auth_ldap_uid_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_UID_FIELD']

    @property
    def auth_ldap_firstname_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_FIRSTNAME_FIELD']

    @property
    def auth_ldap_lastname_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_LASTNAME_FIELD']

    @property
    def auth_ldap_email_field(self):
        return self.appbuilder.get_app.config['AUTH_LDAP_EMAIL_FIELD']

    @property
    def openid_providers(self):
        return self.appbuilder.get_app.config['OPENID_PROVIDERS']

    @property
    def oauth_providers(self):
        return self.appbuilder.get_app.config['OAUTH_PROVIDERS']

    def register_views(self):
        self.appbuilder.add_view_no_menu(self.resetpasswordview())
        self.appbuilder.add_view_no_menu(self.resetmypasswordview())

        if self.auth_type == AUTH_DB:
            self.user_view = self.userdbmodelview
            self.auth_view = self.authdbview()
            if self.auth_user_registration:
                pass
                #self.registeruser_view = self.registeruserdbview()
                #self.appbuilder.add_view_no_menu(self.registeruser_view)
        elif self.auth_type == AUTH_LDAP:
            self.user_view = self.userldapmodelview
            self.auth_view = self.authldapview()
        elif self.auth_type == AUTH_OAUTH:
            self.user_view = self.useroauthmodelview
            self.auth_view = self.authoauthview()
        elif self.auth_type == AUTH_REMOTE_USER:
            self.user_view = self.userremoteusermodelview
            self.auth_view = self.authremoteuserview()
        else:
            self.user_view = self.useroidmodelview
            self.auth_view = self.authoidview()
            if self.auth_user_registration:
                pass
                #self.registeruser_view = self.registeruseroidview()
                #self.appbuilder.add_view_no_menu(self.registeruser_view)

        self.appbuilder.add_view_no_menu(self.auth_view)

        self.user_view = self.appbuilder.add_view(self.user_view, "List Users",
                                                  icon="fa-user", label=_("List Users"),
                                                  category="Security", category_icon="fa-cogs",
                                                  category_label=_('Security'))

        role_view = self.appbuilder.add_view(self.rolemodelview, "List Roles", icon="fa-group", label=_('List Roles'),
                                             category="Security", category_icon="fa-cogs")
        role_view.related_views = [self.user_view.__class__]

        self.appbuilder.add_view(self.userstatschartview,
                                 "User's Statistics", icon="fa-bar-chart-o", label=_("User's Statistics"),
                                 category="Security")

        self.appbuilder.menu.add_separator("Security")
        self.appbuilder.add_view(self.permissionmodelview,
                                 "Base Permissions", icon="fa-lock",
                                 label=_("Base Permissions"), category="Security")
        self.appbuilder.add_view(self.viewmenumodelview,
                                 "Views/Menus", icon="fa-list-alt",
                                 label=_('Views/Menus'), category="Security")
        self.appbuilder.add_view(self.permissionviewmodelview,
                                 "Permission on Views/Menus", icon="fa-link",
                                 label=_('Permission on Views/Menus'), category="Security")

    def create_db(self):
        if self.add_role(self.auth_role_admin):
                    log.info("Inserted Role for public access %s" % (self.auth_role_admin))
        if self.add_role(self.auth_role_public):
            log.info("Inserted Role for public access %s" % (self.auth_role_public))
        if self.count_users() == 0:
            log.warning("No user yet created, use fabmanager command to do it.")

    def reset_password(self, userid, password):
        """
            Change/Reset a user's password for authdb.
            Password will be hashed and saved.

            :param userid:
                the user.id to reset the password
            :param password:
                The clear text password to reset and save hashed on the db
        """
        user = self.get_user_by_id(userid)
        user.password = generate_password_hash(password)
        self.update_user(user)

    def update_user_auth_stat(self, user, success=True):
        """
            Update authentication successful to user.

            :param user:
                The authenticated user model
        """
        if not user.login_count:
            user.login_count = 0
        if not user.fail_login_count:
            user.fail_login_count = 0
        if success:
            user.login_count += 1
            user.fail_login_count = 0
        else:
            user.fail_login_count += 1
        user.last_login = datetime.datetime.now()
        self.update_user(user)

    def auth_user_db(self, username, password):
        """
            Method for authenticating user, auth db style

            :param username:
                The username
            :param password:
                The password, will be tested against hashed password on db
        """
        if username is None or username == "":
            return None
        user = self.find_user(username=username)
        if user is None or (not user.is_active()):
            return None
        elif check_password_hash(user.password, password):
            self.update_user_auth_stat(user, True)
            return user
        else:
            self.update_user_auth_stat(user, False)
            return None

    def auth_user_ldap(self, username, password):
        """
            Method for authenticating user, auth LDAP style.
            depends on ldap module that is not mandatory requirement
            for F.A.B.

            :param username:
                The username
            :param password:
                The password
        """
        if username is None or username == "":
            return None
        user = self.find_user(username=username)
        if user is not None and (not user.is_active()):
            return None
        else:
            try:
                import ldap
            except:
                raise Exception("No ldap library for python.")
            try:
                con = ldap.initialize(self.auth_ldap_server)
                con.set_option(ldap.OPT_REFERRALS, 0)
                try:
                    if not self.auth_ldap_search:
                        bind_username = username
                    else:
                        filter = "%s=%s" % (self.auth_ldap_uid_field, username)
                        bind_username_array = con.search_s(self.auth_ldap_search,
                                                               ldap.SCOPE_SUBTREE,
                                                               filter,
                                                               [self.auth_ldap_firstname_field,
                                                                self.auth_ldap_lastname_field,
                                                                self.auth_ldap_email_field
                                                               ])
                        if bind_username_array == []:
                            return None
                        else:
                            bind_username = bind_username_array[0][0]
                            ldap_user_info = bind_username_array[0][1]

                    con.bind_s(bind_username, password)

                    if self.auth_user_registration and user is None:
                        user = self.add_user(
                            username=username,
                            first_name=ldap_user_info[self.auth_ldap_firstname_field][0],
                            last_name=ldap_user_info[self.auth_ldap_lastname_field][0],
                            email=ldap_user_info[self.auth_ldap_email_field][0],
                            role=self.find_role(self.auth_user_registration_role)
                        )

                    self.update_user_auth_stat(user)
                    return user
                except ldap.INVALID_CREDENTIALS:
                    self.update_user_auth_stat(user, False)
                    return None
            except ldap.LDAPError as e:
                if type(e.message) == dict and 'desc' in e.message:
                    log.error("LDAP Error {0}".format(e.message['desc']))
                    return None
                else:
                    log.error(e)
                    return None

    def auth_user_oid(self, email):
        """
            OpenID user Authentication

            :type self: User model
        """
        user = self.find_user(email=email)
        if user is None or (not user.is_active()):
            return None
        else:
            self.update_user_auth_stat(user)
            return user

    def auth_user_remote_user(self, username):
        """
            REMOTE_USER user Authentication

            :type self: User model
        """
        user = self.find_user(username=username)
        if user is None or (not user.is_active()):
            return None
        else:
            self.update_user_auth_stat(user)
            return user

    """
        ----------------------------------------
            PERMISSION ACCESS CHECK
        ----------------------------------------
    """
    def is_item_public(self, permission_name, view_name):
        """
            Check if view has public permissions

            :param permission_name:
                the permission: can_show, can_edit...
            :param view_name:
                the name of the class view (child of BaseView)
        """
        permissions = self.get_public_permissions()
        if permissions:
            for i in permissions:
                if (view_name == i.view_menu.name) and (permission_name == i.permission.name):
                    return True
            return False
        else:
            return False

    def _has_view_access(self, user, permission_name, view_name):
        roles = user.roles
        for role in roles:
            permissions = role.permissions
            if permissions:
                for permission in permissions:
                    if (view_name == permission.view_menu.name) and (permission_name == permission.permission.name):
                        return True
        return False

    def has_access(self, permission_name, view_name):
        """
            Check if current user or public has access to view or menu
        """
        if current_user.is_authenticated():
            return self._has_view_access(g.user, permission_name, view_name)
        else:
            return self.is_item_public(permission_name, view_name)


    def add_permissions_view(self, base_permissions, view_menu):
        """
            Adds a permission on a view menu to the backend

            :param base_permissions:
                list of permissions from view (all exposed methods): 'can_add','can_edit' etc...
            :param view_menu:
                name of the view or menu to add
        """
        view_menu_db = self.add_view_menu(view_menu)
        perm_views = self.find_permissions_view_menu(view_menu_db)

        if not perm_views:
            # No permissions yet on this view
            for permission in base_permissions:
                pv = self.add_permission_view_menu(permission, view_menu)
                role_admin = self.find_role(self.auth_role_admin)
                self.add_permission_role(role_admin, pv)
        else:
            # Permissions on this view exist but....
            role_admin = self.find_role(self.auth_role_admin)
            for permission in base_permissions:
                # Check if base view permissions exist
                if not self.exist_permission_on_views(perm_views, permission):
                    pv = self.add_permission_view_menu(permission, view_menu)
                    self.add_permission_role(role_admin, pv)
            for perm_view in perm_views:
                if perm_view.permission.name not in base_permissions:
                    # perm to delete
                    roles = self.get_all_roles()
                    perm = self.find_permission(perm_view.permission.name)
                    # del permission from all roles
                    for role in roles:
                        self.del_permission_role(role, perm)
                    self.del_permission_view_menu(perm_view.permission.name, view_menu)
                elif perm_view not in role_admin.permissions:
                    # Role Admin must have all permissions
                    self.add_permission_role(role_admin, perm_view)

    def add_permissions_menu(self, view_menu_name):
        """
            Adds menu_access to menu on permission_view_menu

            :param view_menu_name:
                The menu name
        """
        self.add_view_menu(view_menu_name)
        pv = self.find_permission_view_menu('menu_access', view_menu_name)
        if not pv:
            pv = self.add_permission_view_menu('menu_access', view_menu_name)
            role_admin = self.find_role(self.auth_role_admin)
            self.add_permission_role(role_admin, pv)

    def security_cleanup(self, baseviews, menus):
        """
            Will cleanup from the database all unused permissions

            :param baseviews: A list of BaseViews class
            :param menus: Menu class
        """
        viewsmenus = self.get_all_view_menu()
        roles = self.get_all_roles()
        for viewmenu in viewsmenus:
            found = False
            for baseview in baseviews:
                if viewmenu.name == baseview.__class__.__name__:
                    found = True
                    break
            if menus.find(viewmenu.name):
                found = True
            if not found:
                permissions = self.find_permissions_view_menu(viewmenu)
                for permission in permissions:
                    for role in roles:
                        self.del_permission_role(role, permission)
                    self.del_permission_view_menu(permission.permission.name, viewmenu.name)
                self.del_view_menu(viewmenu.name)


    #---------------------------------------
    #    INTERFACE ABSTRACT METHODS
    #---------------------------------------
    #------------------------------------
    # PRIMITIVES FOR USERS
    #------------------------------------
    def get_user_by_id(self, pk):
        """
            Generic function to return user by it's id (pk)
        """
        raise NotImplementedError

    def find_user(self, username=None, email=None):
        """
            Generic function find a user by it's username or email
        """
        raise NotImplementedError

    def get_all_users(self):
        """
            Generic function that returns all exsiting users
        """
        raise NotImplementedError

    def add_user(self, username, first_name, last_name, email, role, password=''):
        """
            Generic function to create user
        """
        raise NotImplementedError

    def update_user(self, user):
        """
            Generic function to create user

            :param user: User model to update to database
        """
        raise NotImplementedError

    def count_users(self):
        """
            Generic function to count the existing users
        """
        raise NotImplementedError

    #------------------------------------
    # PRIMITIVES FOR ROLES
    #------------------------------------
    def find_role(self, name):
        raise NotImplementedError

    def add_role(self, name):
        raise NotImplementedError

    def get_all_roles(self):
        raise NotImplementedError

    #------------------------------------
    # PRIMITIVES FOR PERMISSIONS
    #------------------------------------
    def get_public_permissions(self):
        """
            returns all permissions from public role
        """
        raise NotImplementedError

    def find_permission(self, name):
        """
            Finds and returns a Permission by name
        """
        raise NotImplementedError

    def add_permission(self, name):
        """
            Adds a permission to the backend, model permission

            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        raise NotImplementedError

    def del_permission(self, name):
        """
            Deletes a permission from the backend, model permission

            :param name:
                name of the permission: 'can_add','can_edit' etc...
        """
        raise NotImplementedError

    def get_public_permissions(self):
        raise NotImplementedError

    # ------------------------------------------
    #       PRIMITIVES VIEW MENU
    #-------------------------------------------
    def find_view_menu(self, name):
        """
            Finds and returns a ViewMenu by name
        """
        raise NotImplementedError

    def get_all_view_menu(self):
        raise NotImplementedError

    def add_view_menu(self, name):
        """
            Adds a view or menu to the backend, model view_menu
            param name:
                name of the view menu to add
        """
        raise NotImplementedError

    def del_view_menu(self, name):
        """
            Deletes a ViewMenu from the backend

            :param name:
                name of the ViewMenu
        """
        raise NotImplementedError

    #----------------------------------------------
    #          PERMISSION VIEW MENU
    #----------------------------------------------
    def find_permission_view_menu(self, permission_name, view_menu_name):
        """
            Finds and returns a PermissionView by names
        """
        raise NotImplementedError

    def find_permissions_view_menu(self, view_menu):
        """
            Finds all permissions from ViewMenu, returns list of PermissionView

            :param view_menu: ViewMenu object
            :return: list of PermissionView objects
        """
        raise NotImplementedError

    def add_permission_view_menu(self, permission_name, view_menu_name):
        """
            Adds a permission on a view or menu to the backend

            :param permission_name:
                name of the permission to add: 'can_add','can_edit' etc...
            :param view_menu_name:
                name of the view menu to add
        """
        raise NotImplementedError

    def del_permission_view_menu(self, permission_name, view_menu_name):
        raise NotImplementedError

    def exist_permission_on_views(self, lst, item):
        raise NotImplementedError

    def exist_permission_on_view(self, lst, permission, view_menu):
        raise NotImplementedError

    def add_permission_role(self, role, perm_view):
        """
            Add permission-ViewMenu object to Role

            :param role:
                The role object
            :param perm_view:
                The PermissionViewMenu object
        """
        raise NotImplementedError

    def del_permission_role(self, role, perm_view):
        """
            Remove permission-ViewMenu object to Role

            :param role:
                The role object
            :param perm_view:
                The PermissionViewMenu object
        """
        raise NotImplementedError

    def load_user(self, pk):
        return self.get_user_by_id(int(pk))

    @staticmethod
    def before_request():
        g.user = current_user

