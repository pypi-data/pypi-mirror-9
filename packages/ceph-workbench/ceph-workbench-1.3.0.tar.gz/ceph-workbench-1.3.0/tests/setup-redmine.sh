set -x 
docker run --name=redmine -d -p 10080:80 -v $(pwd)/data/redmine:/home/redmine/data -v /var/run/docker.sock:/run/docker.sock -v $(which docker):/bin/docker  sameersbn/redmine:2.6.1
sleep 180
python tests/redmine-enable-rest-api.py http://127.0.0.1:10080 admin admin
