import sublime
import sublime_plugin


class SetTextToView(sublime_plugin.TextCommand):
    """Input: group number, text"""
    def run(self, edit, group, text):
        v = sublime.active_window().active_view_in_group(group)
        v.insert(edit, 0, text)


class CreateOutputPanelWithText(sublime_plugin.TextCommand):
    """Input: text"""
    def run(self, edit, text):
        w = sublime.active_window()
        v = w.create_output_panel("temppanel")
        v.insert(edit, 0, text)
        w.run_command("show_panel", {"panel": "output.temppanel"})
