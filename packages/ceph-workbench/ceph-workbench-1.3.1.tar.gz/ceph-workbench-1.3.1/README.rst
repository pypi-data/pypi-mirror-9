ceph-workbench
==============

ceph-workbench is a command line tool that implements a development
workflow for `Ceph <http://ceph.com>`_

Home page : https://pypi.python.org/pypi/ceph-workbench

Hacking
=======

* Get the code : git clone http://workbench.dachary.org/dachary/ceph-workbench.git
* Run the tests : tox
* Check the documentation : rst2html < README.rst > /tmp/a.html
* Prepare a new version

 - version=1.3.0 ; perl -pi -e "s/^version.*/version = $version/" setup.cfg ; for i in 1 2 ; do python setup.py sdist ; amend=$(git log -1 --oneline | grep --quiet "version $version" && echo --amend) ; git commit $amend -m "version $version" ChangeLog setup.cfg ; git tag -a -f -m "version $version" $version ; done

* Publish a new version

 - python setup.py sdist upload --sign
 - git push ; git push --tags

* pypi maintenance

 - python setup.py register # if the project does not yet exist
 - trim old versions at https://pypi.python.org/pypi/ceph-workbench
