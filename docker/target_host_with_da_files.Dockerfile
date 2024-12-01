FROM debian:stable-slim

ENV PIP_ROOT_USER_ACTION=ignore

# Install necessary packages
RUN apt-get update && apt-get install -y openssh-server python3 python3-pip iproute2 exim4 curl

# SSH setup
RUN mkdir -p /root/.ssh && mkdir /var/run/sshd
COPY env/authorized_keys /tmp
RUN cat /tmp/authorized_keys >> /root/.ssh/authorized_keys
RUN chown -R root:root /root/.ssh
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
EXPOSE 22

# Create DirectAdmin user data simulation
RUN mkdir -p /usr/local/directadmin/data/users

# Generate random user data
RUN bash -c ' \
    user_list="user1 user2 user3 suspended_user"; \
    for user in $user_list; do \
        mkdir -p /usr/local/directadmin/data/users/$user; \
        echo "email=${user}@example.com" > /usr/local/directadmin/data/users/$user/user.conf; \
        echo "package=package$((RANDOM % 10))" >> /usr/local/directadmin/data/users/$user/user.conf; \
        echo -e "domain$((RANDOM % 10)).com\ndomain$((RANDOM % 10)).net" > /usr/local/directadmin/data/users/$user/domains.list; \
        echo "nemails=$((RANDOM % 1000))" > /usr/local/directadmin/data/users/$user/user.usage; \
        if [ "$user" = "suspended_user" ]; then \
            echo "suspended=yes" >> /usr/local/directadmin/data/users/$user/user.conf; \
            suspend_time=$(date -d "5 days ago" +%s); \
            echo "suspend_time=$suspend_time" >> /usr/local/directadmin/data/users/$user/user.conf; \
        fi \
    done'

RUN mkdir -p /usr/local/directadmin/scripts

# Mock the da command with a script that simulates `da build versions`
RUN echo '#!/bin/bash' > /usr/local/bin/da && \
    echo 'if [ "$1" == "build" ] && [ "$2" == "versions" ]; then' >> /usr/local/bin/da && \
    echo '  echo "Latest version of Apache: 2.4.62"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of Apache: 2.4.62"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of Pure-FTPd: 1.0.52"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of Pure-FTPd: 1.0.52"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of ImageMagick: 7.1.1-41"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of ImageMagick: 7.1.1-41"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of WP-CLI: 2.11.0"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of WP-CLI: 2.11.0"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of Imapsync: 2.229"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of Imapsync: 2.229"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of AWstats: 7.9"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of AWstats: 7.9"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of Dovecot: 2.3.21.1"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of Dovecot: 2.3.21.1"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of dovecot.conf: 0.4"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of dovecot.conf: 0.4"' >> /usr/local/bin/da && \
    echo '' >> /usr/local/bin/da && \
    echo '  echo "Latest version of Exim: 4.98"' >> /usr/local/bin/da && \
    echo '  echo "Installed version of Exim: 4.98"' >> /usr/local/bin/da && \
    echo '  echo "------------------------------------------------"' >> /usr/local/bin/da && \
    echo 'else' >> /usr/local/bin/da && \
    echo '  echo "Command not recognized"' >> /usr/local/bin/da && \
    echo 'fi' >> /usr/local/bin/da && \
    chmod +x /usr/local/bin/da

# Set up working directory for the agent
WORKDIR /kameleon-agent
COPY ./agent/requirements.txt .

# Install Python dependencies
RUN python3 -m pip install --break-system-packages -r requirements.txt

# Entry point for the main application
ENTRYPOINT ["python3", "main.py"]