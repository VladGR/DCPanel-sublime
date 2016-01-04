import sublime
import sublime_plugin

from .tools import Tools
from .core import Core


class VControlDatabasesCommand(sublime_plugin.WindowCommand):
    MESSAGE_MYSQL = 'Currently only MySQL supported for database control.'

    def init_commands(self):
        self.cmdtups = []
        self.cmdtups.append(('.. ({})'.format(self.db_name), '000'))
        self.cmdtups.append(('Download database from remote server', '001'))
        self.cmdtups.append(
            ('Create database on remote server (if not exists)', '002'))
        self.cmdtups.append(('Upload database to remote server', '003'))

        self.cmds = [tup[0] for tup in self.cmdtups]

    def onselect_db(self, index):
        if index == -1:
            return

        dic = self.dbs[index]
        self.db_id = dic['id']
        self.type_db = dic['type_db']
        self.db_name = dic['name']

        self.init_commands()
        Tools.show_quick_panel(self.cmds, self.onselect_cmd)

    def onselect_001(self):
        if self.type_db != 'M':
            sublime.message_dialog(self.MESSAGE_MYSQL)
            return

        Core().download_database(self.db_id)

    def onselect_002(self):
        if self.type_db != 'M':
            sublime.message_dialog(self.MESSAGE_MYSQL)
            return

        res = Core().create_database(self.db_id)
        if res is True:
            sublime.message_dialog('OK')
        else:
            sublime.message_dialog('Error')

    def onselect_003(self):
        if self.type_db != 'M':
            sublime.message_dialog(self.MESSAGE_MYSQL)
            return
        sublime.ok_cancel_dialog(
            'Current database on remote server will be destroyed. \
            Are you sure?', 'Continue')
        Tools.show_input_panel(
            'Input confirmation password', '', self.oninput_003, None, None)

    def oninput_003(self, confirmation_password):
        if confirmation_password != Core().get_confirmation_password():
            sublime.message_dialog('Confirmation password is not correct.')
            return

        c = Core()
        res = c.is_database_exists_on_localhost(self.db_id)
        if res is False:
            message = 'To run this operation, database "{}" \
                should be exist on localhost'
            message = message.format(self.db_name)
            sublime.message_dialog(message)
            return

        c.upload_database(self.db_id)

    def onselect_cmd(self, index):
        """Runs command for chosen database"""
        if index == -1:
            return

        tup = self.cmdtups[index]
        cmd = tup[1]
        if cmd == '000':
            self.run()
        elif cmd == '001':
            self.onselect_001()
        elif cmd == '002':
            self.onselect_002()
        elif cmd == '003':
            self.onselect_003()

    def run(self, **kw):
        dbs = Core().get_databases()
        # filter only Project DBs
        self.dbs = [d for d in dbs if d['type'] == 'P']

        sp = ['{0} : {1} {2}'.format(
            d['name'],
            d['project_name'],
            d['type_db_name']) for d in self.dbs]
        Tools.show_quick_panel(sp, self.onselect_db)
