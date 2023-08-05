#!/usr/bin/env python
# coding: utf-8

"""
    PyLucid CGI dispatcher
    ~~~~~~~~~~~~~~~~~~~~~~

    You should check if the shebang is ok for your environment!
    some examples:
        #!/usr/bin/env python
        #!/usr/bin/env python2.4
        #!/usr/bin/env python2.5
        #!/usr/bin/python
        #!/usr/bin/python2.4
        #!/usr/bin/python2.5
        #!C:\python\python.exe

    Important:
        Used wsgiref, witch is new in Python 2.5!

    If settings.DEBUG is ON:
      - all write to stdout+stderr are checked. It's slow!
      - Its guaranteed that a HTML Header would be send first.

    :copyleft: 2007-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


#print "Content-type: text/html; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#print "Content-type: text/plain; charset=utf-8\r\n\r\nHARDCORE DEBUG:\n"
#import cgitb;cgitb.enable()


import os
import sys



#####################################################################################################
# PLEASE CHANGE THIS PATH:
#
os.environ["VIRTUALENV_FILE"] = "/please/insert/path/to/PyLucid_env/bin/activate_this.py"
#
# It's the absolute filesystem path to ...PyLucid_env/bin/activate_this.py
#
#####################################################################################################



# This must normally not changes, because you should use a local_settings.py file
os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


def traceback_end():
    """
    Print out a traceback and terminate with sys.exit()
    """
    print
    print "-" * 80
    print "Python v%s" % sys.version
    print "-" * 80
    try:
        import traceback
        print traceback.format_exc()
    except Exception, e:
        print "Error: %s" % e
    sys.exit()


try:
    virtualenv_file = os.environ["VIRTUALENV_FILE"]
except KeyError:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "environment variable VIRTUALENV_FILE not set!"
    print "(VIRTUALENV_FILE is the path to '.../PyLucid_env/bin/activate_this.py')"
    print
    traceback_end()


try:
    execfile(virtualenv_file, dict(__file__=virtualenv_file))
except Exception:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "VIRTUALENV_FILE value is wrong: %r" % virtualenv_file
    print
    print "Please edit the file %r and change the path!" % __file__
    print
    traceback_end()


try:
    from django.conf import settings
except:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "Can't import 'settings'!"
    print
    traceback_end()


try:
    from wsgiref.handlers import CGIHandler
except Exception, err:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "PyLucid - Low-Level-Error!"
    print
    print "Can't import CGIHandler from wsgiref: %s" % err
    print "(Note: wsgiref is new in Python 2.5!)"
    if sys.version_info[:2] < (2, 5):
        print "This Python version is too old!"
        print "If you have a new installed, please update shebang in %s" % __file__
        print
        print "Note: the virtualenv must be created with the same version!"
    print
    traceback_end()


if settings.DEBUG:
    """
    Redirect all write to stdout+stderr in DEBUG mode.
    """
    import cgi, inspect

    class BaseOut(object):
        """
        Base class for HeaderChecker and StdErrorHandler
        -global header_send variable
        """
        wrong_header = True
        header_send = False
        second_header = False

        def __init__(self, out):
            self.out = out
            self.oldFileinfo = ""

        def print_head(self, headline):
            self.out.write("Content-type: text/html; charset=utf-8\r\n\r\n")
            self.out.write("<h2>%s</h2>\n" % headline)
            self.header_send = True

        def _get_fileinfo(self):
            """
            Append the fileinfo: Where from the announcement comes?
            """
            try:
                self_basename = os.path.basename(__file__)
                if self_basename.endswith(".pyc"):
                    # cut: ".pyc" -> ".py"
                    self_basename = self_basename[:-1]

                for stack_frame in inspect.stack():
                    # go forward in the stack, to outside of this file.
                    filename = stack_frame[1]
                    lineno = stack_frame[2]
                    if os.path.basename(filename) != self_basename:
                        break

                filename = "...%s" % filename[-80:]
                fileinfo = "%-25s line %3s" % (filename, lineno)
            except Exception, e:
                fileinfo = "(inspect Error: %s)" % e

            return fileinfo

        def send_info(self):
            """
            Write information about the file and line number, from which the
            message comes from.
            """
            fileinfo = self._get_fileinfo()

            if fileinfo != self.oldFileinfo:
                # Send the fileinfo only once.
                self.oldFileinfo = fileinfo
                self.out.write(
                    "stdout/stderr write from: <strong>%s</strong>:\n" % fileinfo
                )

        def isatty(self):
            return False
        def flush(self):
            pass

    HEADERS = ("content-type:", "status: 301", "status: 302", "status: 200", "status: 500")
    class HeaderChecker(BaseOut):
        """
        Very slow! But in some case very helpfully ;)
        Check if the first line is a html header. If not, a header line will
        be send.
        """
        def check(self, txt):
            txt_lower = txt.lower()
            for header in HEADERS:
                if txt_lower.startswith(header):
                    return True
            return False

        def write(self, *txt):
            txt = " ".join([i for i in txt])
            if self.header_send:
                # headers was send in the past
                if self.check(txt) == True:
                    # second, normal header comes
                    self.second_header = True
                    self.out.write("</pre>")

            elif self.check(txt) == True:
                # the first Line is a header line -> send it
                self.wrong_header = False
                self.header_send = True
            else:
                self.print_head(headline="Wrong Header!")
                self.out.write("<pre>")

            if self.wrong_header == True and self.second_header == False:
                # Escape all content, since the second, normal header would be send
                self.send_info()
                txt = cgi.escape(txt)

            self.out.write(txt)


    class StdErrorHandler(BaseOut):
        """
        redirects messages from stderr to stdout.
        Sends a header, if the header were not already sent.
        """
        def write(self, *txt):
            txt = " ".join([i for i in txt])
            if not self.header_send:
                self.print_head(headline="Write to stderr!")

            self.send_info()
            self.out.write("<pre>%s</pre>" % cgi.escape(txt))

    old_stdout = sys.stdout
    sys.stdout = HeaderChecker(old_stdout)
    sys.stderr = StdErrorHandler(old_stdout)
#_____________________________________________________________________________



# Run PyLucid for one request:
try:
    from django.core.handlers.wsgi import WSGIHandler
    CGIHandler().run(WSGIHandler())
except Exception, err:
    print "Content-type: text/plain; charset=utf-8\r\n\r\n"
    print "Low-Level-Error: %s" % err
    print
    print "-" * 80
    print
    print "Have you installed PyLucid?"
    print
    print "If not, follow the instruction here:"
    print settings.INSTALL_HELP_URL
    print
    traceback_end()
