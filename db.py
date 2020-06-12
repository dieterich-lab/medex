import psycopg2.extras
from flask import  g
import os

user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DB']
port = os.environ['POSTGRES_PORT']
DATABASE_URL=f'postgresql://{user}:{password}@{host}:{port}/{database}'

db = psycopg2.connect(DATABASE_URL)
