ceph-workbench
==============

ceph-workbench is a command line tool that implements a development
workflow for `Ceph <http://ceph.com>`_

Home page : https://pypi.python.org/pypi/ceph-workbench

Hacking
=======

* Get the code : git clone http://workbench.dachary.org/dachary/ceph-workbench.git
* Run the tests : tox
* Tag a version

 - edit the version field of setup.cfg
 - git tag -a -m 'whatever' 2.1.1
 - git push --tags

* Check the documentation : rst2html < README.rst > /tmp/a.html
* Publish

 - python setup.py register
 - python setup.py sdist upload --sign
 - trim old versions at https://pypi.python.org/pypi/ceph-workbench
