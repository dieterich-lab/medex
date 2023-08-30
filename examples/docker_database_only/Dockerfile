FROM postgres:latest

# Use this postgres image to easier debug long running queries

RUN echo track_activity_query_size = 32768 >>/var/lib/postgresql/data/postgresql.conf
