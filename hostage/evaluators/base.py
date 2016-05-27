#
# Basic functions
#

import os.path
import subprocess

from ..core import Result

def _hasAg():
    # TODO we should probably cache this result:
    try:
        subprocess.check_output(["which", "ag"])
        return True
    except:
        return False

def execute(*commands):
    """Execute the given commands as subprocess and resolve
    to the output of the command
    """
    try:
        return Result(subprocess.check_output(commands))
    except subprocess.CalledProcessError, e:
        return Result()

def execStatus(*commands):
    """Execute the commands and resolve to True for a successful
    result. The output goes to stdout as if executing in a shell
    """
    try:
        return Result(0 == subprocess.check_call(commands))
    except subprocess.CalledProcessError, e:
        return Result()

def findFile(path):
    """Resolves to True if the file path exists"""
    return Result(os.path.exists(path))

def grep(text):
    """Resolves to any found text. Prefers `ag` if installed"""
    if _hasAg():
        # if `ag` is installed, prefer it
        return execute("ag", text)
    else:
        return execute("grep", "-R", text, ".")

def grepStatus(text):
    """As with execStatus, dumps the output to stdout
    regardless of the result code (but resolves to True
    or None based on status)
    """
    if _hasAg():
        # if `ag` is installed, prefer it
        return execStatus("ag", text)
    else:
        return execStatus("grep", "-R", text, ".")
