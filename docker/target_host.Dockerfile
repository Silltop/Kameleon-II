
FROM debian:stable-slim
ENV PIP_ROOT_USER_ACTION=ignore
RUN apt-get update && apt-get install -y openssh-server python3 python3-pip iproute2 exim4
RUN mkdir -p /root/.ssh
RUN mkdir /var/run/sshd
RUN chown -R root:root /root/.ssh
COPY env/authorized_keys /tmp
RUN cat /tmp/authorized_keys >> /root/.ssh/authorized_keys
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
EXPOSE 22
RUN systemd-tmpfiles --create
WORKDIR /kameleon-agent
COPY ./agent/requirements.txt .
RUN python3 -m pip install --break-system-packages -r requirements.txt
ENTRYPOINT ["python3", "main.py"]