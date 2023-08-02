# Kameleon-II

First start:
 - create dir inventory
 - create file hosts and write
    ```text
    172.17.0.2 ansible_user=root
    ```
 - generate key value pair of ed25519 key 
 - paste pub key into dockerfile
 - private key copy to ./env/id_ed

### Dockerfile for testing

```commandline
FROM debian:stable-slim
RUN apt-get update && apt-get install -y openssh-server python3 iproute2
RUN mkdir -p /root/.ssh
RUN mkdir /var/run/sshd
RUN chown -R root:root /root/.ssh
RUN echo "ssh-ed25519 YOURKEY" >> /root/.ssh/authorized_keys
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
EXPOSE 22
RUN systemd-tmpfiles --create
CMD ["/usr/sbin/sshd","-D"]
```