from flask import (
    Flask,
    render_template,
    redirect,
    jsonify,
    request,
    g,
    session,
    url_for
)

from core import Cesi
from loggers import ActivityLog
from decorators import (
    is_user_logged_in,
    is_admin,
    is_admin_or_normal_user
)
from run import app, VERSION

cesi = Cesi.getInstance()
activity = ActivityLog.getInstance()

# Open database connection
@app.before_request
def before_request():
    g.db_conn = cesi.get_db_connection()

# Close database connection
@app.teardown_appcontext
def close_connection(_):
    g.db_conn.close()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.errorhandler(400)
def not_found(error):
    return jsonify(message=error.description)

@app.route('/{}/userinfo'.format(VERSION))
@is_user_logged_in()
def user_info():
    return jsonify(username=session['username'], usertypecode=session['usertypecode'])

# Render login page or username, password control
@app.route('/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = g.db_conn.cursor()
        cur.execute("select * from userinfo where username=?",(username,))
        #if query returns an empty list
        if not cur.fetchall():
            session.clear()
            activity.logger.info("Login fail. Username is not available.")
            return redirect('/login?code=invalid')
        else:
            cur.execute("select * from userinfo where username=?",(username,))

            if password == cur.fetchall()[0][1]:
                session['username'] = username
                session['logged_in'] = True
                cur.execute("select * from userinfo where username=?",(username,))
                session['usertypecode'] = cur.fetchall()[0][2]
                activity.logger.info("{} logged in.".format(session['username']))
                return redirect('/')
            else:
                session.clear()
                activity.logger.info("Login fail. Invalid password.")
                return redirect('/login?code=invalid')

    code = request.args.get('code', '')
    return render_template('login.html', code = code, name = cesi.name)

# Logout action
@app.route('/{}/logout/'.format(VERSION), methods = ['GET', 'POST'])
def logout():
    activity.logger.error("{} logged out".format(session['username']))
    session.clear()
    return redirect(url_for('login'))

@app.route('/{}/initdb/'.format(VERSION))
def initdb():
    cesi.drop_database()
    cesi.check_database()
    return jsonify(message="Success")

@app.route('/')
def showMain():
    # get user type
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    username = session['username']
    usertypecode = session['usertypecode']
    return render_template('index.html',
                            name = cesi.name,
                            theme = cesi.theme,
                            username = username,
                            usertypecode = usertypecode)
