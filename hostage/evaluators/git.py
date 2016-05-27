
from .base import execute

def gitTagExists(name):
    return execute("git", "tag", "-l", name)

