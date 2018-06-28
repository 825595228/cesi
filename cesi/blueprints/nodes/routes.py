from flask import (
    Blueprint,
    jsonify,
    session
)

from core import Cesi
from decorators import (
    is_user_logged_in,
    is_admin_or_normal_user,
    is_admin
)
from util import JsonValue
from loggers import ActivityLog

nodes = Blueprint('nodes', __name__)
cesi = Cesi.getInstance()
activity = ActivityLog.getInstance()

@nodes.route('/')
@is_user_logged_in()
def get_node_names():
    connected = []
    not_connected = []
    for node in cesi.nodes:
        if node.is_connected:
            connected.append(node.name)
        else:
            not_connected.append(node.name)

    return jsonify(
        nodes={
            'connected': connected,
            'not_connected': not_connected
        }
    )

@nodes.route('/<node_name>/')
@is_user_logged_in()
def get_node(node_name):
    node = cesi.get_node_or_400(node_name)
    return jsonify(node.serialize())

@nodes.route('/<node_name>/processes/')
@is_user_logged_in()
def get_node_processes(node_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    return jsonify(node.serialize_processes())

@nodes.route('/<node_name>/processes/<process_name>/')
@is_user_logged_in()
def get_process(node_name, process_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    process = node.get_process_or_400(process_name)
    return jsonify(process.serialize())

@nodes.route('/<node_name>/processes/<process_name>/start/')
@is_user_logged_in("Illegal request for start to {node_name} node's {process_name} process.")
@is_admin_or_normal_user("Unauthorized user request for start.Start event fail for {node_name} node's {process_name} process.")
def start_process(node_name, process_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    status, msg = node.start_process(process_name)
    if status:
        activity.logger.info("{} started {} node's {} process.".format(session['username'], node_name, process_name))
        return JsonValue.success(node=node, process_name=process_name, event_name="start")
    else:
        activity.logger.info("{} unsuccessful start event {} node's {} process.".format(session['username'], node_name, process_name))
        return jsonify(message=msg)

@nodes.route('/<node_name>/processes/<process_name>/stop/')
@is_user_logged_in("Illegal request for stop to {node_name} node's {process_name} process.")
@is_admin_or_normal_user("Unauthorized user request for stop.Stop event fail for {node_name} node's {process_name} process.")
def stop_process(node_name, process_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    status, msg = node.stop_process(process_name)
    if status:
        activity.logger.info("{} stopped {} node's {} process.".format(session['username'], node_name, process_name))
        return JsonValue.success(node=node, process_name=process_name, event_name="stop")
    else:
        activity.logger.info("{} unsuccessful stop event {} node's {} process.".format(session['username'], node_name, process_name))
        return jsonify(message=msg)

@nodes.route('/<node_name>/processes/<process_name>/restart/')
@is_user_logged_in("Illegal request for restart to {node_name} node's {process_name} process.")
@is_admin_or_normal_user("Unauthorized user request for restart.Restart event fail for {node_name} node's {process_name} process.")
def restart_process(node_name, process_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    status, msg = node.restart_process(process_name)
    if status:
        activity.logger.info("{} restarted {} node's {} process.".format(session['username'], node_name, process_name))
        return JsonValue.success(node=node, process_name=process_name, event_name="restart")
    else:
        activity.logger.info("{} unsuccessful restart event {} node's {} process.".format(session['username'], node_name, process_name))
        return jsonify(message=msg)

@nodes.route('/<node_name>/processes/<process_name>/log/')
@is_user_logged_in("Illegal request for read log to {node_name} node's {process_name} process.")
def read_process_log(node_name, process_name):
    if session['usertype'] == 0 or session['usertype'] == 1 or session['usertype'] == 2:
        node = cesi.get_node_or_400(node_name)
        if not node.is_connected:
            return jsonify(message="Node is not connected")

        log_string = node.connection.supervisor.tailProcessStdoutLog(process_name, 0, 500)[0]
        log_list = log_string.split("\n")[1:-1]
        activity.logger.info("{} read log {} node's {} process.".format(session['username'], node_name, process_name))
        return jsonify(status="success", log=log_list)
    else:
        activity.logger.info("{} is unauthorized user request for read log. Read log event fail for {} node's {} process.".format(session['username'], node_name, process_name))
        return jsonify(status="error", message="You are not authorized for this action")

@nodes.route('/<node_name>/all-processes/start/')
@is_user_logged_in("Illegal request for start to {node_name} node's all processes.")
@is_admin_or_normal_user("Unauthorized user request for start.Start event fail for {node_name} node's all processes.")
def start_all_process(node_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    for process in node.processes:
        if not process.state == 20:
            status, msg = node.start_process(process.name)
            if status:
                activity.logger.info("{} started {} node's {} process.".format(session['username'], node_name, process.name))
            else:
                activity.logger.info("{} unsuccessful start event {} node's {} process.".format(session['username'], node_name, process.name))

    return jsonify(message="success")

@nodes.route('/<node_name>/all-processes/stop/')
@is_user_logged_in("Illegal request for stop to {node_name} node's all processes.")
@is_admin_or_normal_user("Unauthorized user request for stop.Stop event fail for {node_name} node's all processes.")
def stop_all_process(node_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    for process in node.processes:
        if not process.state == 0:
            status, msg = node.stop_process(process.name)
            if status:
                activity.logger.info("{} stopped {} node's {} process.".format(session['username'], node_name, process.name))
            else:
                activity.logger.info("{} unsuccessful stop event {} node's {} process.".format(session['username'], node_name, process.name))

    return jsonify(message="success")

@nodes.route('/<node_name>/all-processes/restart/')
@is_user_logged_in("Illegal request for restart to {node_name} node's all processes.")
@is_admin_or_normal_user("Unauthorized user request for restart.Restart event fail for {node_name} node's all processes.")
def restart_all_process(node_name):
    node = cesi.get_node_or_400(node_name)
    if not node.is_connected:
        return jsonify(message="Node is not connected")

    for process in node.processes:
        if not process.state == 0:
            status, msg = node.stop_process(process.name)
            if status:
                print("Process stopped!")
            else:
                print(msg)

        status, msg = node.start_process(process.name)
        if status:
            activity.logger.info("{} restarted {} node's {} process.".format(session['username'], node_name, process.name))
        else:
            activity.logger.info("{} unsuccessful restart event {} node's {} process.".format(session['username'], node_name, process.name))

    return jsonify(message="success")