import os


def get_database_url():
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASSWORD']
    host = os.environ['POSTGRES_HOST']
    database = os.environ['POSTGRES_DB']
    port = os.environ['POSTGRES_PORT']
    url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    print(f"Database URL: {url}")
    return url
