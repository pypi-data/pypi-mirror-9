"""
Deployapp -w


For websites, it can deploy

A simple module that allows you to deploy site and run application in a virtualenv (for python)

It runs pre_scripts and post_scripts deployment

For website, it can deploy Python and PHP/HTML site by create the settings and config files necessary

For application it just execute the scripts

DeploySite uses Gunicorn/Supervisort/Gevent/Nginx to launch Python app
FOr PHP or HTML site, Apache/Nginx

For Python site, it uses Nginx as a proxy

Features:
    - Deploy Python/PHP/HTML site
    -

A simple module to deploy flask/Python, PHP/HTML sites


Virtualenv

** TESTED ON CENTOS AND WITH PYTHON 2.7

@Author: Mardix
@Copyright: 2015 Mardix
LICENSE: MIT

https://github.com/mardix/deploysite

Requirements:
    Nginx
    Gunicorn
    Supervisor
    Gevent
    Virtualenvwrapper
"""

import os
import datetime
import subprocess
import multiprocessing
import socket
import random
import argparse
import shutil
try:
    import yaml
except ImportError as ex:
    print("PyYaml is missing. pip --install pyyaml")
try:
    from jinja2 import Template
except ImportError as ex:
    print("Jinja2 is missing. pip --install jinja2")

__version__ = "0.7.0"
__author__ = "Mardix"
__license__ = "MIT"
__NAME__ = "Deployapp"

CWD = os.getcwd()
CONFIG_FILE = "deploy.yml"
NGINX_DEFAULT_PORT = 80
GUNICORN_PORT_RANGE = [8000, 9000]  # Port range for gunicorn proxy
GUNICORN_DEFAULT_MAX_REQUESTS = 500
GUNICORN_DEFAULT_WORKER_CLASS = "gevent"

VIRTUALENV = None
VERBOSE = False
VIRTUALENV_DIRECTORY = "/root/.virtualenvs"
VIRTUALENV_DEFAULT_PACKAGES = ["gunicorn", "gevent"]
LOCAL_BIN = "/usr/local/bin"

DEPLOY_CONFIG = None
# ------------------------------------------------------------------------------
# TEMPLATES

# SUPERVISOR
SUPERVISOR_CTL = "/usr/local/bin/supervisorctl"
SUPERVISOR_LOG_PATH = "/var/log/supervisor/%s.log"
SUPERVISOR_CONF_PATH = "/etc/supervisor/%s.conf"
SUPERVISOR_TPL = """
[program:{name}]
command={command}
directory={directory}
user={user}
autostart=true
autorestart=true
stopwaitsecs=600
startsecs=10
stdout_logfile={log}
stderr_logfile={log}
environment={environment}
"""

# CONF FILE
NGINX_CONF_FILE_PATTERN = "/etc/nginx/conf.d/%s.conf"

NGINX_CONFIG = """
server {

    listen {{ PORT }};
    server_name {{ SERVER_NAME }};
    root {{ DIRECTORY }};
    access_log {{ LOGS_DIR }}/access_{{ SERVER_NAME }}.log;
    error_log {{ LOGS_DIR }}/error_{{ SERVER_NAME }}.log;
    
{%- if SSL_CERT and SSL_KEY %}
    if ($scheme = "http") {
        return 301 https://{{ SERVER_NAME }}$request_uri;
    }

    listen 443 ssl;
    ssl_certificate {{ DIRECTORY }}/{{ CERT }};
    ssl_certificate_key {{ DIRECTORY }}/{{ KEY }};

    ssl_session_cache shared:SSL:1m;
    ssl_session_timeout  5m;
    ssl_ciphers  HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers   on;
{% endif -%}

{% if PROXY_PORT %}
    location / {
        proxy_pass http://127.0.0.1:{{ PROXY_PORT }}/;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }

{% else %}

    location / {
        index index.html index.htm index.php;
    }

    # Pass PHP scripts to PHP-FPM
    location ~* \.php$ {
        fastcgi_index   index.php;
        fastcgi_pass    127.0.0.1:9000;
        include         fastcgi_params;
        fastcgi_param   SCRIPT_FILENAME    $document_root$fastcgi_script_name;
        fastcgi_param   SCRIPT_NAME        $fastcgi_script_name;
    }
    
{% endif %}

{%- if ALIASES %}
    {%- for alias, location in ALIASES.items() %}
    location {{ alias }} {
        alias {{ location }};
    }
    {% endfor -%}
{% endif -%}

    {{ SERVER_DIRECTIVES }}

}

{% if not ALLOW_WWW %}
# www to non-www for both http and https
server {
    listen {{ PORT }};
    listen 443;
    server_name www.{{ SERVER_NAME }};
    return 301 $scheme://{{ SERVER_NAME }}$request_uri;
}
{% endif %}

"""

POST_RECEIVE_HOOK_CONFIG = """
#!/bin/sh
while read oldrev newrev refname
do
    branch=$(git rev-parse --symbolic --abbrev-ref $refname)
    if [ "master" == "$branch" ]; then
        GIT_WORK_TREE={{ WORKING_DIR }} git checkout -f
        cd {{ WORKING_DIR }}
        {% if SET_DEPLOY_ON_PUSH %}
            deployapp -w
        {% endif %}
    fi
done
"""

# ------------------------------------------------------------------------------

def run(cmd, verbose=True):
    """ Shortcut to subprocess.call """
    if verbose and VERBOSE:
        subprocess.call(cmd.strip(), shell=True)
    else:
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process.communicate()[0]

def runvenv(command, virtualenv=None):
    """
    run with virtualenv with the help of .bashrc
    :params command:
    :params  virtualenv: The venv name
    """
    kwargs = dict()
    if not VERBOSE:
        kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if virtualenv:
        command = "workon %s; %s; deactivate" % (virtualenv, command)
    cmd = ["/bin/bash", "-i", "-c", command]
    process = subprocess.Popen(cmd, **kwargs)
    return process.communicate()[0]

def get_venv_bin(bin_program=None, virtualenv=None):
    """
    Get the bin path of a virtualenv program
    """
    bin = (VIRTUALENV_DIRECTORY + "/%s/bin") % virtualenv if virtualenv else LOCAL_BIN
    return (bin + "/%s") % bin_program if bin_program else bin 

def _print(text):
    """
    Verbose print. Will print only if VERBOSE is ON
    """
    if VERBOSE:
        print(text)

def is_port_open(port, host="127.0.0.1"):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        s.shutdown(2)
        return True
    except Exception as e:
        return False

def generate_random_port():
    while True:
        port = random.randrange(GUNICORN_PORT_RANGE[0], GUNICORN_PORT_RANGE[1])
        if not is_port_open(port):
            return port

def nginx_reload():
    run("service nginx reload")

def nginx_restart():
    run("service nginx stop")
    run("service nginx start")

# VirtualenvWrapper
def virtualenv_make(name):
    runvenv("mkvirtualenv %s" % name)
    pip = get_venv_bin(bin_program="pip", virtualenv=name)
    packages = " ".join([p for p in VIRTUALENV_DEFAULT_PACKAGES])
    runvenv("%s install %s" % (pip, packages), virtualenv=name)

def virtualenv_remove(name):
    runvenv("rmvirtualenv %s" % name)

# Deployment
def get_deploy_config(directory):
    """
    Return dict of the yaml file
    :params directory:
    """
    global DEPLOY_CONFIG

    if not DEPLOY_CONFIG:
        yaml_file = directory + DEPLOY_CONFIG
        if not os.path.isfile(yaml_file):
            raise Exception("Deploy file '%s' is required" % yaml_file)
        with open(yaml_file) as jfile:
            DEPLOY_CONFIG = yaml.load(jfile)
    return DEPLOY_CONFIG

def _parse_command(command, virtualenv=None):
    command = command.replace("$VENV_PY", get_venv_bin(bin_program="python", virtualenv=virtualenv))
    command = command.replace("$VENV_BIN", get_venv_bin(virtualenv=virtualenv))
    return command

def reload_server():
    nginx_reload()
    Supervisor.reload()

# Supervisor
class Supervisor(object):
    """
    Supervisor Class
    """

    @classmethod
    def ctl(cls, action, name):
        return run("%s %s %s" % (SUPERVISOR_CTL, action, name))

    @classmethod
    def status(cls, name):
        status = run("%s %s %s" % (SUPERVISOR_CTL, "status", name), verbose=False)
        if status:
            _status = ' '.join(status.split()).split(" ")
            if _status[0] == name:
                return _status[1]
        return None

    @classmethod
    def start(cls, name, command, directory="/", user="root", environment=None):
        """
        To Start/Set  a program with supervisor
        :params name: The name of the program
        :param command: The full command
        :param directory: The directory
        :param user:
        :param environment:
        """
        log_file = SUPERVISOR_LOG_PATH % name
        conf_file = SUPERVISOR_CONF_PATH % name
        if cls.status(name) == "RUNNING":
            cls.ctl("stop", name)
        with open(conf_file, "wb") as f:
            f.write(SUPERVISOR_TPL.format(name=name,
                                          command=command,
                                          log=log_file,
                                          directory=directory,
                                          user=user,
                                          environment=environment or ""))
        cls.reload()
        cls.ctl("start", name)

    @classmethod
    def stop(cls, name, remove=True):
        """
        To Stop/Remove a program
        :params name: The name of the program
        :remove: If True will also delete the conf file
        """
        conf_file = SUPERVISOR_CONF_PATH % name
        cls.ctl("stop", name)
        if remove:
            if os.path.isfile(conf_file):
                os.remove(conf_file)
            cls.ctl("remove", name)
        cls.reload()

    @classmethod
    def reload(cls):
        """
        Reload supervisor with the changes
        """
        cls.ctl("reread", "")
        cls.ctl("update", "")

class Git(object):
    def __init__(self, directory):
        self.directory = directory

    def get_working_dir(self, repo):
        working_dir = "%s/%s" % (self.directory, repo)
        bare_repo = "%s.git" % working_dir
        return working_dir, bare_repo

    def init_bare_repo(self, repo):
        working_dir, bare_repo = self.get_working_dir(repo)
        logs_dir = "%s.logs" % working_dir

        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)
        if not os.path.isdir(working_dir):
            os.makedirs(working_dir)
        if not os.path.isdir(bare_repo):
            os.makedirs(bare_repo)
            run("cd %s && git init --bare" % bare_repo)
            return True
        return False

    def update_post_receive_hook(self, repo, self_deploy=False):
        working_dir, bare_repo = self.get_working_dir(repo)
        post_receice_hook_file = "%s/hooks/post-receive" % bare_repo

        # Always make a backup of the post receive hook
        if os.path.isfile(post_receice_hook_file):
            ts = datetime.datetime.now().strftime("%s")
            backup_file = (post_receice_hook_file + "-bk-%s") % ts
            shutil.copyfile(post_receice_hook_file, backup_file)

        with open(post_receice_hook_file, "wb") as f:
            content = Template(POST_RECEIVE_HOOK_CONFIG)\
                .render(WORKING_DIR=working_dir, SELF_DEPLOY_ON_PUSH=self_deploy)
            f.write(content)
        run("chmod +x %s " % post_receice_hook_file)


class App(object):
    virtualenv = None
    directory = None

    def __init__(self, directory):
        self.config = get_deploy_config(directory)
        self.directory = directory
        self.nginx_conf = Template(NGINX_CONFIG)

    def get_virtualenv(self, key):
        conf = {
            "name": None,
            "directory": None,
            "rebuild": False
        }
        if "virtualenv" in self.config:
            conf.update(self.config["virtualenv"])
        return conf.get(key, default=None)

    def deploy_web(self):
        if "webs" in self.config:
            for site in self.config["web"]:
                if "name" not in site:
                    raise TypeError("'name' is missing in sites config")
                if "server_name" not in site:
                    raise TypeError("'server_name' is missing in sites config")
                if "application" in site and not self.get_virtualenv("name"):
                    raise TypeError("'virtualenv' in required to deploy Python application")

                name = site["name"]
                server_name = site["server_name"]
                directory = site["directory"] if "directory" in site else self.directory
                ssl = site["ssl"] if "ssl" in site else {}
                nginx = site["nginx"] if "nginx" in site else {}
                nginx_aliases = nginx["aliases"] if "aliases" in nginx else {}
                remove = True if "remove" in site and site["remove"] is True else False
                allow_www = False if "allow_www" in nginx and nginx["allow_www"] is False else True
                port = nginx["port"] if "port" in nginx else NGINX_DEFAULT_PORT
                server_directives = nginx["server_directives"] if "server_directives" in nginx else ""
                application = site["application"] if "application" in site else None
                gunicorn_app_name = "gunicorn_%s" % (server_name.replace(".", "_"))
                gunicorn_option = site["gunicorn"] if "gunicorn" in site else {}
                proxy_port = None

                # Config file
                nginx_config_file = NGINX_CONF_FILE_PATTERN % name

                if remove and os.path.isfile(nginx_config_file):
                    os.remove(nginx_config_file)
                    if "application" in site:
                        Supervisor.stop(name=gunicorn_app_name, remove=True)

                logs_dir = "%s.logs" % directory
                if not os.path.isdir(logs_dir):
                    os.makedirs(logs_dir)

                # PYTHON app.
                if application:
                    proxy_port = generate_random_port()
                    default_gunicorn = {
                        "workers": (multiprocessing.cpu_count() * 2) + 1,
                        "threads": 4,
                        "max-requests": GUNICORN_DEFAULT_MAX_REQUESTS,
                        "worker-class": GUNICORN_DEFAULT_WORKER_CLASS
                    }
                    gunicorn_option.update(default_gunicorn)

                    settings = " ".join(["--%s %s" % (x[0], x[1]) for x in gunicorn_option.items()])
                    gunicorn_bin = get_venv_bin(bin_program="gunicorn", virtualenv=self.get_virtualenv("name"))
                    command = "{GUNICORN_BIN} -b 0.0.0.0:{PROXY_PORT} {APP} {SETTINGS}"\
                              .format(GUNICORN_BIN=gunicorn_bin, PROXY_PORT=proxy_port,
                                      APP=application, SETTINGS=settings,)

                    Supervisor.start(name=gunicorn_app_name,
                                     command=command,
                                     directory=directory)

                with open(nginx_config_file, "wb") as f:
                    context = dict(NAME=name,
                                   SERVER_NAME=server_name,
                                   PORT=port or NGINX_DEFAULT_PORT,
                                   DIRECTORY=directory,
                                   LOGS_DIR=logs_dir,
                                   SSL_CERT=ssl.get("CERT", None),
                                   SSL_KEY=ssl.get("KEY", None),
                                   ALIASES=nginx_aliases,
                                   ALLOW_WWW=allow_www,
                                   SERVER_DIRECTIVES=server_directives,
                                   PROXY_PORT=proxy_port)
                    content = self.nginx_conf.render(**context)
                    f.write(content)
        else:
            raise TypeError("'webs' is missing in deploy.yml")

    def run_scripts(self, script_type=""):
        script_key = "scripts%s" % script_type
        if script_key in self.config:
            for script in self.config[script_key]:
                if "command" not in script:
                    raise TypeError("'command' is missing in scripts")
                directory = script["directory"] if "directory" in script else self.directory
                command = _parse_command(command=script["command"], virtualenv=self.get_virtualenv("name"))
                runvenv("cd %s; %s" % (directory, command), virtualenv=self.get_virtualenv("name"))

    def run_workers(self):
        if "workers" in self.config:
            for worker in self.config:
                if "name" not in worker:
                    raise TypeError("'name' is missing in workers")
                if "command" not in worker:
                    raise TypeError("'command' is missing in workers")

                name = worker["name"]
                user = worker["user"] if "user" in worker else "root"
                directory = worker["directory"] if "directory" in worker else self.directory
                command = _parse_command(command=worker["command"], virtualenv=self.get_virtualenv("name"))
                remove = True if "remove" in worker and worker["remove"] is True else False

                if remove:
                    Supervisor.stop(name=name, remove=True)
                else:
                    Supervisor.start(name=name,
                                     command=command,
                                     directory=directory,
                                     user=user)

    def install_requirements(self):
        requirements_file = self.directory + "/requirements.txt"
        if os.path.isfile(requirements_file):
            pip = get_venv_bin(bin_program="pip", virtualenv=self.get_virtualenv("name"))
            runvenv("%s install -r %s" % (pip, requirements_file), virtualenv=self.get_virtualenv("name"))

    def setup_virtualenv(self):
        if self.get_virtualenv("name"):
            if self.get_virtualenv("rebuild"):
                virtualenv_remove(self.get_virtualenv("name"))
            virtualenv_make(self.get_virtualenv("name"))

def cmd():
    try:
        global VIRTUALENV_DIRECTORY
        global VERBOSE

        parser = argparse.ArgumentParser(description="%s %s" % (__NAME__, __version__))
        parser.add_argument("-w", "--websites", help="Deploy all sites", action="store_true")
        parser.add_argument("--scripts", help="Execute Pre/Post scripts", action="store_true")
        parser.add_argument("--workers", help="Run Workers", action="store_true")
        parser.add_argument("--reload-server", help="To reload the servers", action="store_true")
        parser.add_argument("-r", "--repo", help="The repo name [-r www --git-init --self-deploy]")
        parser.add_argument("--git-init", help="To setup git bare repo name in "
                                                 "the current directory to push "
                                                 "to [ie: -r www --git-init]", action="store_true")
        parser.add_argument("--git-push-deploy", help="On git push, to deploy instantly. set to 0 or N to disallow "
                                                      "[-r www --git-push-deploy Y|N]")
        parser.add_argument("--non-verbose", help="Verbose", action="store_true")

        arg = parser.parse_args()
        VERBOSE = False if arg.non_verbose else True

        _print("*" * 80)
        _print("%s %s" % (__NAME__, __version__))
        _print("")

        # The repo name to perform git stuff on
        repo = arg.repo or None

        app = App(CWD)
        git = Git(CWD)

        # Automatically setup environment and install requirement
        if arg.websites or arg.scripts or arg.workers:
            if app.get_virtualenv("name"):
                _print("> SETUP VIRTUALENV: %s " % app.get_virtualenv("name"))
                app.setup_virtualenv()
                if app.get_virtualenv("directory"):
                    VIRTUALENV_DIRECTORY = app.get_virtualenv("directory")
            _print("> Install requirements")
            app.install_requirements()
            _print("Done!\n")

        if arg.websites:
            try:
                _print(":: DEPLOY WEBSITES ::")

                _print("> Running PRE-SCRIPTS ...")
                app.run_scripts("_pre_web")

                _print("> Deploying WEB ... ")
                app.deploy_web()

                _print("> Running POST-SCRIPTS ...")
                app.run_scripts("_post_web")

                _print("")

            except Exception as ex:
                _print("Error WEB: %s" % ex.__repr__())
            _print("Done!\n")

        if arg.scripts:
            try:
                _print("> Running SCRIPTS ...")
                app.run_scripts()
            except Exception as ex:
                _print("Error SCRIPTS: %s" % ex.__repr__())

        if arg.workers:
            try:
                _print("> Running WORKERS...")
                app.run_workers()
            except Exception as ex:
                _print("Error WORKERS: %s" % ex.__repr__())

        # Setup new repo
        if arg.git_init:
            _print("> Create Git Bare repo ...")
            if not repo:
                raise TypeError("Missing 'repo' name")

            bare_repo = "%s/%s.git" % (CWD, repo)
            _print("Repo: %s" % bare_repo)

            if git.init_bare_repo(repo):
                git.update_post_receive_hook(repo, False)
            _print("Done!\n")

        # Git push deploy
        if arg.git_push_deploy:
            _print("> Git Push Deploy ...")
            if not repo:
                raise TypeError("Missing 'repo' name")

            deploy = True if arg.git_push_deploy in [True, 1, "1", "y", "Y"] else False
            git.update_post_receive_hook(repo, deploy)
            _print("Done!\n")

        # Reload server
        if arg.reload_server:
            _print("> Reloading server ...")
            reload_server()
            _print("Done!\n")

    except Exception as ex:
        _print("ERROR: %s " % ex.__repr__())


