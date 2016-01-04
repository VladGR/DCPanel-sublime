import os
import sublime
import sublime_plugin

from .core import Core


class VGenerateMysshCommand(sublime_plugin.WindowCommand):
    def run(self, **kw):
        c = Core()
        bash_dir = c.get_local_bash_dir()
        path = bash_dir + 'myssh'

        servers = c.get_servers()
        names = ', '.join([d['code'] for d in servers])

        data = '#!/bin/bash\n\n'
        data += 'clear\n\n'
        data += 'echo "enter host: {} "\n'.format(names)
        data += 'read host\n\n'

        data += 'case "$host" in\n\n'

        for d in servers:
            data += '"{}"\t ) ssh root@{} ;;\n'.format(d['code'], d['main_ip'])

        data += '\n\n'
        data += 'esac\n\n'
        data += 'exit 0'

        with open(path, 'w') as f:
            f.write(data)

        os.chmod(path, 0o755)
        sublime.message_dialog('File generated.')
