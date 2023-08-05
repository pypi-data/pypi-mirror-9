import json
import click
import getpass
from os.path import expanduser, join, isfile
import os
import re

from pprint import pprint

import requests

from config_reader import ProjectReader, VersionReader

from cocaine.cli.util import make_archive

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

API_VERSION = (0, 0, 3)

def _command_need_auth(cmd):
    return not cmd in NO_AUTH_COMMANDS

def _command_need_config(cmd):
    return not cmd in NO_CONFIG_COMMANDS

def _load_auth(ctx):
    global BASE
    global USER
    if not isfile(AUTH_FILE):
        return False
    try:
        rc_file = file(AUTH_FILE)
        data = json.load(rc_file)
        rc_file.close()
        if (re.search(r'^https?://[^:/]+(?::\d+)$', data["base"])):
            BASE = data["base"]
        else:
            click.echo('Base url broken. Please, use cocaine login with correct arguments (url ex. http://some.host:1234)')
            ctx.abort()
        USER = data["user"]
        return True
    except (ValueError, KeyError):
        click.echo('Please, use `coke login` first!')
        ctx.abort()

def _load_project_config(path):
    global CONFIG
    try:
        with open(path, 'r') as prj_file:
            CONFIG = json.load(prj_file)
    except (ValueError, IOError):
        CONFIG = {}

def _check_api_version(ctx):
    r = requests.get(BASE+"/version/")
    if (r.status_code >= 400):
        ctx.abort("Can't check API version")
    parsed_api_version = r.text.split(".")
    for level in xrange(3): # TODO use xrange(2) after 0.1 version
        if (int(parsed_api_version[level]) < API_VERSION[level]):
            ctx.abort('You need update client version!')

@click.group()
@click.pass_context
def cli(ctx):
    _load_project_config(PROJECT_FILE)
    if _command_need_auth(ctx.invoked_subcommand):
        if _load_auth(ctx):
            _check_api_version(ctx)
    if _command_need_config(ctx.invoked_subcommand) and not len(CONFIG):
        click.echo('You need create project.json first!')
        click.echo('You can try `init` to do that.')
        ctx.abort()


headers = {'content-type': 'application/json'}
    
@cli.command()
@click.option('--url', default='http://localhost:5555')
@click.option('--user', default=getpass.getuser())
def login(url, user):
    if not re.search(r'^https?://[^:/]+(?::\d+)$', url):
        click.echo('Url broken. Please, use cocaine login with correct arguments (url ex. http://some.host:1234)')
        pass
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

    print "creating project:"
    pprint(project_def)
    
    r = requests.post(BASE+"/create/",
                      headers=headers,
                      params=params,
                      data=json.dumps(project_def, indent=2))
    handle_streaming_response(r)


def handle_streaming_response(r):
    print "response", r
    print "headers", r.headers
    for ch in r.iter_lines(chunk_size=1):
        logging.debug("got chunk %s"%ch)
        try:
            r = json.loads(ch)
            if "error" in r and  r["error"]:
                print r["traceback"]
            else:
                if "b64" in r and r["b64"]:
                    m = r["message"].decode("base64")
                else:
                    m = r["message"]
                print m
        except Exception:
            print ch

@cli.command()
@click.option('--force', '-f', is_flag=True,
              help="force an update of the existing version")
@click.option('--no-build', '-n', is_flag=True,
              help="don't schedule build of a container")
@click.option('--archive', '-a', is_flag=True,
              help="use archive as a source of the application")
@click.option('--increment', '-i', is_flag=True,
              help="increment version")
@click.option('--version', '-v', help="set version")
def push(force, no_build, archive, increment, version, **kwargs):
    new_version = version
    old_version = CONFIG["version"]
    if increment and version:
        click.echo("options -i and -v are mutually exclusive")
        pass
    elif increment:
        cocs_suffix = re.search(r'-cocaine-(\d+)?$', old_version)

        if cocs_suffix:
            try:
                new_version_patch = str(int(cocs_suffix.group(1)) + 1)
            except ValueError:
                click.echo("Please update version in project.json manually")
                pass
            new_version = re.sub(r'\d+$', new_version_patch, old_version)
        else:
            new_version = old_version + "-cocaine-1"

    if new_version:
        CONFIG["version"] = new_version
        with open(PROJECT_FILE, "r") as prj_file:
            config_str = prj_file.read()
        with open(PROJECT_FILE, "w") as prj_file:
            new_config = re.sub('(?P<before>["\']version["\']:\s+["\']?)%s' % old_version, '\g<before>%s' % new_version, config_str)
            prj_file.write(new_config)
        logging.info("incrementing version from %s to %s" % (old_version, new_version))

    params={"force":force,
            "no-build":no_build,
            "sync": True}

    if not archive:
        version_def  = VersionReader.read(CONFIG)

        r = requests.post(BASE+"/push/",
                          headers=headers,
                          params=params,
                          data=json.dumps(version_def, indent=2),
                          stream=True)
        handle_streaming_response(r)

    else:
        version_def = VersionReader.read(CONFIG)
        key = "%(name)s_%(version)s"%(version_def)
        version_def["container"] = {
            "source":{
                "namespace": "app-archive",
                "key": key,
                "tags": ("APP_ARCHIVE",),
                "type": "archive"
            }
        }

        print "creating archive"

        tarball = make_archive(".")

        print "uploading archive"

        r = requests.post(BASE+"/app-archive",
                          data={"archive":tarball,
                                "key": key})

        print r.text

        print "upload done"

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
@click.option('-u', is_flag=True,
              help="undeploy version from cluster")
@click.argument('target')
def deploy(target, u, **kwargs):
    "deploy version to TARGET cluster"

    event = "deploy"

    if u:
        event = "undeploy"

    r = requests.post(BASE+"/%s/%s/"%(event,target),
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
@click.argument('target')
def restart(target, **kwargs):
    "restart version on TARGET cluster"

    r = requests.post(BASE+"/restart/%s/"%target,
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
