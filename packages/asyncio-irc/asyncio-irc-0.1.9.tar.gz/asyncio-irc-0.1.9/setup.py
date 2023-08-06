from distutils.core import setup

setup(
        name="asyncio-irc",
        version="0.1.9",
        description="irc based on asyncio",
        author="Fox Wilson",
        author_email="fwilson@fwilson.me",
        url="https://github.com/watchtower/asyncirc",
        install_requires=["blinker"],
        packages=["asyncirc", "asyncirc.plugins"]
)
