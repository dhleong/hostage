
import re

from ..core import Result

def readGradleDef(path, name):
    pattern = re.compile("%s\\s*=\\s*(.*)" % name)
    with open(path) as fp:
        for line in fp:
            m = pattern.findall(line)
            if m:
                return Result(m[0])
    return Result()

