import sublime_plugin

from .tools import Tools


class VControlMenuCommand(sublime_plugin.WindowCommand):
    @property
    def sp(self):
        self.commands = (
            ('Databases', 'v_control_databases', '', ''),
            ('Control servers', 'v_control_servers', '', ''),
            ('Deploy current project', 'v_deploy_project', '', ''),
            ('Django projects', 'v_list_projects', 'type', 'DJ'),
            ('Python projects', 'v_list_projects', 'type', 'PY'),
            ('GoLang projects', 'v_list_projects', 'type', 'GO'),
            ('PHP projects', 'v_list_projects', 'type', 'PHP'),
            ('HTML projects', 'v_list_projects', 'type', 'HTML'),
            ('Open file by project and filename', 'v_open_code', '', ''),
            ('Generate myssh bash script', 'v_generate_myssh', '', ''),
        )
        return [tup[0] for tup in self.commands]

    def onselect(self, index):
        if index == -1:
            return

        tup = self.commands[index]
        cmd = tup[1]

        dic = {'type': tup[3]} if tup[2] == 'type' else {}
        self.window.run_command(cmd, dic)

    def run(self):
        Tools.clear()
        Tools.show_quick_panel(self.sp, self.onselect)
