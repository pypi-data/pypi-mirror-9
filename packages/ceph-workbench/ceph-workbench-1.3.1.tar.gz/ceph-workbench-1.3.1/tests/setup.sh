docker ps --all | grep -v CONTAIN | cut -f1 -d ' ' | while read c ; do docker stop $c ; docker rm $c ; done
sudo rm -fr data
mkdir data
bash -x tests/setup-redmine.sh
bash -x tests/setup-gitlab.sh
