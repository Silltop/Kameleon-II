
FROM debian:stable-slim
RUN apt-get update && apt-get install -y openssh-server python3 iproute2 exim4
RUN mkdir -p /root/.ssh
RUN mkdir /var/run/sshd
RUN chown -R root:root /root/.ssh
COPY authorized_keys /tmp
RUN cat /tmp/authorized_keys >> /root/.ssh/authorized_keys
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
EXPOSE 22
RUN systemd-tmpfiles --create
CMD ["/usr/sbin/sshd","-D"]
