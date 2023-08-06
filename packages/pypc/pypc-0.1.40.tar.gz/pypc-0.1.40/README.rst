====
pypc
====

|Build Status|

The Python3 Package Creator.

Pypc generates standard scaffolding and environment for a Python package.

* Creates the directory structure show above in `Usage`
* Installs virtualenv + creates venv directory
* Installs pyflakes, pep8 to venv

Installation
============

    $ pip install pypc

Usage
=====
How do I create a pip python package? The following will create a
standard package, as generally described in
https://packaging.python.org/en/latest/distributing.html. It will also
setup virtualenv, pip install pyflakes and pep8, and generate a
requirements.txt.

    # Standard build

    $ pypc project
    
    $ cd project;ls

    AUTHORS  CHANGES  docs/  examples/  LICENSE  MANIFEST.in  project/  README.md  requirements.txt  setup.py  tox.in  venv/

Alternatively, you can run in minimal mode with -m or --minimal. This
only creates a README and setup.py and does not require network access
(after pypc is installed).

    # Minimal install

    $ pypc -m project

    $ cd project;ls

    project/  README.rst  setup.py

In both cases, project/ is populated with a __init__.py.


Options
=======

    usage: pypc [-h] [-m] [-V] [--author AUTHOR] [--email EMAIL]
                [--version VERSION] [--desc DESC] [--url URL] [--rm README]
                [--fs FS]
                path

If you only want to create a package with a setup.py (no virtual env,
etc), use the -m or --minimal flag.

Note: -V outputs the version of pypc whereas --version is used to
 specify the initial version of the package you are creation. This is
 slightly confusion, and improvements are welcome.

Philosopy
=========
* KISS. Small and simple enough (i.e. Flask/webpy, not django) that it can be integrated into pip,
* Defaults. a default modus of operandi which works offline,
* PEP 20. "There should be one-- and preferably only one --obvious way to do it." In this respect, the general file structure should remain static and accept overrides/overloading of templates and if specific modules/packages (like flask) require specific (additional) file structure, a builder can import/bootstrap using pypc (as it would pip)

Standards
=========
Resources about the standards and walkthroughs:

* http://guide.python-distribute.org/creation.html
* http://www.scotttorborg.com/python-packaging/minimal.html
* http://stackoverflow.com/questions/9411494/how-do-i-create-a-pip-installable-project
* http://docs.python-guide.org/en/latest/writing/structure/
* http://www.kennethreitz.org/essays/repository-structure-and-python
* http://as.ynchrono.us/2007/12/filesystem-structure-of-python-project_21.html
* http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/

Alternatives
============
* https://github.com/audreyr/cookiecutter
* https://github.com/seanfisk/python-project-template - Git based, clone repo (requires altering git history)

Questions for you
=================
1) Does the file structure pypc generates break any conventions?
2) Is the code for pypc readable/accessible?
3) Feature suggestions? (would love to auto-init venv)

Disclaimer
==========
Pypc is a pre-alpha proof of concept. It's slow as it installs pyflakes, pep8, virtualenv sets up a virtualenv, and then generates a freeze list of requirements).
Right now there is little to no test-coverage; being it is a proof of concept, I'll try to continue as TDD.

Discussion
==========
Join the conversation! Other design considerations and details can be found on the pypa mailing list: https://groups.google.com/forum/#!searchin/pypa-dev/mek/pypa-dev/eaku1xvUVHU/Kbj_17sP23kJ

.. |Build Status| image:: https://travis-ci.org/mekarpeles/pypc.png
