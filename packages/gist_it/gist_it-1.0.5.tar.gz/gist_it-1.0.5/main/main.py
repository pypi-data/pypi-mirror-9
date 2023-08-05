# -*- coding: utf-8 -*-
"""Gist_it can send gist

ex)
gist_it FILE_NAME
cat FILE_NAME | gist_it

oauth credential is saved $HOME/.gist_it_credential
if occure error. rm $HOME/.gist_it_credential

Usage:	gist_it -h | --help
	gist_it init [--credential=<credential>]
	gist_it [-a] [-p] [--credential=<credential>] [--title=<title>] <file>
	gist_it [-a] [-p] [--credential=<credential>] [--title=<title>] 

Options:
	init		if use auth user. (only first time)
	file		If omitted, use stdin.
	-h --help	show this help message and exit
	-a		auth user (if use stdin. run "gist_it init")
	-c		github oauth credential path (use cache)
	-p		add public option
	--title=<title>	add title [default: "None"].
	--credential=<credential>	set credential path

"""

from docopt import docopt
import sys
import os
from gist import Gist
from github import Github

class GistitException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def main():
    args = docopt(__doc__)

    credential = args["--credential"]
    if not credential or not os.path.isfile(credential):
        credential = os.environ['HOME'] + "/.gist_it_credential"

    if args["init"]:
        Github().get_credential(Gist.scope, credential)
        print "save credential to %s" % credential
        return

    is_public = False
    if args["-p"]:
        is_public = True

    is_auth = False
    if args["-a"]:
        is_auth = True

    text = ""
    file_name = args["<file>"]
    if file_name and os.path.isfile(file_name):
        text = open(file_name).read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print __doc__
        sys.exit(1)

    if args["--title"]:
        file_name = args["--title"]

    response = Gist(credential).create(file_name,text,"",is_public,is_auth)
    if response and "html_url" in response:
        print response["html_url"]
    else:
        raise GistitException("gist response error")
        

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print e
        sys.exit(1)
