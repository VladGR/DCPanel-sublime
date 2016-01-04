"""
plugin_loaded: Run own operations on Sublime Load.
"""

import sublime
import threading


def my_func():
    """Can run any function on Sublime start and make any initial actions"""
    sublime.status_message('Sublime started...')


def plugin_loaded():
    t = threading.Thread(target=my_func)
    t.daemon = True
    t.start()
