import sublime


class Tools:
    def clear():
        print('\n'*10)

    def showpanel():
        """Show console"""
        sublime.active_window().run_command("show_panel", {"panel": "console"})

    def show_quick_panel(options, done):
        """Helper method - show QuickPanel multiple times via timeout"""
        sublime.set_timeout(
            lambda: sublime.active_window().show_quick_panel(
                options, done), 10)

    def show_input_panel(title, initial, ondone, onchange, oncancel):
        """Helper method for InputPanel"""
        sublime.set_timeout(
            lambda: sublime.active_window().show_input_panel(
                title, initial, ondone, onchange, oncancel), 10)

    def set_1column_layout():
        sublime.active_window().set_layout({
            "cols": [0.0, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1]]
        })

    def set_2column_layout():
        sublime.active_window().set_layout({
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]   # x1,y1,x2,y2  x1,y1,x2,y2
        })

    def new_file_in_second_group():
        """Opens new file in second group.

        Creates second group, if only one group exists.
        """

        w = sublime.active_window()
        num = w.num_groups()
        if num == 1:
            Tools.set_2column_layout()

        v = w.new_file()
        w.set_view_index(v, 1, 0)
        w.focus_group(1)

    def open_file_in_second_group(file):
        """Opens file in second group."""

        w = sublime.active_window()
        num = w.num_groups()
        if num == 1:
            Tools.set_2column_layout()

        w.focus_group(1)
        w.open_file(file)
        # v = w.open_file(file)
