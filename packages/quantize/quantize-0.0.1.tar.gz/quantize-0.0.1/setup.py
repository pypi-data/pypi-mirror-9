import uuid
try:
    from setuptools import setup
    from pip.req import parse_requirements
except ImportError:
    raise ImportError(
        "Please upgrade `setuptools` to the newest version via: "
        "`pip install -U setuptools`"
    )

def build():
    setup(
        name = "quantize",
        version = "0.0.1",
        author = "Brian Abelson",
        author_email = "brianabelson@gmail.com",
        description = "A simple command line utility for syncing arbitrary messages sent via `stdin` to a midi clock.",
        license = "MIT",
        keywords = "midi, midi clock, command line",
        url = "https://github.com/abelsonlive/quantize",
        packages = ['quantize'],
        long_description = "",
        install_requires = [str(ir.req) for ir in parse_requirements("requirements.txt", session=uuid.uuid1())],
        scripts = ['bin/q'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Communications :: Email",
            "License :: OSI Approved :: MIT License",
        ]
    )

if __name__ == '__main__':
    build()