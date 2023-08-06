FROM tutum/curl
MAINTAINER Tutum <info@tutum.co>

RUN apt-get update && \
    apt-get install -y python python-dev python-pip libyaml-dev
ADD . /app
RUN export SDK_VER=$(cat /app/requirements.txt | grep python-tutum | grep -o '[0-9.]*') && \
    curl -0L https://github.com/tutumcloud/python-tutum/archive/${SDK_VER}.tar.gz | tar -zxv && \
    pip install python-tutum-${SDK_VER}/. && \
    pip install /app && \
    rm -rf /app python-tutum-${SDK_VER} && \
    tutum -v

ENTRYPOINT ["tutum"]
