DROP DATABASE {{project}}_{{branch}}_db;
CREATE DATABASE {{project}}_{{branch}}_db CHARACTER SET utf8;

GRANT ALL ON {{project}}_{{branch}}_db.* to '{{db_user}}'@'localhost';
GRANT ALL ON {{project}}_{{branch}}_db.* to '{{db_user}}'@'{{address}}';
