SELECT pg_terminate_backend(pid) from pg_stat_activity where datname='arches_arches_la';

DROP DATABASE IF EXISTS arches_arches_la;

CREATE DATABASE arches_arches_la
  WITH ENCODING='UTF8'
       OWNER=postgres
       TEMPLATE=template_postgis_20
       CONNECTION LIMIT=-1;

