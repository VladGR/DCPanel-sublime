import sublime
import sublime_plugin

from .tools import Tools
from .core import Core


class VListProjectsCommand(sublime_plugin.WindowCommand):
    def init_commands(self):
        self.cmdtups = []
        self.cmdtups.append(('.. {0}'.format(self.project['name']), '000'))

        if self.project['type'] == 'DJ':
            self.cmdtups.append(('Create venv on localhost', '001'))
            self.cmdtups.append(('Download "media" from remote host', '002'))

        self.cmdtups.append(('Show info', '003'))

        self.cmds = [tup[0] for tup in self.cmdtups]

    def onselect_project(self, index):
        if index == -1:
            return

        self.project = self.projects[index]
        self.init_commands()
        Tools.show_quick_panel(self.cmds, self.onselect_cmd)

    def onselect_001(self):
        Core().create_venv_localhost(self.project['id'])

    def onselect_002(self):
        Core().download_django_media(self.project['id'])

    def onselect_003(self):
        sublime.message_dialog(Core().format_dic_to_message(self.project))

    def onselect_cmd(self, index):
        "run command for chosen project"
        if index == -1:
            return

        tup = self.cmdtups[index]
        cmd = tup[1]
        if cmd == '000':
            self.run(type=self.project['type'])
            return

        if cmd == '001':
            self.onselect_001()
            return

        if cmd == '002':
            self.onselect_002()
            return

        if cmd == '003':
            self.onselect_003()
            return

    def run(self, **kw):
        self.projects = Core().get_projects(kw['type'])
        sp = []
        for d in self.projects:
            if d['server'] is None:
                row = '{0} : No server'.format(d['name'])
            else:
                row = '{0} : {1} ({2})'.format(
                    d['name'],
                    d['server']['code'],
                    d['server']['country']['name']
                )
            sp.append(row)

        Tools.show_quick_panel(sp, self.onselect_project)
