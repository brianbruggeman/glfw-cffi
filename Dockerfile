FROM ubuntu
MAINTAINER Brian Bruggeman <brian.m.bruggeman@gmail.com>

ENV PROJECT glfw-cffi
ENV PROJECT_HOME /opt/$PROJECT/
ENV WORKON_HOME /root/.local/envs
ENV GLFW_VERSION 3.2.1
ENV DISPLAY :99.0
ENV GLFW_LIBRARY /root/lib/libglfw.so

COPY ./ $PROJECT_HOME

RUN $PROJECT_HOME/bootstrap-ubuntu.sh

RUN vex -m $PROJECT /bin/bash -c 'cd $PROJECT_HOME && pip install -e .[tests]'
RUN vex $PROJECT /bin/bash -c 'cd $PROJECT_HOME && pip install circus'

CMD vex $PROJECT /bin/bash -c 'cd $PROJECT_HOME && circusd circus-startup-xvfb.ini --daemon && py.test'
