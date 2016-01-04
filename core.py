import json
import os
import re
import random
import shutil
import string
import subprocess
import urllib
import urllib.request
import urllib.parse

from os.path import dirname

# Do not "import sublime"
# Only business logic here.

# API

API_HOST = 'http://localhost:8001/api'
API_CONF = '/conf/'
API_COUNTRY = '/country/'
API_DB = '/db/'
API_INSTALL = '/install/'
API_IP = '/ip/'
API_PROJECT = '/project/'
API_PROVIDER = '/provider/'
API_SERVER = '/server/'
API_USER = '/user/'

API_PROJECTS_BY_TYPE = '/project-list/'
API_PROJECT_BY_NAME = '/project-by-name/'

API_LOCAL_LINUX_USERNAME = '/local-linux-username/'
API_LOCAL_BASH_DIR = '/local-bash-dir/'
API_CONFIRMATION_PASSWORD = '/confirmation-password/'
API_SERVER_CONTROL_SCRIPT = '/server-control-script/'

CONTROL_SERVER_LOGFILE = '/var/log/servercontrol/control.log'


class Core:
    def run_command_in_terminal(self, cmd, wait=True):
        """Runs command in gnome terminal. It's for long commands"""

        if wait is True:
            cmd += ' && echo Press Enter && read'
        tcmd = "gnome-terminal -e \"bash -c '{}'\" ".format(cmd)
        print(tcmd)
        subprocess.call(tcmd, shell=True)

    def run_command_in_subprocess(self, cmd):
        """Run command and returns boolean. It's for short commands."""
        try:
            subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            # if exit code non zero
            print(e)
            return False
        return True

    def run_command_in_subprocess_get_output(self, cmd):
        """Run command and returns output."""
        try:
            output = subprocess.check_output(
                cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = str(e)
        return output

    def format_dic_to_message(self, dic):
        message = ''
        for k, v in sorted(dic.items()):
            message += '{}: {}\n'.format(k, v)
        return message

    def send_request(self, url):
        bytes = urllib.request.urlopen(url).read()
        return bytes.decode()

    def get_projects(self, proj_type):
        """Returns list of projects by type with full info"""
        url = API_HOST + API_PROJECTS_BY_TYPE + proj_type + '/'
        l = self.send_request(url)
        return json.loads(l)

    def get_servers(self):
        """Returns list of servers"""
        url = API_HOST + API_SERVER
        l = self.send_request(url)
        return json.loads(l)

    def get_databases(self):
        """Returns list of databases"""
        url = API_HOST + API_DB
        l = self.send_request(url)
        return json.loads(l)

    def get_server_by_id(self, id):
        """Returns dictionary with nested info"""
        url = API_HOST + API_SERVER + str(id) + '/'
        dic = self.send_request(url)
        return json.loads(dic)

    def get_localhost(self):
        """Returns localhost dictionary"""
        servers = self.get_servers()
        for d in servers:
            if d['code'] == 'localhost':
                return d
        raise Exception('Can\t find server with code "localhost"')

    def get_project_by_id(self, id):
        """Returns dictionary with nested info"""
        url = API_HOST + API_PROJECT + str(id) + '/'
        dic = self.send_request(url)
        return json.loads(dic)

    def get_project_by_name(self, name):
        """Returns dictionary with nested info"""
        url = API_HOST + API_PROJECT_BY_NAME + name + '/'
        dic = self.send_request(url)
        return json.loads(dic)

    def get_server_control_script(self):
        """Returns path to server control script"""
        url = API_HOST + API_SERVER_CONTROL_SCRIPT
        res = self.send_request(url)
        dic = json.loads(res)
        return dic['value']

    def get_database_by_id(self, id):
        """Returns dictionary with nested info"""
        url = API_HOST + API_DB + str(id) + '/'
        dic = self.send_request(url)
        return json.loads(dic)

    def get_database_by_server_id_and_type_db(self, server_id, type_db):
        """Server can have only one database of particular type"""
        dbs = self.get_databases()
        for d in dbs:
            if d['server'] == server_id and d['type_db'] == type_db:
                return self.get_database_by_id(d['id'])
        raise Exception('Can\'t get database.')

    def is_database_exists_on_localhost(self, db_id):
        db = self.get_database_by_id(db_id)
        if db['type_db'] == 'M':
            return self.is_mysql_database_exists_on_localhost(db_id)

    def is_mysql_database_exists_on_localhost(self, db_id):
        db = self.get_database_by_id(db_id)
        localhost = self.get_localhost()
        localhost_db = self.get_database_by_server_id_and_type_db(
            localhost['id'], 'M')

        cmd = 'mysql -u root -p{0} -e "use {1}"'.format(
            localhost_db['user']['root'], db['name'])
        res = self.run_command_in_subprocess(cmd)
        return res

    def get_local_linux_username(self):
        """Returns local linux user that deals with remote servers"""
        url = API_HOST + API_LOCAL_LINUX_USERNAME
        res = self.send_request(url)
        dic = json.loads(res)
        return dic['value']

    def get_local_bash_dir(self):
        """Returns local linux bash scripts directory"""
        url = API_HOST + API_LOCAL_BASH_DIR
        res = self.send_request(url)
        dic = json.loads(res)
        return dic['value']

    def get_confirmation_password(self):
        """Returns confirmation password for important operations"""
        url = API_HOST + API_CONFIRMATION_PASSWORD
        res = self.send_request(url)
        dic = json.loads(res)
        return dic['value']

    def copy_control_to_server(self, server_id):
        server = self.get_server_by_id(server_id)
        username = self.get_local_linux_username()

        cmd = 'ssh {}@{} mkdir -p {} && '.format(
            username,
            server['main_ip'],
            server['control_dir']
        )

        cmd += 'scp '

        cmd += self.get_server_control_script()
        cmd += ' {}@{}:{}'.format(
            username, server['main_ip'], server['control_dir'])
        self.run_command_in_terminal(cmd)

    def view_control_script_logs(self, server_id):
        server = self.get_server_by_id(server_id)

        cmd = 'ssh root@{} cat {}'.format(
            server['main_ip'],
            CONTROL_SERVER_LOGFILE,
        )
        return self.run_command_in_subprocess_get_output(cmd)

    def clear_control_script_logs(self, server_id):
        server = self.get_server_by_id(server_id)

        cmd = 'ssh root@{} \'echo "" > {}\''.format(
            server['main_ip'],
            CONTROL_SERVER_LOGFILE,
        )
        return self.run_command_in_subprocess(cmd)

    def download_database(self, db_id):
        """Downloads database from remote host.

        Downloads database and creates on localhost database and user
        with same password. Removes database on localhost if it exists
        before creating.
        """

        db = self.get_database_by_id(db_id)
        if db['type_db'] == 'M':
            return self.download_mysql_database(db_id)

    def download_mysql_database(self, db_id):
        db = self.get_database_by_id(db_id)
        localhost = self.get_localhost()
        localhost_db = self.get_database_by_server_id_and_type_db(
            localhost['id'], 'M')

        dic = {
            'dbname': db['name'],
            'username': db['user']['name'],
            'password': db['user']['password'],
            'root_db_password': localhost_db['user']['root'],
            'server_ip': db['server_ip']
        }

        sql = """
            DROP DATABASE IF EXISTS \`{dbname}\`;
            GRANT USAGE ON *.* TO \`{username}\`;
            DROP USER \`{username}\`;
            CREATE DATABASE \`{dbname}\` character set utf8 collate
             utf8_general_ci;
            GRANT ALL PRIVILEGES on \`{dbname}\`.* to \`{username}\`@localhost
             identified by '{password}' with grant option;
            """.format(**dic)

        sql = re.sub('\s+', ' ', sql).strip()

        cmd = 'mysql -u root -p{0} -e "{1}"'.format(
            dic['root_db_password'], sql)
        self.run_command_in_subprocess(cmd)

        cmd = 'echo Please wait... && '
        # slower: 'mysqldump -u {username} -p{password} -h {server_ip}...'
        # faster: (ssh keys should be installed on local machine)
        cmd += 'ssh root@{server_ip} mysqldump -u {username} '
        cmd += '-p{password} {dbname} | '
        cmd += 'mysql -u root -p{root_db_password} {dbname} && '
        cmd += 'echo Done'
        cmd = cmd.format(**dic)
        self.run_command_in_terminal(cmd)

    def create_database(self, db_id):
        """Creates database on remote server if it doens't exists"""
        db = self.get_database_by_id(db_id)

        if db['type_db'] == 'M':
            return self.create_mysql_database(db_id)

    def create_mysql_database(self, db_id):
        db = self.get_database_by_id(db_id)
        server_id = db['project']['server']['id']
        server_db = self.get_database_by_server_id_and_type_db(server_id, 'M')

        dic = {
            'dbname': db['name'],
            'username': db['user']['name'],
            'password': db['user']['password'],
            'server_ip': db['server_ip'],
            'root_db_password': server_db['user']['root'],  # remote server
        }

        sql = """
            CREATE DATABASE IF NOT EXISTS \`{dbname}\` character set utf8
             collate utf8_general_ci;
            GRANT USAGE ON *.* TO \`{username}\`;
            DROP USER \`{username}\`;
            GRANT ALL PRIVILEGES
             on \`{dbname}\`.* to \`{username}\`@'localhost'
             identified by '{password}' with grant option;
            """.format(**dic)

        if db['remote_access'] is True:
            sql += """
                GRANT ALL PRIVILEGES on \`{dbname}\`.* to \`{username}\`@'%'
                 identified by '{password}' with grant option;
            """.format(**dic)

        sql = re.sub('\s+', ' ', sql).strip()
        cmd = 'mysql -u root -p{root_db_password} -h {server_ip} ' \
            .format(**dic)
        cmd += '-e "{}"'.format(sql)

        res = self.run_command_in_subprocess(cmd)
        return res

    def upload_database(self, db_id):
        """Uploads database to remote host.

        If database exists on remote host it will be destroyed.
        """
        db = self.get_database_by_id(db_id)
        if db['type_db'] == 'M':
            return self.upload_mysql_database(db_id)

    def upload_mysql_database(self, db_id):
        db = self.get_database_by_id(db_id)
        server_id = db['project']['server']['id']
        server_db = self.get_database_by_server_id_and_type_db(server_id, 'M')
        localhost = self.get_localhost()
        localhost_db = self.get_database_by_server_id_and_type_db(
            localhost['id'], 'M')

        dic = {
            'dbname': db['name'],
            'username': db['user']['name'],
            'password': db['user']['password'],
            'server_ip': db['server_ip'],
            'root_db_password': server_db['user']['root'],  # remote server
            'root_db_password_localhost': localhost_db['user']['root']
        }

        # drop database on remote server
        cmd = 'mysql -u root -p{root_db_password} -h {server_ip} '
        cmd += '-e "DROP DATABASE IF EXISTS \`{dbname}\`"'
        cmd = cmd.format(**dic)
        res = self.run_command_in_subprocess(cmd)
        if res is False:
            return False

        # create database and user on remote server
        res = self.create_mysql_database(db_id)
        if res is False:
            return False

        # upload database from localhost to remote server
        cmd = 'echo Please wait... && '
        cmd += 'mysqldump -u root -p{root_db_password_localhost} {dbname} | '
        cmd += 'mysql -u root -p{root_db_password} -h {server_ip} {dbname} && '
        cmd += 'echo Done'
        cmd = cmd.format(**dic)

        res = self.run_command_in_terminal(cmd)
        return res

    def create_venv_localhost(self, project_id):
        project = self.get_project_by_id(project_id)
        s = 'virtualenv {} --python={}'
        s = s.format(project['venv_dir_local'], project['python_path_local'])

        # create virtualenv if directory doesn't exist
        cmd = '[ -d "{}" ] || {};'.format(project['venv_dir_local'], s)

        path = '{project_dir_local}{requirements_dir}development.txt' \
            .format(**project)
        path = os.path.normpath(path)

        cmd += '. {venv_dir_local}bin/activate && '.format(**project)
        cmd += 'pip install -r {}'.format(path)

        self.run_command_in_terminal(cmd)

    def deploy_go_project(self, project_id):
        project = self.get_project_by_id(project_id)
        server = self.get_server_by_id(project['server']['id'])
        username = self.get_local_linux_username()

        cmd = 'ssh {0}@{1} mkdir -p {2}'.format(
            username,
            server['main_ip'],
            project['project_dir_server'],
        )
        self.run_command_in_subprocess(cmd)

        cmd = 'rsync -avzh -e ssh {0}bin/ {1}@{2}:{3}'.format(
            project['project_dir_local'],
            username,
            server['main_ip'],
            project['project_dir_server'],
        )
        self.run_command_in_terminal(cmd)

    def deploy_php_project(self, project_id):
        project = self.get_project_by_id(project_id)
        server = self.get_server_by_id(project['server']['id'])

        cmd = 'rsync -avzh -e ssh {0} php@{1}:{2}'
        cmd = cmd.format(
            project['project_dir_local'],
            server['main_ip'],
            project['project_dir_server'],
        )
        self.run_command_in_terminal(cmd)

    def deploy_html_project(self, project_id):
        project = self.get_project_by_id(project_id)
        server = self.get_server_by_id(project['server']['id'])
        username = self.get_local_linux_username()

        cmd = 'rsync -avzh -e ssh {0} {1}@{2}:{3}'
        cmd = cmd.format(
            project['project_dir_local'],
            username,
            server['main_ip'],
            project['project_dir_server'],
        )
        self.run_command_in_terminal(cmd)

    def download_django_media(self, project_id):
        """Local linux username is the same as django's"""
        project = self.get_project_by_id(project_id)
        server = self.get_server_by_id(project['server']['id'])

        dic = {'username': self.get_local_linux_username()}
        dic['remote_dir'] = project['media_dir_server']
        dic['local_dir'] = project['project_dir_local'] \
            + project['media_dir_local'].lstrip('/')
        dic['ip'] = server['main_ip']

        cmd = 'rsync -avh -e ssh {username}@{ip}:{remote_dir} {local_dir}' \
            .format(**dic)
        self.run_command_in_terminal(cmd)

    def get_files_by_project(self, name, filename):
        """Returns all project files by partial filename"""
        project = self.get_project_by_name(name)
        path = project['project_dir_local']

        sp = []
        for top, dirs, files in os.walk(path):
            for name in files:
                file = os.path.join(top, name)
                if filename in os.path.basename(file):
                    sp.append(file)
        return sp

    def randstring(self, len):
        s = string.ascii_lowercase+string.digits
        return ''.join(random.sample(s, len))

    def remove_pyc_files(self, path):
        for top, dirs, files in os.walk(path):
            for name in files:
                file = os.path.join(top, name)
                if file.endswith('.pyc'):
                    os.remove(file)

    def remove_py_cache(self, path):
        for top, dirs, files in os.walk(path):
            for name in dirs:
                dpath = os.path.join(top, name)
                if dpath.endswith('__pycache__'):
                    shutil.rmtree(dpath, ignore_errors=True)

    def deploy_django_project(self, project_id):
        """Copies files to server excluding media, touchs reload.ini"""
        project = self.get_project_by_id(project_id)
        server = self.get_server_by_id(project['server']['id'])
        username = self.get_local_linux_username()

        self.remove_pyc_files(project['project_dir_local'])
        self.remove_py_cache(project['project_dir_local'])

        # make executables
        for rel_path in project['executables']:
            path = project['project_dir_local'] + rel_path.lstrip('/')
            cmd = 'chmod +x {}'.format(path)
            self.run_command_in_subprocess(cmd)

        cmds = []
        # copy project file excluding media directory
        ex = project['media_dir_local']
        cmd = 'rsync -avzh --exclude {0} -e ssh {1} {2}@{3}:{4}'.format(
            ex,
            project['project_dir_local'],
            username,
            server['main_ip'],
            project['project_dir_server']
        )
        cmds.append(cmd)

        # copy static files excluding media directory if media inside static
        if project['is_static_dir_separate']:
            cmd = "rsync -avzh "
            if project['static_dir_local'] in project['media_dir_local']:
                ex = project['media_dir_local'].replace(
                    project['static_dir_local'], '')
                cmd += ' --exclude {} '.format(ex)

            path_local = project['project_dir_local'] \
                + project['static_dir_local'].lstrip('/')
            cmd += '-e ssh {0} {1}@{2}:{3}'.format(
                path_local,
                username,
                server['main_ip'],
                project['static_dir_server']
            )
            cmds.append(cmd)

        # touch reload
        touch_path = project['project_dir_server'] \
            + project['reload_ini_path'].lstrip('/')
        cmd = 'ssh {0}@{1} touch {2}'.format(
            username,
            server['main_ip'],
            touch_path
        )
        cmds.append(cmd)

        cmd = ' && '.join(cmds)
        print(cmd)
        self.run_command_in_terminal(cmd)

    def django_user_rights(self, project_id):
        """Applies user rights on server"""
        project = self.get_project_by_id(project_id)
        server = self.get_server_by_id(project['server']['id'])
        username = self.get_local_linux_username()

        cmds = []
        cmd = 'ssh root@{0} chown -R {1}:{2} {3}'.format(
            server['main_ip'],
            username,
            server['nginx_name'],
            project['static_dir_server']
        )
        cmds.append(cmd)

        if project['is_static_dir_separate']:
            # If static directory is separate,
            # nginx must not have access to project
            # folder. Project folder is accessed only by user.
            cmd = 'ssh root@{0} chmod 0700 {1}'.format(
                server['main_ip'],
                project['project_dir_server']
            )
            cmds.append(cmd)

            # Nginx should have full access to static directory
            # (as Group member)
            cmd = 'ssh root@{0} chmod -R 0770 {1}'.format(
                server['main_ip'],
                project['static_dir_server']
            )
            cmds.append(cmd)
        else:
            # If static directory inside project - the 1st level directory
            # inside main project directory should have access only for user
            # and nobody else.
            # We can take 1st level directory for example from "requirements"
            # directory that is on 2nd level.

            cmd = 'ssh root@{0} chmod 0755 {1}'.format(
                server['main_ip'],
                project['project_dir_server']
            )
            cmds.append(cmd)

            # Nginx needs full access to static directory inside project
            # (as Group member)
            cmd = 'ssh root@{0} chmod 0770 {1}'.format(
                server['main_ip'],
                project['static_dir_server']
            )
            cmds.append(cmd)

            # 1st level directory inside project, where all python files,
            # should be accessible only by user.
            path = project['project_dir_server'] \
                + project['requirements_dir'].lstrip('/')
            path = dirname(dirname(path))
            cmd = 'ssh root@{0} chmod 0700 {1}'.format(
                server['main_ip'],
                path
            )
            cmds.append(cmd)

        cmd = ' && '.join(cmds)
        print(cmd)
        self.run_command_in_terminal(cmd)
