from frasco import Blueprint, session, redirect, url_for, request, flash


def create_blueprint(app):
    bp = Blueprint("facebook_login", __name__, static_folder="static")

    feature = app.features.facebook
    users = app.features.users

    @bp.route('/login/facebook')
    def login():
        callback_url = url_for('.callback', next=request.args.get('next'), _external=True)
        return feature.api.authorize(callback=callback_url)

    @bp.route('/login/facebook/callback')
    def callback():
        resp = feature.api.authorized_response()
        if resp is None:
            flash(feature.options["user_denied_login_message"], "error")
            return redirect(url_for("users.login"))

        me = feature.api.get("/me", token=[resp['access_token']])
        attrs = {"facebook_access_token": resp['access_token'],
                 "facebook_token_expires": resp['expires'],
                 "facebook_id": str(me.data["id"]),
                 "facebook_name": me.data["name"],
                 "facebook_email": me.data["email"]}
        defaults = {}
        if feature.options["use_email"]:
            defaults[users.options["email_column"]] = me.data["email"]
        if feature.options["use_name_as_username"]:
            defaults[users.options["username_column"]] = me.data["name"]
        for k in feature.options["save_data"]:
            if k in me.data:
                defaults[k] = me.data[k]

        return users.oauth_login("facebook", "facebook_id", str(me.data["id"]), attrs, defaults)

    return bp