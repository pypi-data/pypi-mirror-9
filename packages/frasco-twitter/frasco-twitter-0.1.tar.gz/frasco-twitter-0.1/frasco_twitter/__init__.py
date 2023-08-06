from frasco import Feature, action, flash, url_for, hook, lazy_translate
from frasco_users import current_user
from .blueprint import create_blueprint


class TwitterFeature(Feature):
    name = "twitter"
    requires = ["users"]
    blueprints = [create_blueprint]
    defaults = {"use_screenname_as_username": False,
                "user_denied_login_message": lazy_translate("Login via Twitter was denied")}

    def init_app(self, app):
        self.app = app
        self.api = app.features.users.create_oauth_app("twitter",
            base_url='https://api.twitter.com/1.1/',
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authenticate',
            consumer_key=self.options["consumer_key"],
            consumer_secret=self.options["consumer_secret"],
            login_view="twitter_login.login")

        @self.api.tokengetter
        def token_getter(token=None):
            if not current_user.is_authenticated() or not current_user.twitter_oauth_token:
                return
            return (current_user.twitter_oauth_token, current_user.twitter_oauth_token_secret)

        self.model = app.features.models.ensure_model(app.features.users.model,
            twitter_oauth_token=str,
            twitter_oauth_token_secret=str,
            twitter_screenname=dict(type=str, index=True))

    @action("post_twitter_update", default_option="status")
    def post_update(self, status):
        self.api.post("statuses/update.json", data={"status": status})
