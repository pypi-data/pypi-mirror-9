import logging

from flask import Blueprint, url_for, current_app
from .views import IndexView, UtilView
from .filters import TemplateFilters
from .menu import Menu
from .babel.manager import BabelManager
from .version import VERSION_STRING

log = logging.getLogger(__name__)


def dynamic_class_import(class_path):
    """
        Will dynamically import a class from a string path
        :param class_path: string with class path
        :return: class
    """
    # Split first occurrence of path
    tmp = class_path.split('.', 1)
    package = __import__(tmp[0])
    return reduce(getattr, tmp[1].split('.'), package)


class AppBuilder(object):
    """


        This is the base class for all the framework.
        This is were you will register all your views and create the menu structure.
        Will hold your flask app object, all your views, and security classes.
        
        initialize your application like this for SQLAlchemy::

            from flask import Flask
            from flask.ext.appbuilder import SQLA, AppBuilder

            app = Flask(__name__)
            app.config.from_object('config')
            db = SQLA(app)
            appbuilder = AppBuilder(app, db.session)

        When using MongoEngine::

            from flask import Flask
            from flask_appbuilder import AppBuilder
            from flask_appbuilder.security.mongoengine.manager import SecurityManager
            from flask_mongoengine import MongoEngine

            app = Flask(__name__)
            app.config.from_object('config')
            dbmongo = MongoEngine(app)
            appbuilder = AppBuilder(app, security_manager_class=SecurityManager)

        You can also create everything as an application factory.
    """
    baseviews = []
    security_manager_class = None
    app = None
    session = None
    sm = None  # Security Manager Class
    bm = None  # Babel Manager Class

    menu = None
    indexview = None

    static_folder = None
    static_url_path = None

    template_filters = None

    def __init__(self, app=None,
                 session=None,
                 menu=None,
                 indexview=None,
                 base_template='appbuilder/baselayout.html',
                 static_folder='static/appbuilder',
                 static_url_path='/appbuilder',
                 security_manager_class=None):
        """
            AppBuilder constructor
            
            :param app:
                The flask app object
            :param session:
                The SQLAlchemy session object
            :param menu:
                optional, a previous contructed menu
            :param indexview:
                optional, your customized indexview
            :param static_folder:
                optional, your override for the global static folder
            :param static_url_path:
                optional, your override for the global static url path
            :param security_manager_class:
                optional, pass your own security manager class
        """
        self.baseviews = []
        self.menu = menu or Menu()
        self.base_template = base_template
        self.security_manager_class = security_manager_class
        self.indexview = indexview or IndexView
        self.static_folder = static_folder
        self.static_url_path = static_url_path

        self.app = app
        if app is not None:
            self.init_app(app, session)


    def init_app(self, app, session):
        app.config.setdefault('APP_NAME', 'F.A.B.')
        app.config.setdefault('APP_THEME', '')
        app.config.setdefault('APP_ICON', '')
        app.config.setdefault('LANGUAGES',
                              {'en': {'flag': 'gb', 'name': 'English'}})
        if self.security_manager_class is None:
            from flask_appbuilder.security.sqla.manager import SecurityManager
            self.security_manager_class = SecurityManager
        self.session = session
        if not self.security_manager_class:
            self.security_manager_class = dynamic_class_import(app.config.get("SECURITY_CLASS"))
        self.sm = self.security_manager_class(self)
        self.bm = BabelManager(self)
        self._add_global_static()
        self._add_global_filters()
        app.before_request(self.sm.before_request)
        self._add_admin_views()
        self._add_menu_permissions()
        if not self.app:
            for baseview in self.baseviews:
                # instantiate the views and add session
                self._check_and_init(baseview)
                # Register the views has blueprints
                self.register_blueprint(baseview)
                # Add missing permissions where needed
                self._add_permission(baseview)
        self._init_extension(app)

    def _init_extension(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['appbuilder'] = self

    @property
    def get_app(self):
        """
            Get current or configured flask app

            :return: Flask App
        """
        if self.app:
            return self.app
        else:
            return current_app

    @property
    def get_session(self):
        """
            Get the current sqlalchemy session.

            :return: SQLAlchemy Session
        """
        return self.session

    @property
    def app_name(self):
        """
            Get the App name

            :return: String with app name
        """
        return self.get_app.config['APP_NAME']

    @property
    def app_theme(self):
        """
            Get the App theme name

            :return: String app theme name
        """
        return self.get_app.config['APP_THEME']

    @property
    def app_icon(self):
        """
            Get the App icon location

            :return: String with relative app icon location
        """
        return self.get_app.config['APP_ICON']

    @property
    def languages(self):
        return self.get_app.config['LANGUAGES']

    @property
    def version(self):
        """
            Get the current F.A.B. version

            :return: String with the current F.A.B. version
        """
        return VERSION_STRING

    def _add_global_filters(self):
        self.template_filters = TemplateFilters(self.get_app, self.sm)

    def _add_global_static(self):
        bp = Blueprint('appbuilder', __name__, url_prefix='/static',
                       template_folder='templates', static_folder=self.static_folder,
                       static_url_path=self.static_url_path)
        self.get_app.register_blueprint(bp)

    def _add_admin_views(self):
        self.indexview = self._check_and_init(self.indexview)
        self.add_view_no_menu(self.indexview)
        self.add_view_no_menu(UtilView())
        self.bm.register_views()
        self.sm.register_views()

    def _add_permissions_menu(self, name):
        try:
            self.sm.add_permissions_menu(name)
        except Exception as e:
            log.error("Add Permission on Menu Error: {0}".format(str(e)))

    def _add_menu_permissions(self):
        for category in self.menu.get_list():
            self._add_permissions_menu(category.name)
            for item in category.childs:
                # dont add permission for menu separator
                if item.name != '-':
                    self._add_permissions_menu(item.name)

    def _check_and_init(self, baseview):
        # If class if not instantiated, instantiate it
        # and add db session from security models.
        if hasattr(baseview, 'datamodel'):
            if baseview.datamodel.session is None:
                baseview.datamodel.session = self.session
        if hasattr(baseview, '__call__'):
            baseview = baseview()
        return baseview

    def add_view(self, baseview, name, href="", icon="",
                 label="", category="",
                 category_icon="", category_label=""):
        """
            Add your views associated with menus using this method.
            
            :param baseview:
                A BaseView type class instantiated or not.
                This method will instantiate the class for you if needed.
            :param name:
                The string name that identifies the menu.
            :param href:
                Override the generated href for the menu. You can use an url string or an endpoint name
                if non provided default_view from view will be set as href.
            :param icon:
                Font-Awesome icon name, optional.
            :param label:
                The label that will be displayed on the menu, if absent param name will be used
            :param category:
                The menu category where the menu will be included,
                if non provided the view will be acessible as a top menu.
            :param category_icon:
                Font-Awesome icon name for the category, optional.
            :param category_label:
                The label that will be displayed on the menu, if absent param name will be used

            Examples::
            
                appbuilder = AppBuilder(app, db)
                # Register a view, rendering a top menu without icon.
                appbuilder.add_view(MyModelView(), "My View")
                # or not instantiated
                appbuilder.add_view(MyModelView, "My View")
                # Register a view, a submenu "Other View" from "Other" with a phone icon.
                appbuilder.add_view(MyOtherModelView, "Other View", icon='fa-phone', category="Others")
                # Register a view, with category icon and translation.
                appbuilder.add_view(YetOtherModelView(), "Other View", icon='fa-phone',
                                label=_('Other View'), category="Others", category_icon='fa-envelop',
                                category_label=_('Other View'))
                # Add a link
                appbuilder.add_link("google", href="www.google.com", icon = "fa-google-plus")
        """
        baseview = self._check_and_init(baseview)
        log.info("Registering class %s on menu %s.%s" % (baseview.__class__.__name__, category, name))

        if not self._view_exists(baseview):
            baseview.appbuilder = self
            self.baseviews.append(baseview)
            self._process_ref_related_views()
            if self.app:
                self.register_blueprint(baseview)
                self._add_permission(baseview)
        self.add_link(name=name, href=href, icon=icon, label=label,
                      category=category, category_icon=category_icon,
                      category_label=category_label, baseview=baseview)
        return baseview

    def add_link(self, name, href, icon="", label="", category="", category_icon="", category_label="", baseview=None):
        """
            Add your own links to menu using this method
            
            :param name:
                The string name that identifies the menu.
            :param href:
                Override the generated href for the menu. You can use an url string or an endpoint name
            :param icon:
                Font-Awesome icon name, optional.
            :param label:
                The label that will be displayed on the menu, if absent param name will be used
            :param category:
                The menu category where the menu will be included,
                if non provided the view will be accessible as a top menu.
            :param category_icon:
                Font-Awesome icon name for the category, optional.
            :param category_label:
                The label that will be displayed on the menu, if absent param name will be used

        """
        self.menu.add_link(name=name, href=href, icon=icon, label=label,
                           category=category, category_icon=category_icon,
                           category_label=category_label, baseview=baseview)
        if self.app:
            self._add_permissions_menu(name)
            if category:
                self._add_permissions_menu(category)

    def add_separator(self, category):
        """
            Add a separator to the menu, you will sequentially create the menu
            
            :param category:
                The menu category where the separator will be included.                    
        """
        self.menu.add_separator(category)

    def add_view_no_menu(self, baseview, endpoint=None, static_folder=None):
        """
            Add your views without creating a menu.
            
            :param baseview:
                A BaseView type class instantiated.
                    
        """
        baseview = self._check_and_init(baseview)
        log.info("Registering class %s" % baseview.__class__.__name__)

        if not self._view_exists(baseview):
            baseview.appbuilder = self
            self.baseviews.append(baseview)
            self._process_ref_related_views()
            if self.app:
                self.register_blueprint(baseview, endpoint=endpoint, static_folder=static_folder)
                self._add_permission(baseview)
        else:
            log.warning("View already exists {0} ignoring".format(baseview.__class__.__name__))
        return baseview

    def security_cleanup(self):
        """
            This method is useful if you have changed the name of your menus or classes,
            changing them will leave behind permissions that are not associated with anything.

            You can use it always or just sometimes to
            perform a security cleanup. Warning this will delete any permission
            that is no longer part of any registered view or menu.

            Remember invoke ONLY AFTER YOU HAVE REGISTERED ALL VIEWS
        """
        self.sm.security_cleanup(self.baseviews, self.menu)

    @property
    def get_url_for_login(self):
        return url_for('%s.%s' % (self.sm.auth_view.endpoint, 'login'))

    @property
    def get_url_for_logout(self):
        return url_for('%s.%s' % (self.sm.auth_view.endpoint, 'logout'))

    @property
    def get_url_for_index(self):
        return url_for('%s.%s' % (self.indexview.endpoint, self.indexview.default_view))

    @property
    def get_url_for_userinfo(self):
        return url_for('%s.%s' % (self.sm.user_view.endpoint, 'userinfo'))

    def get_url_for_locale(self, lang):
        return url_for('%s.%s' % (self.bm.locale_view.endpoint, self.bm.locale_view.default_view), locale=lang)

    def _add_permission(self, baseview):
        try:
            self.sm.add_permissions_view(baseview.base_permissions, baseview.__class__.__name__)
        except Exception as e:
            log.error("Add Permission on View Error: {0}".format(str(e)))

    def register_blueprint(self, baseview, endpoint=None, static_folder=None):
        self.get_app.register_blueprint(baseview.create_blueprint(self, endpoint=endpoint, static_folder=static_folder))

    def _view_exists(self, view):
        for baseview in self.baseviews:
            if baseview.__class__ == view.__class__:
                return True
        return False

    def _process_ref_related_views(self):
        try:
            for view in self.baseviews:
                if hasattr(view, 'related_views'):
                    for rel_class in view.related_views:
                        for v in self.baseviews:
                            if isinstance(v, rel_class) and v not in view._related_views:
                                view._related_views.append(v)
        except:
            raise Exception('Use related_views with classes, not instances')


