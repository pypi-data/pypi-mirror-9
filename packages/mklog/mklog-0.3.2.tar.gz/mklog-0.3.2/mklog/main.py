# Copyright 2009-2015 Louis Paternault

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Simple way of logging things.

* "Logging" means prepending date and time at the beginning of lines.
* "Things" may be content of files, standard input, or output of a command.
"""

from collections import namedtuple
import argparse
import logging
import subprocess
import sys
import textwrap
import threading
import time

import mklog
from mklog import errors

LOGGER = logging.getLogger(mklog.__name__)
LOGGER.addHandler(logging.StreamHandler())

TIMEFORMAT = "%Y-%m-%d %H:%M:%S"

################################################################################
##### Print line preceded by date and time
# No verification is done whether argument contains exactly one line or not.
def log(line, output_format, error=False):
    r"""Print argument to standard output, preceded by current time and date

    Arguments:
    - error: if True, print it to standard error, in standard output otherwise.
    - line: a string to print, supposed to end with an EOL character (\n).
    - output_format: a named tuple of two strings.
        - output_format.line is the line-format. It can (should?) contain
          substrings as "{time}" and "{output}" which are replaced by current
          time and the line to print.
        - output_format.time is the time-format. It will be passed to
          "time.strftime()" to print current time.
    """
    if error:
        out = sys.stderr
    else:
        out = sys.stdout
    out.write(output_format.line.format(
        time=time.strftime(output_format.time),
        output=line[:-1],
        ))
    out.write("\n")
    out.flush()

def log_pipe(pipe, output_format, error=False):
    """Print content from "pipe", preceding it by current date and time

    If error it True, print it to standard error, in standard output otherwise.
    Output_format is the format to use to print content. See log() to know its
    syntax.
    """
    while 1:
        # For each line in file "pipe", print it, preceded with current time
        line = pipe.readline()
        if line == '':
            break
        log(line, output_format, error)

################################################################################
def set_daemon(thread):
    "Set deamon mode of thread to true (tricky because changes of Python API)"
    if hasattr(thread, "daemon"):
        thread.daemon = True
    else:
        thread.setDaemon(True)

################################################################################
def safe_open(name):
    """Safely open a file, and return

    - None if an error occured
    - The file object otherwise"""
    try:
        return open(name, 'r')
    except IOError:
        LOGGER.error("Error while opening '%s'.", name)
        return None

################################################################################
### Parsing arguments
def commandline_parser():
    """Parse command line

    Return a tuple (options, file), where:
    - options: a dictionary containing only the command (if any) to be executed
      (corresponding to option "-c") in the key "command";
    - file: the list of files to be processed.
    """
    # Defining parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""
            Print the standard input, content of files, or result of a command
            to standard output, preceded by date and time (in a log-like way).
            """),
        epilog=textwrap.dedent("""
            `mklog` aims to be a simple way to write text in a log format,
            i.e.  each line being preceded by date and time it was written.
            Text can be either standard input, content of files, or both
            standard and error output of a command.

            If neither files nor a command are given, standard input is
            processed.  Otherwise, the content of each file (if any), and the
            output of the command (if any) are processed.

            # Environment

            When executing command (with `-c` option), environment is
            preserved, and command should run exactly the same way it should
            have run if it had been executed directly within the shell.
            """),
        )

    parser.add_argument(
        '--version',
        action='version',
        version="%(prog)s {version}".format(
            version=mklog.VERSION,
            ),
        )

    parser.add_argument(
        "files",
        metavar="FILES",
        nargs='*',
        help="Files to process.",
        )

    parser.add_argument(
        "-f", "--format",
        dest="line_format",
        default="{time} {output}",
        help=textwrap.dedent("""\
            Format of output. Interpreted sequences are "{time}" for current
            time, "{output}" for output of the command.  Default is "{time}
            {output}".
            """),
        )

    parser.add_argument(
        "-t", "--time-format",
        dest="time_format",
        default=TIMEFORMAT,
        help=textwrap.dedent("""\
            Format of time. See the "time" documentation for more information
            about format (e.g.
            http://docs.python.org/library/time.html#time.strptime).  Default
            is "{}".
            """.format(TIMEFORMAT.replace('%', '%%'))),
        )

    parser.add_argument(
        "-c", "--command",
        nargs=argparse.REMAINDER,
        help=textwrap.dedent("""
            Run command, processing both its standard and error output.

            Commands can be written whithout quotes (such as `mklog -c tail -f
            file1 file2`), or with it, which allows using shell features (such
            as `mklog -c "(ls; cat file1) & cat file2"`).

            Destination of output is preserved: standard output of command is
            written to standard output of `mklog`, and standard error to
            standard error. Both are processed.

            This must be the last option on the command line.
        """),
        )


    # Running parser
    return parser

################################################################################
### Main function
def main():
    "Main function"

    options = commandline_parser().parse_args()
    # Now, "options" contains a dictionary containing only the command (if any)
    # to be executed (corresponding to option "-c") in the key "command", and
    # "files" contains the list of files to be processed.

    try:
        # Handling files
        # At the end of this block, "files" will contain the list of files to
        # be read from: either files given in argument, or standard input if no
        # file is given in the command line.
        if len(options.files) == 0 and options.command == None:
            options.files = [sys.stdin]
        else:
            options.files = [safe_open(f) for f in options.files]

        # Processing "options.line_format" and "options.time_format".
        # Quick and dirty parsing.
        output_format = namedtuple("Format", "line, time")(
            line=options.line_format,
            time=options.time_format,
            )

        # Processing files
        for file_descriptor in options.files:
            if file_descriptor is None:
                continue
            log_pipe(file_descriptor, output_format)

        # Handling command
        if options.command != None:
            try:
                process = subprocess.Popen(
                    options.command,
                    stdin=sys.stdin,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    shell=(len(options.command) == 1),
                    )
            except OSError:
                raise errors.ExecutionError(options.command)
            standard_output = threading.Thread(
                target=log_pipe,
                kwargs={
                    'pipe' : process.stdout,
                    'output_format': output_format
                    }
                )
            standard_error = threading.Thread(
                target=log_pipe,
                kwargs={
                    'pipe' : process.stderr,
                    'error' : True,
                    'output_format': output_format
                    }
                )
            set_daemon(standard_output)
            set_daemon(standard_error)
            standard_error.start()
            standard_output.start()
            standard_error.join()
            standard_output.join()
            process.wait()

    except KeyboardInterrupt:
        sys.exit(1)
    except errors.MklogError as error:
        LOGGER.error(error)
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
