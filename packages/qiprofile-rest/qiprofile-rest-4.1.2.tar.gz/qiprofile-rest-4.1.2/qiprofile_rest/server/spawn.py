import sys
import os
from subprocess import (Popen, PIPE, STDOUT)

APP = os.path.abspath(os.path.join(os.path.dirname(__file__), 'run.py'))
"""The Python script to run."""


def spawn():
    """
    Start the Quantitaive Imaging Profile REST server.
    
    :return: the completed process return code
    """
    # The cumbersome but apparently necessary idiom below is required to continuously
    # pipe the server output to the console
    # (cf. http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running).
    proc = Popen(['python', APP], stdout=PIPE, stderr=STDOUT)
    while True:
        line = proc.stdout.readline()
        if line == '' and proc.poll() != None:
            break
        sys.stdout.write(line)
        sys.stdout.flush()
    out, _ = proc.communicate()
    rc = proc.returncode
    
    return rc
