CREATE DATABASE {{project}}_{{branch}}_db CHARACTER SET utf8;

INSERT INTO mysql.user (Host, User, Password) VALUES('localhost', '{{db_user}}', PASSWORD('{{dbpassword}}'));
FLUSH PRIVILEGES;

INSERT INTO mysql.user (Host, User, Password) VALUES('{{address}}', '{{db_user}}', PASSWORD('{{dbpassword}}'));
FLUSH PRIVILEGES;

GRANT ALL ON {{project}}_{{branch}}_db.* to '{{db_user}}'@'localhost';

GRANT ALL ON {{project}}_{{branch}}_db.* to '{{db_user}}'@'{{address}}';
