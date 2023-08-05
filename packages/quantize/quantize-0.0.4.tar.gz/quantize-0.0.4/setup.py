import uuid
try:
    from setuptools import setup
except ImportError:
    raise ImportError(
        "Please upgrade `setuptools` to the newest version via: "
        "`pip install -U setuptools`"
    )

def build():
    setup(
        name = "quantize",
        version = "0.0.4",
        author = "Brian Abelson",
        author_email = "brianabelson@gmail.com",
        description = "A simple command line utility for syncing arbitrary messages sent via `stdin` to a midi clock.",
        license = "MIT",
        keywords = "midi, midi clock, command line",
        url = "https://github.com/abelsonlive/quantize",
        packages = ['quantize'],
        long_description = "",
        install_requires = [
            "gevent==1.0.1",
            "greenlet==0.4.5",
            "mido==1.1.12",
            "python-rtmidi==0.5b1"
        ],
        scripts = ['bin/q'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Communications :: Email",
            "License :: OSI Approved :: MIT License",
        ]
    )

if __name__ == '__main__':
    build()