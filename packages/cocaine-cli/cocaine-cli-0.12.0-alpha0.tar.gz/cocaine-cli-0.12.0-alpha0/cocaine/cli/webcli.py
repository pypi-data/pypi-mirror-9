import json
import click
import getpass
from os.path import expanduser, join, isfile
import os

import requests

from config_reader import ProjectReader, VersionReader

import logging
log = logging.getLogger()
log.setLevel(logging.INFO)

AUTH_FILE = join(expanduser("~"), ".cocaine-pipelinerc")
PROJECT_FILE = './project.json'

NO_AUTH_COMMANDS = ("login", "init")
NO_CONFIG_COMMANDS = ("login", "init", "reschedule", "tasks", "status")

USER = None
BASE = None
CONFIG = {}

def _command_need_auth(cmd):
    return not cmd in NO_AUTH_COMMANDS

def _command_need_config(cmd):
    return not cmd in NO_CONFIG_COMMANDS

def _load_auth():
    global BASE
    global USER
    if not isfile(AUTH_FILE):
        return False
    try:
        rc_file = file(AUTH_FILE)
        data = json.load(rc_file)
        rc_file.close()
        BASE = data["base"]
        USER = data["user"]
        return True
    except (ValueError, KeyError):
        return False

def _load_prj_config():
    global CONFIG
    try:
        with open(PROJECT_FILE, 'r') as prj_file:
            CONFIG = json.load(prj_file)
    except (ValueError, IOError):
        CONFIG = {}

@click.group()
@click.pass_context
def cli(ctx):
    _load_prj_config()
    if _command_need_auth(ctx.invoked_subcommand):
        if not _load_auth():
            click.echo('please, use `coke login` first!')
            ctx.abort()
    if _command_need_config(ctx.invoked_subcommand) and not len(CONFIG):
        click.echo('You need create project.json first!')
        click.echo('You can try `init` to do that.')
        ctx.abort()


headers = {'content-type': 'application/json'}
    
@cli.command()
@click.option('--url', default='http://localhost:5555')
@click.option('--user', default=getpass.getuser())
def login(url, user):
    rc_file = file(AUTH_FILE, "w")
    os.chmod(AUTH_FILE, 0600)
    json.dump({
        "base": url,
        "user": user
    }, rc_file, indent=2)
    rc_file.close()


@cli.command()
@click.option('--name', prompt="Project title", default=CONFIG.get("name"))
def init(name):
    CONFIG["name"] = name

    ## fill members as previous value or empty object
    CONFIG["members"] = CONFIG.get("members", {})

    while click.confirm("Add user to config?", default=False, abort=False, show_default=True):
        u_name = click.prompt("User name", default=USER or getpass.getuser(), show_default=True)
        u_roles = click.prompt("User roles", default="admin, developer", show_default=True)
        CONFIG["members"][u_name] = u_roles.replace(" ", "").split(",")
    else:
        if not len(CONFIG["members"]):
            CONFIG["members"][USER or getpass.getuser()] = ("admin", "developer")

    CONFIG["clusters"] = CONFIG.get("clusters", {})

    while click.confirm("Add cluster?", default=False, abort=False, show_default=True):
        c_name = click.prompt("Cluster name")
        c_url = click.prompt("Project url")
        c_board = click.prompt("Kibana dashboard")
        c_query = click.prompt("Kibana search query")
        CONFIG["clusters"][c_name] = {
            "url": c_url,
            "logging": {
                "dashboard": c_board,
                "search_query": c_query
            }
        }

    click.echo(json.dumps(CONFIG, indent=2))
    click.confirm("All right?", default=True, show_default=True)
    prj_file = file(PROJECT_FILE, "w")
    json.dump(CONFIG, prj_file, indent=2)
    prj_file.close()

@cli.command()
@click.option('--force', '-f', is_flag=True,
              help="force an update of the existing project")
def create(force, **kwargs):
    params={"force":force}

    project_def  = ProjectReader.read(CONFIG)
    r = requests.post(BASE+"/create/",
                      headers=headers,
                      params=params,
                      data=json.dumps(project_def, indent=2))
    print r.text


def handle_streaming_response(r):
    print "response", r
    print "headers", r.headers
    for ch in r.iter_lines(chunk_size=1):
        logging.debug("got chunk %s"%ch)
        r = json.loads(ch)
        if "error" in r and  r["error"]:
            print r["traceback"]
        else:
            if "b64" in r and r["b64"]:
                m = r["message"].decode("base64")
            else:
                m = r["message"]
            print m
    

@cli.command()
@click.option('--force', '-f', is_flag=True,
              help="force an update of the existing version")
@click.option('--no-build', '-n', is_flag=True,
              help="don't schedule build of a container")
@click.option('--async', is_flag=True,
              help="run task in async mode")
def push(force, no_build, **kwargs):

    version_def  = VersionReader.read(CONFIG)

    params={"force":force,
            "no-build":no_build,
            "sync": True}

    r = requests.post(BASE+"/push/",
                      headers=headers,
                      params=params,
                      data=json.dumps(version_def, indent=2),
                      stream=True)
    handle_streaming_response(r)

@cli.command()
@click.argument("task-id")
def status(task_id):
    "<task-id> prints status of the task"
    r = requests.get(BASE+"/status/%s/"%task_id)
    print r.text

@cli.command()
@click.argument('target')
def deploy(target, **kwargs):
    "deploy version to TARGET cluster"

    r = requests.post(BASE+"/deploy/%s/"%target,
                      data = json.dumps(CONFIG, indent=2),
                      params = { "sync": True },
                      stream = True)

    handle_streaming_response(r)
    # print r.text

@cli.command()
@click.argument('target')
def balance(target, **kwargs):
    "balance project load to versions on TARGET cluster"

    r = requests.post(BASE+"/balance/%s/"%target,
                      data = json.dumps(CONFIG, indent=2),
                      params = { "sync": True },
                      stream = True)

    handle_streaming_response(r)
    # print r.text


@cli.command()
def tasks():
    r = requests.get(BASE+"/tasks/")
    print r.text

        
@cli.command()
def reschedule():
    r = requests.post(BASE+"/reschedule/")
    print r.text


@cli.command()
def show():
    "show project status"

    project_id = CONFIG['name']

    r = requests.get(BASE+"/project/%s/"%project_id)
    print r.text


if __name__ == "__main__":
    cli()
