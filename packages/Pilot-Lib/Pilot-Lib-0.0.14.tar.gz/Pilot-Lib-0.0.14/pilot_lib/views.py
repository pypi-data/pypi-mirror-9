
import os
from hashlib import sha1
import time
import base64
import hmac
import urllib
import pkg_resources
import utils
from flask import abort, redirect, request, url_for, jsonify
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask_pilot import Pilot, route, flash_error, flash_success, flash_info
from flask_recaptcha import ReCaptcha
from ses_mailer import TemplateMail
from flask_wtf import Form
from wtforms import SelectField
from flask.ext.assets import Environment, Bundle

class TemplatesLoader(object):
    @classmethod
    def init_app(cls, app):
        path = pkg_resources.resource_filename(__name__, "templates")
        utils.add_path_to_jinja(app, path)

        # Register Assets
        _dir_ = os.path.dirname(__file__)
        env = Pilot.assets
        env.load_path = [
            Pilot._app.static_folder,
            os.path.join(_dir_, 'static'),
        ]
        env.register(
            'pilotlib_js',
            Bundle(
                "js/s3upload.js",
                output='pilotlib.js'
            )
        )
        env.register(
            'pilotlib_css',
            Bundle(
                'css/pilotlib_style.css',
                output='pilotlib.css'
            )
        )
Pilot.bind(TemplatesLoader.init_app)

class S3UploadMixin(object):
    """
    This mixin allow you to upload file directly to S3 using javascript
    """

    def sign_s3_upload(self):
        """
        Allow to create Signed object to upload to S3 via JS
        """
        AWS_ACCESS_KEY = self.get_config('AWS_ACCESS_KEY_ID')
        AWS_SECRET_KEY = self.get_config('AWS_SECRET_ACCESS_KEY')
        S3_BUCKET = self.get_config('S3_BUCKET')

        object_name = request.args.get('s3_object_name')
        mime_type = request.args.get('s3_object_type')
        expires = long(time.time()+10)
        amz_headers = "x-amz-acl:public-read"
        put_request = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)
        signature = base64.encodestring(hmac.new(AWS_SECRET_KEY, put_request, sha1).digest())
        signature = urllib.quote(urllib.quote_plus(signature.strip()))
        url = 'https://s3.amazonaws.com/%s/%s' % (S3_BUCKET, object_name)
        return jsonify({
            'signed_request': '%s?AWSAccessKeyId=%s&Expires=%d&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
             'url': url
          })

def login_view(model,
          logout_view=None,
          signin_view=None,
          login_message="Please Login",
          allow_signup=True,
          view_template=None):

    """
    :params model: The user model instance active-sqlachemy
    :view: The base view
    :logout_view: The view after logout
    :signin_view: The view after sign in
    :login_message: The message to show when login
    :allow_signup: To allow signup on the page
    :param view_template: The directory containing the view pages

    Doc:
    Login is a view that allows you to login/logout use.
    You must create a Pilot view called `Login` to activate it

    LoginView = app.views.login(model=model.User, signin_view="Account:index")
    class Login(LoginView, Pilot):
        route_base = "/account"


    """

    User = model
    tmail = TemplateMail()
    recaptcha = ReCaptcha()

    # Login

    login_view = "Login:login"
    login_manager = LoginManager()
    login_manager.login_view = login_view
    login_manager.login_message = login_message
    login_manager.login_message_category = "error"

    # Start binding
    Pilot.bind(tmail.init_app)
    Pilot.bind(model.db.init_app)
    Pilot.bind(login_manager.init_app)
    Pilot.bind(recaptcha.init_app)


    @login_manager.user_loader
    def load_user(userid):
        return User.get(userid)

    if not view_template:
        view_template = "PilotLib/Templates/Login"
    template_page = view_template + "/%s.html"


    class Login(S3UploadMixin):
        route_base = "/"

        @classmethod
        def signup_handler(cls):
            """
            To handle the signup process. Must still bind to the app
             :returns User object:
            """
            if request.method == "POST":
                name = request.form.get("name")
                email = request.form.get("email")
                password = request.form.get("password")
                password2 = request.form.get("password2")
                profile_pic_url = request.form.get("profile_pic_url", None)
                
                if not name:
                    raise UserWarning("Name is required")
                elif not utils.is_valid_email(email):
                    raise UserWarning("Invalid email address '%s'" % email)
                elif not password.strip() or password.strip() != password2.strip():
                    raise UserWarning("Passwords don't match")
                elif not utils.is_valid_password(password):
                    raise UserWarning("Invalid password")
                else:
                    return User.new(email=email,
                                    password=password.strip(),
                                    name=name,
                                    profile_pic_url=profile_pic_url)

        @classmethod
        def change_login_handler(cls, user_context=None, email=None):
            if not user_context:
                user_context = current_user
            if not email:
                email = request.form.get("email").strip()

            if not utils.is_valid_email(email):
                raise UserWarning("Invalid email address '%s'" % email)
            else:
                if email != user_context.email and User.find_by_email(email):
                    raise UserWarning("Email exists already '%s'" % email)
                elif email != user_context.email:
                    user_context.update(email=email)
                    return True
            return False

        @classmethod
        def change_password_handler(cls, user_context=None, password=None,
                                    password2=None):
            if not user_context:
                user_context = current_user
            if not password:
                password = request.form.get("password").strip()
            if not password2:
                password2 = request.form.get("password2").strip()

            if password:
                if password != password2:
                    raise UserWarning("Password don't match")
                elif not utils.is_valid_password(password):
                    raise UserWarning("Invalid password")
                else:
                    user_context.set_password(password)
                    return True
            else:
                raise UserWarning("Password is empty")

        @classmethod
        def reset_password_handler(cls, user_context=None, send_notification=False):
            """
            Reset the password
            :returns string: The new password string
            """
            if not user_context:
                user_context = current_user

            new_password = user_context.set_random_password()

            if send_notification:
                tmail.send("reset-password",
                           to=user_context.email,
                           new_password=new_password,
                           name=user_context.name,
                           login_url=url_for(login_manager.login_view, _external=True)
                           )

            return new_password

        # --- LOGIN
        def login(self):
            """
            Login page
            """
            logout_user()
            return self.render(login_url_next=request.args.get("next", ""),
                               view_template=template_page % "login")

        @route("/loginp", methods=["POST"])
        def login_post(self):
            """
            Accept the POST login
            """
            email = request.form.get("email").strip()
            password = request.form.get("password").strip()

            if not email or not password:
                flash_error("Email or Password is empty")
                return redirect(url_for(login_view, next=request.form.get("next")))
            account = User.find_by_email(email)
            if account and account.password_matched(password):
                login_user(account)
                return redirect(request.form.get("next") or url_for(signin_view))
            else:
                flash_error("Email or Password is invalid")
                return redirect(url_for(login_view, next=request.form.get("next")))

        # --- LOGOUT
        def logout(self):
            logout_user()
            flash_success("Logout successfully!")
            return redirect(url_for(logout_view or login_view))

        # --- LOST PASSWORD
        @route("lost-password")
        def lost_password(self):
            logout_user()
            return self.render(view_template=template_page % "lost_password")

        @route("lost-passwordp", methods=["POST"])
        def lost_password_post(self):
            email = request.form.get("email")
            user = User.find_by_email(email)
            if user:
                self.reset_password_handler(user_context=user,
                                            send_notification=True)
                flash_success("A new password has been sent to '%s'" % email)
            else:
                flash_error("Invalid email address")
            return redirect(url_for(login_view))

        # --- RESET PASSWORD
        def reset_password(self, token):
            pass

        # --
        def signup(self):
            logout_user()
            if not allow_signup:
                abort(401)
            return self.render(login_url_next=request.args.get("next", ""),
                               view_template=template_page % "signup")

        @route("signupp", methods=["POST"])
        def signup_post(self):
            # reCaptcha
            if not recaptcha.verify():
                flash_error("Invalid Security code")
                return redirect(url_for("Login:signup", next=request.form.get("next")))
            try:
                new_account = self.signup_handler()
                login_user(new_account)
                flash_success("Congratulations! ")
                return redirect(request.form.get("next") or url_for(signin_view))
            except Exception as ex:
                flash_error(ex.message)
            return redirect(url_for("Login:signup", next=request.form.get("next")))

        @route("/account-settings")
        @login_required
        def account_settings(self):
                return self.render(view_template=template_page % "account_settings")

        @route("/change-login", methods=["POST"])
        @login_required
        def change_login(self):
            confirm_password = request.form.get("confirm-password").strip()
            try:
                if current_user.password_matched(confirm_password):
                    self.change_login_handler()
                    flash_success("Login Info updated successfully!")
                else:
                    flash_error("Invalid password")
            except Exception as ex:
                flash_error("Error: %s" % ex.message)
            return redirect(url_for("Login:account_settings"))

        @route("/change-password", methods=["POST"])
        @login_required
        def change_password(self):
            try:
                confirm_password = request.form.get("confirm-password").strip()
                if current_user.password_matched(confirm_password):
                    self.change_password_handler()
                    flash_success("Password updated successfully!")
                else:
                    flash_error("Invalid password")
            except Exception as ex:
                flash_error("Error: %s" % ex.message)
            return redirect(url_for("Login:account_settings"))

        @route("/change-info", methods=["POST"])
        @login_required
        def change_info(self):
            name = request.form.get("name").strip()
            profile_pic_url = request.form.get("profile_pic_url").strip()

            data = {}
            if name and name != current_user.name:
                data.update({"name": name})
            if profile_pic_url:
                data.update({"profile_pic_url": profile_pic_url})
            if data:
                current_user.update(**data)
                flash_success("Account info updated successfully!")
            return redirect(url_for("Login:account_settings"))

        @route("/change-profile-pic", methods=["POST"])
        @login_required
        def change_profile_pic(self):
            profile_pic_url = request.form.get("profile_pic_url").strip()
            _ajax = request.form.get("_ajax", None)
            if profile_pic_url:
                current_user.update(profile_pic_url=profile_pic_url)
            if _ajax:
                return jsonify({})
            return redirect(url_for("Login:account_settings"))

    return Login

def user_admin_view(model, login_view, view_template=None):
    """
    :param model: The User class model
    :param login_view: The login view interface
    :param view_template: The directory containing the view pages
    :return: UserAdmin

    Doc:
    User Admin is a view that allows you to admin users.
    You must create a Pilot view called `UserAdmin` to activate it

    UserAdmin = app.views.user_admin(User, Login)
    class UserAdmin(UserAdmin, Pilot):
        pass

    The user admin create some global available vars under '__.user_admin'

    It's also best to add some security access on it
    class UserAdmin(UserAdmin, Pilot):
        decorators = [login_required]

    You can customize the user info page (::get) by creating the directory in your
    templates dir, and include the get.html inside of it

    ie:
    >/admin/templates/UserAdmin/get.html

    <div>
        {% include "PilotLib/Templates/UserAdmin/get.html" %}
    <div>

    <div>Hello {{ __.user_admin.user.name }}<div>

    """
    User = model
    LoginView = login_view

    if not view_template:
        view_template = "PilotLib/Templates/UserAdmin"
    template_page = view_template + "/%s.html"

    class AdminForm(Form):
        """
        Help create a simple form
        """
        user_role = SelectField(choices=[(role, role) for i, role in enumerate(User.all_roles)])
        user_status = SelectField(choices=[(status, status) for i, status in enumerate(User.all_status)])

    class UserAdmin(object):
        route_base = "user-admin"

        @classmethod
        def search_handler(cls, per_page=20):
            """
            To initiate a search
            """
            page = request.args.get("page", 1)
            show_deleted = True if request.args.get("show-deleted") else False
            name = request.args.get("name")
            email = request.args.get("email")

            users = User.all(include_deleted=show_deleted)
            users = users.order_by(User.name.asc())
            if name:
                users = users.filter(User.name.contains(name))
            if email:
                users = users.filter(User.email.contains(email))

            users = users.paginate(page=page, per_page=per_page)

            cls.__(user_admin=dict(
                form=AdminForm(),
                users=users,
                search_query={
                       "excluded_deleted": request.args.get("show-deleted"),
                       "role": request.args.get("role"),
                       "status": request.args.get("status"),
                       "name": request.args.get("name"),
                       "email": request.args.get("email")
                    }
                ))
            return users

        @classmethod
        def get_user_handler(cls, id):
            """
            Get a user
            """
            user = User.get(id, include_deleted=True)
            if not user:
                abort(404, "User doesn't exist")
            cls.__(user_admin=dict(user=user, form=AdminForm()))
            return user

        def index(self):
            self.search_handler()
            return self.render(view_template=template_page % "index")

        def get(self, id):
            self.get_user_handler(id)
            return self.render(view_template=template_page % "get")

        def post(self):
            try:
                id = request.form.get("id")
                user = User.get(id, include_deleted=True)
                if not user:
                    flash_error("Can't change user info. Invalid user")
                    return redirect(url_for("UserAdmin:index"))

                delete_entry = True if request.form.get("delete-entry") else False
                if delete_entry:
                    user.update(status=user.STATUS_SUSPENDED)
                    user.delete()
                    flash_success("User DELETED Successfully!")
                    return redirect(url_for("UserAdmin:get", id=id))

                email = request.form.get("email")
                password = request.form.get("password")
                password2 = request.form.get("password2")
                name = request.form.get("name")
                role = request.form.get("user_role")
                status = request.form.get("user_status")
                upd = {}
                if email and email != user.email:
                    LoginView.change_login_handler(user_context=user)
                if password and password2:
                    LoginView.change_password_handler(user_context=user)
                if name != user.name:
                    upd.update({"name": name})
                if role and role != user.role:
                    upd.update({"role": role})
                if status and status != user.status:
                    if user.is_deleted and status == user.STATUS_ACTIVE:
                        user.delete(False)
                    upd.update({"status": status})
                if upd:
                    user.update(**upd)
                flash_success("User's Info updated successfully!")

            except Exception as ex:
                flash_error("Error: %s " % ex.message)
            return redirect(url_for("UserAdmin:get", id=id))


        @route("reset-password", methods=["POST"])
        def reset_password(self):
            try:
                id = request.form.get("id")
                user = User.get(id)
                if not user:
                    flash_error("Can't reset password. Invalid user")
                    return redirect(url_for("User:index"))

                password = LoginView.reset_password_handler(user_context=user,
                                                        send_notification=True)
                flash_success("User's password reset successfully!")
            except Exception as ex:
                flash_error("Error: %s " % ex.message)
            return redirect(url_for("UserAdmin:get", id=id))

        @route("create", methods=["POST"])
        def create(self):
            try:
                account = LoginView.signup_handler()
                account.set_role(request.form.get("role", "USER"))
                flash_success("User created successfully!")
                return redirect(url_for("UserAdmin:get", id=account.id))
            except Exception as ex:
                flash_error("Error: %s" % ex.message)
            return redirect(url_for("UserAdmin:index"))

    return UserAdmin


def error_view(view_template=None):
    """
    Create the Error view
    Must be instantiated

    import error_view
    ErrorView = error_view()

    :param view_template: The directory containing the view pages
    :return:
    """
    if not view_template:
        view_template = "PilotLib/Templates/Error"

    template_page = "%s/index.html" % view_template

    class Error(Pilot):
        """
        Error Views
        """
        @classmethod
        def register(cls, app, **kwargs):
            super(cls, cls).register(app, **kwargs)

            @app.errorhandler(400)
            def error_400(error):
                return cls.index(error, 400)

            @app.errorhandler(401)
            def error_401(error):
                return cls.index(error, 401)

            @app.errorhandler(403)
            def error_403(error):
                return cls.index(error, 403)

            @app.errorhandler(404)
            def error_404(error):
                return cls.index(error, 404)

            @app.errorhandler(500)
            def error_500(error):
                return cls.index(error, 500)

            @app.errorhandler(503)
            def error_503(error):
                return cls.index(error, 503)

        @classmethod
        def index(cls, error, code):
            cls.__(page_title="Error %s" % code)

            return cls.render(error=error, view_template=template_page), code
    return Error
ErrorView = error_view()

def contact_view(view_template=None):
    if not view_template:
        view_template = "PilotLib/Templates/Contact"

    template_page = "%s/index.html" % view_template


def maintenance_view(view_template=None, page_title=""):
    """
    Create the Maintenance view
    Must be instantiated

    import maintenance_view
    MaintenanceView = maintenance_view()

    :param view_template: The directory containing the view pages
    :return:
    """
    if not view_template:
        view_template = "PilotLib/Templates/Maintenance"

    template_page = "%s/index.html" % view_template

    class Maintenance(Pilot):
        """
        Error Views
        """
        @classmethod
        def index(cls):
            cls.__(page_title=page_title)
            return cls.render(view_template=template_page), 503
    return Maintenance