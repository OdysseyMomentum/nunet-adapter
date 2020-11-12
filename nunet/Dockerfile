FROM ubuntu:18.04

RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y

RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN apt-get update && apt-get install -y software-properties-common postgresql-10 postgresql-client-10 postgresql-contrib-10  

# docker-compose will not let you get environment variables on build time or build args as environment variables(alas the weird code)
# setup environment variables
ARG container_name
ARG max_load_local
ARG max_load_system_test
ARG max_load_production

ENV NUNET_CONTAINER_NAME=${container_name}
ENV MAX_LOAD_LOCAL=${max_load_local}
ENV MAX_LOAD_PRODUCTION=${max_load_production}
ENV MAX_LOAD_SYSTEM_TEST=${max_load_system_test}


RUN apt-get update && apt-get install -y --no-install-recommends \
        sudo \
        git \
        build-essential \
        python3.6 \
        python3.6-dev \
        python3-pip \
        python-setuptools \
        libpq-dev\
        pgloader\
        cmake \
        wget \
        curl \
        libsm6 \
        libxext6 \
        libxrender-dev \
        vim

EXPOSE 50000

# setup postgresql
USER postgres

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host nunet_db  all    172.0.0.0/4   md5" >> /etc/postgresql/10/main/pg_hba.conf
RUN echo "host  all      all    0.0.0.0/0       reject" >> /etc/postgresql/10/main/pg_hba.conf


# And add ``listen_addresses`` to ``/etc/postgresql/10/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/10/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

USER root
COPY . /nunet-demo
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6
RUN python3 -m pip install -r /nunet-demo/requirements.txt
WORKDIR /nunet-demo
RUN chmod +x install.sh
RUN ./install.sh



# initialize database with default values
WORKDIR /nunet-demo/session_manager
RUN chmod +x start.sh 
CMD ./start.sh