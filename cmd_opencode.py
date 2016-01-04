import sublime
import sublime_plugin

from .tools import Tools
from .core import Core


class VOpenCodeCommand(sublime_plugin.TextCommand):
    """
        Opens file by project name and partial filename.
        Command: projectname filename
    """

    def onselect(self, index):
        """QuickPanel - when found multiple files"""
        if index == -1:
            return

        file = self.files[index]
        Tools.open_file_in_second_group(file)

    def ondone(self, phrase):
        tup = phrase.split()
        if len(tup) != 2:
            sublime.error_message(
                'wrong input: it should be "projectname filename"')
            return

        name, filename = tup[0].strip(), tup[1].strip()
        sp = Core().get_files_by_project(name, filename)

        if not sp:
            sublime.error_message('files not found')
            return

        # if find 1 file - show it
        # else show multiple files on QuickPanel
        if len(sp) == 1:
            Tools.open_file_in_second_group(sp[0])
            return

        self.files = sp
        Tools.show_quick_panel(sp, self.onselect)

    def run(self, edit, **kw):
        Tools.show_input_panel(
            'Input: "projectname filename"', '', self.ondone, None, None)
