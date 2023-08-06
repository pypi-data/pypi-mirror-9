from frasco import Blueprint, redirect, url_for, request, flash


def create_blueprint(app):
    bp = Blueprint("twitter_login", __name__)

    feature = app.features.twitter
    users = app.features.users

    @bp.route('/login/twitter')
    def login():
        callback_url = url_for('.callback', next=request.args.get('next'), _external=True)
        return feature.api.authorize(callback=callback_url)

    @bp.route('/login/twitter/callback')
    def callback():
        resp = feature.api.authorized_response()
        if resp is None:
            flash(feature.options["user_denied_login_message"], "error")
            return redirect(url_for("users.login"))

        attrs = {"twitter_screenname": resp['screen_name'],
                 "twitter_oauth_token": resp['oauth_token'],
                 "twitter_oauth_token_secret": resp['oauth_token_secret']}
        defaults = {}
        if feature.options["use_screenname_as_username"]:
            defaults[users.options["username_column"]] = resp["screen_name"]

        return users.oauth_login("twitter", "twitter_screenname", resp["screen_name"], attrs, defaults)

    return bp