from frasco import Feature, action, flash, url_for, hook, session, lazy_translate
from frasco_users import current_user
from .blueprint import create_blueprint


class FacebookFeature(Feature):
    name = "facebook"
    requires = ["users"]
    blueprints = [create_blueprint]
    defaults = {"use_name_as_username": False,
                "use_email": True,
                "scope": "email",
                "save_data": ["first_name", "last_name"],
                "user_denied_login_message": lazy_translate("Login via Facebook was denied")}

    def init_app(self, app):
        self.app = app
        self.api = app.features.users.create_oauth_app("facebook",
            base_url='https://graph.facebook.com/',
            request_token_url=None,
            access_token_url='/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
            consumer_key=self.options["app_id"],
            consumer_secret=self.options["app_secret"],
            request_token_params={'scope': self.options['scope']},
            login_view="facebook_login.login")

        @self.api.tokengetter
        def token_getter():
            if not current_user.is_authenticated() or not current_user.facebook_access_token:
                return
            return (current_user.facebook_access_token, "")

        self.model = app.features.models.ensure_model(app.features.users.model,
            facebook_access_token=str,
            facebook_token_expires=dict(type=int, index=True),
            facebook_name=str,
            facebook_email=str,
            facebook_id=dict(type=str, index=True))
