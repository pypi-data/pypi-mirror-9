__author__ = 'dpgaspar'

import uuid
import logging

from werkzeug.security import generate_password_hash
from flask import render_template, flash, redirect, session, url_for, request
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL

from flask_openid import SessionWrapper, OpenIDResponse
from ...views import expose, PublicFormView
from flask_babelpkg import lazy_gettext
from .models import User, RegisterUser
from ..forms import RegisterUserOIDForm, RegisterUserDBForm, LoginForm_oid
from ...models.sqla.interface import SQLAInterface
from ...validators import Unique
from ..._compat import as_unicode


log = logging.getLogger(__name__)


def get_first_last_name(fullname):
    names = fullname.split()
    if len(names) > 1:
        return names[0], ' '.join(names[1:])
    elif names:
        return names[0], ''


class BaseRegisterUser(PublicFormView):
    """
        Make your own user registration view and inherit from this class if you
        want to implement a completely different registration process. If not,
        just inherit from RegisterUserDBView or RegisterUserOIDView depending on
        your authentication method.
        then override SecurityManager property that defines the class to use::

            from flask.ext.appbuilder.security.registerviews import RegisterUserDBView

            class MyRegisterUserDBView(BaseRegisterUser):
                email_template = 'register_mail.html'
                ...


            class MySecurityManager(SecurityManager):
               registeruserdbview = MyRegisterUserDBView

        When instantiating AppBuilder set your own SecurityManager class::

            appbuilder = AppBuilder(app, db.session, security_manager_class=MySecurityManager)
    """
    route_base = '/register'
    email_template = 'appbuilder/general/security/register_mail.html'
    """ The template used to generate the email sent to the user """
    email_subject = lazy_gettext('Account activation')
    """ The email subject sent to the user """
    activation_template = 'appbuilder/general/security/activation.html'
    """ The activation template, shown when the user is activated """

    def send_email(self, register_user):
        """
            Method for sending the registration Email to the user
        """
        try:
            from flask_mail import Mail, Message
        except:
            log.error("Install Flask-Mail to use User registration")
            return False
        mail = Mail(self.appbuilder.get_app)
        msg = Message()
        msg.subject = self.email_subject
        url = url_for('.activation', _external=True, activation_hash=register_user.registration_hash)
        msg.html = render_template(self.email_template,
                                   url=url,
                                   username=register_user.username,
                                   first_name=register_user.first_name,
                                   last_name=register_user.last_name)
        msg.recipients = [register_user.email]
        try:
            mail.send(msg)
        except Exception as e:
            log.error("Send email exception: {0}".format(str(e)))
            return False
        return True

    def add_registration(self, username, first_name, last_name, email, password=''):
        """
            Add a registration request for the user.

        :rtype : RegisterUser
        """
        register_user = RegisterUser()
        register_user.username = username
        register_user.email = email
        register_user.first_name = first_name
        register_user.last_name = last_name
        register_user.password = generate_password_hash(password)
        register_user.registration_hash = str(uuid.uuid1())
        try:
            self.appbuilder.get_session.add(register_user)
        except Exception as e:
            log.exception("Add record error: {0}".format(str(e)))
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
            return None
        if self.send_email(register_user):
            self.appbuilder.get_session.commit()
            flash(as_unicode(self.message), 'info')
        else:
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
        return register_user

    @expose('/activation/<string:activation_hash>')
    def activation(self, activation_hash):
        """
            Endpoint to expose an activation url, this url
            is sent to the user by email, when accessed the user is inserted
            and activated
        """
        reg = self.appbuilder.get_session.query(RegisterUser).filter(
            RegisterUser.registration_hash == activation_hash).scalar()
        try:
            if not self.appbuilder.sm.add_user(username=reg.username,
                                               email=reg.email,
                                               first_name=reg.first_name,
                                               last_name=reg.last_name,
                                               role=self.appbuilder.sm.get_role_by_name(
                                                       self.appbuilder.sm.auth_user_registration_role),
                                               password=reg.password):
                raise Exception('Could not add user to DB')
            self.appbuilder.get_session.delete(reg)
        except Exception as e:
            log.exception("Add record on user activation error: {0}".format(str(e)))
            flash(as_unicode(self.error_message), 'danger')
            self.appbuilder.get_session.rollback()
            return redirect(self.appbuilder.get_url_for_index)
        self.appbuilder.get_session.commit()
        return render_template(self.activation_template,
                               username=reg.username,
                               first_name=reg.first_name,
                               last_name=reg.last_name,
                               appbuilder=self.appbuilder)


class RegisterUserDBView(BaseRegisterUser):
    """
        View for Registering a new user, auth db mode
    """
    form = RegisterUserDBForm
    """ The WTForm form presented to the user to register himself """
    form_title = lazy_gettext('Fill out the registration form')
    """ The form title """
    redirect_url = '/'
    error_message = lazy_gettext('Not possible to register you at the moment, try again later')
    message = lazy_gettext('Registration sent to your email')
    """ The message shown on a successful registration """

    def form_get(self, form):
        datamodel_user = SQLAInterface(User, self.appbuilder.get_session)
        datamodel_register_user = SQLAInterface(RegisterUser, self.appbuilder.get_session)
        if len(form.username.validators) == 1:
            form.username.validators.append(Unique(datamodel_user, 'username'))
            form.username.validators.append(Unique(datamodel_register_user, 'username'))
        if len(form.email.validators) == 2:
            form.email.validators.append(Unique(datamodel_user, 'email'))
            form.email.validators.append(Unique(datamodel_register_user, 'email'))


    def form_post(self, form):
        self.add_registration(username=form.username.data,
                                              first_name=form.first_name.data,
                                              last_name=form.last_name.data,
                                              email=form.email.data,
                                              password=form.password.data)


class RegisterUserOIDView(BaseRegisterUser):
    """
        View for Registering a new user, auth OID mode
    """
    route_base = '/register'

    form = RegisterUserOIDForm
    form_title = lazy_gettext('Fill out the registration form')
    error_message = lazy_gettext('Not possible to register you at the moment, try again later')
    message = lazy_gettext('Registration sent to your email')
    default_view = 'form_oid_post'

    @expose("/formoidone", methods=['GET', 'POST'])
    def form_oid_post(self, flag=True):
        if flag:
            self.oid_login_handler(self.form_oid_post, self.appbuilder.sm.oid)
        form = LoginForm_oid()
        if form.validate_on_submit():
            session['remember_me'] = form.remember_me.data
            return self.appbuilder.sm.oid.try_login(form.openid.data, ask_for=['email', 'fullname'])
        resp = session.pop('oid_resp', None)
        if resp:
            self._init_vars()
            form = self.form.refresh()
            self.form_get(form)
            form.username.data = resp.email
            first_name, last_name = get_first_last_name(resp.fullname)
            form.first_name.data = first_name
            form.last_name.data = last_name
            form.email.data = resp.email
            widgets = self._get_edit_widget(form=form)
            #self.update_redirect()
            return self.render_template(self.form_template,
                                   title=self.form_title,
                                   widgets=widgets,
                                   form_action='form',
                                   appbuilder=self.appbuilder)
        else:
            flash(as_unicode(self.error_message), 'warning')
            return redirect(self.get_redirect())

    def oid_login_handler(self, f, oid):
        """
            Hackish method to make use of oid.login_handler decorator.
        """
        if request.args.get('openid_complete') != u'yes':
            return f(False)
        consumer = Consumer(SessionWrapper(self), oid.store_factory())
        openid_response = consumer.complete(request.args.to_dict(),
                                            oid.get_current_url())
        if openid_response.status == SUCCESS:
            return self.after_login(OpenIDResponse(openid_response, []))
        elif openid_response.status == CANCEL:
            oid.signal_error(u'The request was cancelled')
            return redirect(oid.get_current_url())
        oid.signal_error(u'OpenID authentication error')
        return redirect(oid.get_current_url())

    def after_login(self, resp):
        """
            Method that adds the return OpenID response object on the session
            this session key will be deleted
        """
        session['oid_resp'] = resp

    def form_get(self, form):
        datamodel_user = SQLAInterface(User, self.appbuilder.get_session)
        datamodel_register_user = SQLAInterface(RegisterUser, self.appbuilder.get_session)
        if len(form.username.validators) == 1:
            form.username.validators.append(Unique(datamodel_user, 'username'))
            form.username.validators.append(Unique(datamodel_register_user, 'username'))
        if len(form.email.validators) == 2:
            form.email.validators.append(Unique(datamodel_user, 'email'))
            form.email.validators.append(Unique(datamodel_register_user, 'email'))

    def form_post(self, form):
        self.add_registration(username=form.username.data,
                                              first_name=form.first_name.data,
                                              last_name=form.last_name.data,
                                              email=form.email.data)
