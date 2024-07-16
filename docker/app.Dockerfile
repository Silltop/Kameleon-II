FROM debian:stable-slim
ENV PIP_ROOT_USER_ACTION=ignore
RUN apt-get update && apt-get install -y openssh-server python3 python3-pip iproute2 net-tools curl ansible
RUN mkdir /kameleon
RUN mkdir /kameleon/tmp
WORKDIR /kameleon
COPY ./requirements.txt .
RUN python3 -m pip install --break-system-packages -r requirements.txt
ENTRYPOINT ["python3", "main.py"]
