
from hostage import *

# findFile("./gradlew").orElse(echoAndDie("Run from project root"))

# grepStatus("stopship").then(echoAndDie("I don't think so"))

version = readGradleDef("foo.gradle", "VERSION_NAME_BETA") \
        .valueElse(echoAndDie("No VERSION_NAME_BETA?"))

gitTagExists(version).then(echoAndDie("Tag %s already exists" % version))

echo.do("Done", version)


