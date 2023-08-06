from frasco import Blueprint, redirect, url_for, request, flash
from werkzeug import url_quote


def create_blueprint(app):
    bp = Blueprint("trello_login", __name__)

    feature = app.features.trello
    users = app.features.users

    @bp.route('/login/trello')
    def login():
        callback_url = url_for('.callback', next=request.args.get('next'), _external=True)
        return feature.oauth.authorize(callback_url,
            name=feature.options["app_name"],
            scope=feature.options["scope"],
            expiration=feature.options["expiration"])

    @bp.route('/login/trello/callback')
    def callback():
        resp = feature.oauth.authorized_response()
        if resp is None:
            flash(feature.options["user_denied_login_message"], "error")
            return redirect(url_for("users.login"))

        client = feature.create_client(resp['oauth_token'], resp['oauth_token_secret'])
        member = client.get_member('me')

        attrs = {"trello_oauth_token": resp['oauth_token'],
                 "trello_oauth_token_secret": resp['oauth_token_secret'],
                 "trello_user_id": member.id,
                 "trello_username": member.username}
        defaults = {}
        if feature.options["use_username"]:
            defaults[users.options["username_column"]] = member.username

        return users.oauth_login("trello", "trello_user_id", member.id, attrs, defaults)

    return bp