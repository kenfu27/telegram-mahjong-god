FROM ubuntu:14.04
MAINTAINER Ken Fu <ken.fu@apptask.com>

RUN apt-get update

# Utilities
RUN apt-get install -y nano wget openssh-server

# Python & native libraries
RUN apt-get install -y \
    python-mysqldb \
    python2.7-dev \
    python-pip

# Python libraries
RUN pip install \
    python-telegram-bot \
    SQLAlchemy SQLAlchemy-Utils \
    tornado torndsession \
    requests

# MySQL
RUN apt-key adv --keyserver pgp.mit.edu --recv-keys 5072E1F5
RUN echo 'deb http://repo.mysql.com/apt/ubuntu trusty mysql-5.7' >> /etc/apt/sources.list
RUN apt-get update
RUN ["bash", "-c", "debconf-set-selections <<< 'mysql-community-server mysql-community-server/root-pass password root'"]
RUN ["bash", "-c", "debconf-set-selections <<< 'mysql-community-server mysql-community-server/re-root-pass password root'"]
RUN apt-get install -y mysql-community-server

# Default command
CMD service mysql restart && bash