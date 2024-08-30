from postgres:14

RUN mkdir /data
ADD init.sql /docker-entrypoint-initdb.d
RUN chmod a+r /docker-entrypoint-initdb.d/*
COPY *.sql /docker-entrypoint-initdb.d/
COPY *.csv /data/
