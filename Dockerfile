FROM ubuntu:19.10
MAINTAINER I <idankash@gmail.com>

RUN apt-get update && apt-get install -y apache2 python3 python3-pip && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV APACHE_RUN_USER  www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR   /var/log/apache2
ENV APACHE_PID_FILE  /var/run/apache2/apache2.pid
ENV APACHE_RUN_DIR   /var/run/apache2
ENV APACHE_LOCK_DIR  /var/lock/apache2
ENV APACHE_LOG_DIR   /var/log/apache2
RUN mkdir -p $APACHE_RUN_DIR
RUN mkdir -p $APACHE_LOCK_DIR
RUN mkdir -p $APACHE_LOG_DIR


COPY chess_engine_client /root/client
COPY chess_engine_server /root/server
COPY startup.sh /root/startup.sh

RUN /usr/bin/pip3 install -r /root/server/requirements.txt
RUN cp -a /root/client/. /var/www/
RUN chmod 770 /root/client
RUN chmod 770 /root/server
RUN chmod +x /root/startup.sh

EXPOSE 80
WORKDIR /root
ENTRYPOINT /root/startup.sh
