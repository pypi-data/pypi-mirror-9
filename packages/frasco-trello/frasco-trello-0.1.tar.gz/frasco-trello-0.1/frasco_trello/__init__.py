from frasco import Feature, action, flash, url_for, hook, lazy_translate
from frasco_users import current_user
from .blueprint import create_blueprint
from trello import TrelloClient


class TrelloFeature(Feature):
    name = "trello"
    requires = ["users"]
    blueprints = [create_blueprint]
    defaults = {"app_name": None,
                "scope": "read",
                "expiration": "30days",
                "use_username": False,
                "user_denied_login_message": lazy_translate("Login via Trello was denied")}

    def init_app(self, app):
        self.app = app
        if not self.options["app_name"]:
            self.options["app_name"] = app.config.get('TITLE', 'My App')

        self.oauth = app.features.users.create_oauth_app("trello",
            base_url='https://trello.com/1/',
            request_token_url="OAuthGetRequestToken",
            access_token_url='OAuthGetAccessToken',
            authorize_url='OAuthAuthorizeToken',
            consumer_key=self.options["api_key"],
            consumer_secret=self.options["api_secret"],
            login_view="trello_login.login")

        @self.oauth.tokengetter
        def token_getter(token=None):
            return None
            if not current_user.is_authenticated() or not current_user.trello_oauth_token:
                return
            return (current_user.trello_oauth_token, current_user.trello_oauth_token_secret)

        self.model = app.features.models.ensure_model(app.features.users.model,
            trello_oauth_token=str,
            trello_oauth_token_secret=str,
            trello_user_id=dict(type=str, index=True),
            trello_username=dict(type=str, index=True))

    def create_client(self, token=None, token_secret=None):
        return TrelloClient(
            api_key=self.options["api_key"],
            api_secret=self.options["api_secret"],
            token=token or current_user.trello_oauth_token,
            token_secret=token_secret or current_user.trello_oauth_token_secret)
