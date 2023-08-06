set -e 
DATA=$(pwd)/data
for i in gitlab mysql redis ; do docker stop $i || true ; docker rm $i || true ; done
mkdir -p $DATA
docker run --name=redis -d sameersbn/redis:latest
sudo rm -fr $DATA/mysql
mkdir -p $DATA/mysql
docker run --name=mysql -d -e 'DB_NAME=gitlabhq_production' -e 'DB_USER=gitlab' -e 'DB_PASS=Wrobyak4' -v $DATA/mysql/data:/var/lib/mysql sameersbn/mysql:latest
sudo rm -fr $DATA/gitlab
mkdir -p $DATA/gitlab
docker run --name='gitlab' -it -d  --link mysql:mysql --link redis:redisio -e 'GITLAB_SIGNUP=true' -e 'GITLAB_PORT=80' -e 'GITLAB_HOST=localhost' -e 'GITLAB_SSH_PORT=2222' -p 2222:22 -p 8181:80 -v /var/run/docker.sock:/run/docker.sock -v $DATA/gitlab/data:/home/git/data -v $(which docker):/bin/docker sameersbn/gitlab:7.7.2
sleep 180 # generating assets takes a long time
