from flask import Blueprint, jsonify, session, request

from decorators import is_user_logged_in
from loggers import ActivityLog
import controllers

profile = Blueprint("profile", __name__)
activity = ActivityLog.getInstance()


@profile.route("/", methods=["GET"])
@is_user_logged_in("Illegal request to get your own information")
def get_own_info():
    user = controllers.get_user(session["username"])
    print(user)
    return jsonify(status="success", user=user)


@profile.route("/password/", methods=["PUT"])
@is_user_logged_in("Illegal request to change your own password.")
def change_own_password():
    username = session["username"]
    data = request.get_json()
    old_password = data.get("oldPassword")
    new_password = data.get("newPassword")
    if old_password == "" or new_password == "":
        return jsonify(status="error", message="Please enter valid value")

    result = controllers.validate_user(username, old_password)
    if not result:
        activity.logger.error(
            "Old password is wrong to change {} 's password.".format(username)
        )
        return jsonify(status="error", message="Old password is wrong")

    controllers.update_user_password(username, new_password)
    activity.logger.error("{} user changed the own password.".format(username))
    return jsonify(status="success")
