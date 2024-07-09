## Unique number generator

This is the unique number generator using redis and so for installing redis please run the below commands

!curl -fsSL https://packages.redis.io/redis-stack/redis-stack-server-6.2.6-v7.focal.x86_64.tar.gz -o redis-stack-server.tar.gz 

!tar -xvf redis-stack-server.tar.gz

!pip install redis

!pip install gunicorn

!pip install flask

!./redis-stack-server-6.2.6-v7/bin/redis-stack-server --daemonize yes


Run the below command

python microservice.py

## Docker build
docker build -t sample-microservice .

## Docker run
docker run -p 5000:5000 sample-microservice

## Apply Kubernettes configuration
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

## Access microservice

kubectl get service sample-microservice-service





