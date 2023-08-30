#### Log into database ####
To use PostgreSQL database queries directly. First you need to create an image for PostgreSQL:
* `docker-compose up database -d` create image only for PostgreSQL (using `docker-compose up -d` create image for Medex and PostgreSQL simultaneously)

If we created the image and the image is running, we can go to medex directory and log into database using the commands:
* `docker-compose run database bash`
* `psql --host=database --username=test --dbname=example` log in to PostgreSQL
* database password - `test` (or what ever was configured in your docker compose file)

Password, username and database name can be changed in the file `./docker-compose.yml`.