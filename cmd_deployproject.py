import sublime
import sublime_plugin

from os.path import basename, dirname
from .core import Core


class VDeployProjectCommand(sublime_plugin.WindowCommand):

    def deploy_dj(self, project_id):
        Core().deploy_django_project(project_id)

    def deploy_php(self, project_id):
        """Copying project local files to project server files"""
        Core().deploy_php_project(project_id)

    def deploy_html(self, project_id):
        """Copying project local files to project server files"""
        Core().deploy_html_project(project_id)

    def deploy_go(self, project_id):
        """Copying project_local_dir/bin/* to project_server_dir"""
        Core().deploy_go_project(project_id)

    def run(self, **kw):
        w = sublime.active_window()

        # get project path
        path = w.project_file_name()

        if not path:
            sublime.error_message('Project file has not found.')
            return

        # One level up - config directory with project file:
        #     config/project.sublime-project
        # Two levels up - projectname directory (dirname = project name)
        #   projectname/config/project.sublime-project
        #   projectname/project/project_data_files

        name = basename(dirname(dirname(path)))

        # find project by name
        c = Core()
        project = c.get_project_by_name(name)

        # set 755 for all directories inside project directory
        cmd = "find {} -type d -exec chmod 755 {{}} +".format(
            project['project_dir_local'])
        c.run_command_in_subprocess(cmd)

        # set 644 for all files inside project directory
        if project['type'] != 'GO':
            cmd = "find {} -type f -exec chmod 644 {{}} +".format(
                project['project_dir_local'])
            c.run_command_in_subprocess(cmd)

        # run func by project type
        func = getattr(self, 'deploy_{}'.format(project['type'].lower()))
        return func(project['id'])
