import re
import sublime
import sublime_plugin

from .tools import Tools
from . import core


class VControlServersCommand(sublime_plugin.WindowCommand):
    def init_commands(self):
        self.cmdtups = []
        self.cmdtups.append(('.. {0} {1}'.format(
            self.server['code'], self.main_ip), '000'))
        self.cmdtups.append(('Remove known hosts for the IP', '001'))
        self.cmdtups.append(('Create SSH keys', '002'))
        self.cmdtups.append(('Create user on remote server', '003'))
        self.cmdtups.append(('Copy "control script" to remote server', '004'))
        self.cmdtups.append(('View "control script" logs', '005'))
        self.cmdtups.append(('Clear "control script" logs', '006'))

        self.cmds = [tup[0] for tup in self.cmdtups]

    def onselect_server(self, index):
        """ip (or ips) copy to Clipboard"""
        if index == -1:
            return

        id = self.servers[index]['id']
        self.server = core.Core().get_server_by_id(id)

        self.main_ip = self.server['main_ip']

        sublime.set_clipboard(self.main_ip)
        message = 'Server: {0}, IP address: {1} copied to clipboard'.format(
            self.server['code'], self.main_ip)
        sublime.status_message(message)

        self.init_commands()
        Tools.show_quick_panel(self.cmds, self.onselect_cmd)

    def check_username(self, username):
        if not re.match('[a-zA-Z0-9]+$', username):
            sublime.message_dialog('Username is incorrect.')
            return False
        return True

    def onselect_001(self):
        c = core.Core()
        Tools.clear()
        local_user = c.get_local_linux_username()
        cmd = 'ssh-keygen -f "/home/{0}/.ssh/known_hosts" -R {1}'.format(
            local_user, self.main_ip)
        res = c.run_command_in_subprocess(cmd)
        if res is True:
            sublime.message_dialog('OK')
        else:
            sublime.message_dialog('Error!')

    def oninput_002(self, remote_user):
        if self.check_username(remote_user) is False:
            return

        c = core.Core()
        local_user = c.get_local_linux_username()
        cmd = 'ssh-copy-id -i /home/{0}/.ssh/id_rsa.pub {1}@{2}'.format(
            local_user, remote_user, self.main_ip)
        c.run_command_in_terminal(cmd)

    def oninput_003(self, remote_user):
        """Creates user on remote host.

        Generates password for remote user and adds ssh keys.
        Doesn't store password, because access via ssh keys.
        On local machine sshpass should be installed.
        sudo apt-get install sshpass
        """
        if self.check_username(remote_user) is False:
            return

        c = core.Core()
        # ignore error if user exists
        cmd = 'ssh root@{0} "id -u {1} &>/dev/null'
        cmd += ' || useradd {1} -d /home/{1} -m"'
        cmd = cmd.format(self.main_ip, remote_user)

        res = c.run_command_in_subprocess(cmd)

        # create password and keys
        new_password = c.randstring(15)
        # sudo is important
        # without sudo: pam_chauthtok() failed, error
        cmd = 'ssh root@{0} \'echo "{1}:{2}" | sudo chpasswd\''.format(
            self.main_ip, remote_user, new_password)
        res = c.run_command_in_subprocess(cmd)

        if res is False:
            sublime.message_dialog('Change password error.')
            return

        # copy keys to server
        # run command from current main system user (not sudo)
        cmd = 'sshpass -p {0} ssh-copy-id -i ~/.ssh/id_rsa.pub {1}@{2}'.format(
            new_password, remote_user, self.main_ip)
        c.run_command_in_terminal(cmd)

        sublime.message_dialog('Done. Try to login to ssh by keys.')

    def onselect_cmd(self, index):
        """Runs command for chosen server"""
        if index == -1:
            return

        c = core.Core()
        tup = self.cmdtups[index]
        cmd = tup[1]
        if cmd == '000':
            self.run()

        elif cmd == '001':
            self.onselect_001()

        elif cmd == '002':
            Tools.show_input_panel(
                'Input username', '', self.oninput_002, None, None)

        elif cmd == '003':
            Tools.show_input_panel(
                'Input username', '', self.oninput_003, None, None)

        elif cmd == '004':
            c.copy_control_to_server(self.server['id'])

        elif cmd == '005':
            output = c.view_control_script_logs(self.server['id'])
            Tools.clear()
            Tools.showpanel()
            print(output.decode())

        elif cmd == '006':
            res = c.clear_control_script_logs(self.server['id'])
            if res is True:
                sublime.message_dialog('OK')
            else:
                sublime.message_dialog('Error!')

    def run(self, **kw):
        Tools.clear()
        self.servers = core.Core().get_servers()
        l = []
        for s in self.servers:
            if not s['ips']:
                ip = '---'
            else:
                ip = s['ips'][0]
            l.append('{0} : {1}, ips: {2}'.format(
                s['code'], ip, len(s['ips'])))
        Tools.show_quick_panel(l, self.onselect_server)
