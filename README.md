# Kameleon-II

#### Preparation:
 - create file hosts file inside inventory directory and put your hosts ip there </br>
   example:
    ```text
    172.17.0.2 ansible_user=root
    ```
 - generate key value pair of ed25519 key 
 - paste pub key to authorized_keys file inside ./env directory
 - private key copy to ./env/id_ed

#### Development Environment
To start development environment first build docker files:
```commandline
docker-compose -f docker-compose.yaml build
```
Start environment
```commandline
docker-compose -f docker-compose.yaml up
```
now you will see container logs in stdout.

You can access application by opening </br>
<a>http:127.0.0.1:5000</a>