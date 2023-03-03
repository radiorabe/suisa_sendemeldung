"""Set up suisa_sendemeldung."""

from setuptools import setup

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()


setup(
    name="suisa_sendemeldung",
    description="ACRCloud client for SUISA reporting",
    url="http://github.com/radiorabe/suisa_reporting",
    author="RaBe IT-Reaktion",
    author_email="it@rabe.ch",
    license="MIT",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    install_requires=requirements,
    packages=["suisa_sendemeldung"],
    entry_points={
        "console_scripts": [
            "suisa_sendemeldung=suisa_sendemeldung.suisa_sendemeldung:main"
        ],
    },
    zip_safe=True,
)
