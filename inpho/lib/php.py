"""
Provides a simple interface to legacy PHP code, such as fuzzymatch.
"""
import subprocess

class PHP:
    """This class provides a simple interface to PHP programming."""

    def __init__(self, prefix="", postfix=""):
        """prefix = optional prefix for all code (usually require statements)
        postfix = optional postfix for all code
        Semicolons are not added automatically, so you'll need to make sure to put them in!"""

        self.prefix = prefix
        self.postfix = postfix

    def __submit(self, code):
        """Sends code to the PHP interpreter, returning the output."""
        p = subprocess.Popen("php", shell=True, stdin=subprocess.PIPE, 
                             stdout=subprocess.PIPE, close_fds=True)
        (out, inp) = (p.stdout, p.stdin)
        print >>inp, "<?php "
        print >>inp, self.prefix
        print >>inp, code
        print >>inp, self.postfix
        print >>inp, " ?>"
        inp.close()
        return out

    def get_raw(self, code):
        """Given a code block, invoke the code and return the raw result."""
        out = self.__submit(code)
        return out.read()

    def get(self, code):
        """
        Given a code block that emits json, invoke the code and return the 
        result as a native Python dictionary.
        """

        out = self.__submit(code)
        return json.loads(out.read())

    def get_one(self, code):
        """
        Given a code block that emits multiple json values (one per line), 
        yield the next value.
        """

        out = self.__submit(code)
        for line in out:
            line = line.strip()
            if line:
                yield json.loads(line)
