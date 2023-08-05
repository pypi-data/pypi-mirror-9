#! /usr/bin/python
#
# Echo StreamServer: Echo Query Language Shell
# ============================================================
import sys, os, readline
import atexit

from echo import __version__ as echo_version
from echo import items, users, StreamServerError
from echo.core_api import default_account
from pprint import pprint

__author__ = 'Andrew Droffner'

# Use GNU Readline and a history file.
# ============================================================
histfile = os.path.join(os.path.expanduser("~"), ".eqlhist")
try:
    readline.read_history_file(histfile)
except IOError:
    pass
atexit.register(readline.write_history_file, histfile)

# Introduction
# ============================================================
sys.stdout.write("""
Echo Query Language Shell (echo.items version %(version)r)
Account: %(default_account)r

Send an EQL text string to Stream Server and display the results.
EQL> url:http://example.com/index.html

Prompts:
EQL>   "This prompt means execute a search."
COUNT> "This prompt means execute a count."

Shell Commands
COUNT:  Set to COUNT> mode.
SEARCH: Set to SEARCH> mode.
USERS:  Set to USERS> mode.
QUIT:   Quit the shell.

""" % {
    'version': echo_version,
    'default_account': default_account,
})

# Read-Execute Loop:
# ============================================================
cmd_mode = 'SEARCH'
cmd_mode_list = [ 'COUNT', 'SEARCH', 'USERS' ]

while True:
    try:
        # Prompt user for EQL text string.
        # Example: "url:http://www-stage.nola.com/festivals/index.ssf/2012/06/testing_3_4_5.html")
        eql_text = raw_input('%s> ' % cmd_mode)
        eql_text = eql_text.strip()

        # Skip empty lines.
        if '' == eql_text:
            continue
        # Shell Commands:
        if eql_text.upper() in cmd_mode_list:
            cmd_mode = eql_text.upper()
            continue
        # QUIT Shell:
        if 'QUIT' == eql_text.upper():
            sys.exit()

        # Based on the prompt, execute the command, e.g. a "count" or "search" query.
        if 'COUNT' == cmd_mode:
            n = items.count(eql_text)
            sys.stdout.write("\tCOUNT: %d\n" % n)
        elif 'SEARCH' == cmd_mode:
            r = items.search(eql_text)
            pprint(r)
        elif 'USERS' == cmd_mode:
            r = users.get(eql_text)
            pprint(r)

    except StreamServerError, e:
        sys.stderr.write("Echo StreamServer: [%s] %s\n" % (e.errorCode, e.errorMessage))
    except (EOFError, KeyboardInterrupt, SystemExit):
        sys.stderr.write("\nQUIT\n\n")
        sys.exit()

