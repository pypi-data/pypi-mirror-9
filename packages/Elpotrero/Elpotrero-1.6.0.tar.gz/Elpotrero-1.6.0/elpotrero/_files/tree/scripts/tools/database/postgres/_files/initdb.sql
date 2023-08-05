CREATE USER {{db_user}} WITH PASSWORD '{{db_password}}';
ALTER USER {{db_user}} CREATEDB;

CREATE DATABASE {{project}}_{{branch}}_db;
ALTER DATABASE {{project}}_{{branch}}_db OWNER TO {{db_user}};
GRANT ALL PRIVILEGES ON DATABASE {{project}}_{{branch}}_db TO {{db_user}};
