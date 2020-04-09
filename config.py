import os

user = os.environ['POSTGRES_USER']
password = os.environ['POSTGRES_PASSWORD']
host = os.environ['POSTGRES_HOST']
database = os.environ['POSTGRES_DATABASE']
port = os.environ['POSTGRES_PORT']

DATABASE_CONNECTION_URI = f'postgresql://{user}:{password}@{host}:{port}/{database}'