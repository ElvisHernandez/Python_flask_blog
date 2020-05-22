CREATE TABLE IF NOT EXISTS roles
(id SERIAL PRIMARY KEY,
 name VARCHAR(64) UNIQUE);

 CREATE TABLE IF NOT EXISTS users
 (id SERIAL PRIMARY KEY,
 username VARCHAR(64) UNIQUE,
 password_hash VARCHAR(128) NOT NULL,
 role_id INT REFERENCES roles (id));

--Inserting the Admin, Moderator, and user roles
 INSERT INTO roles (name) VALUES ('Admin');
 INSERT INTO roles (name) VALUES ('Moderator');
 INSERT INTO roles (name) VALUES ('User');

 --Inserting some seed data
 INSERT INTO users (username,role_id) 
 VALUES ('John',1);

 INSERT INTO users (username,role_id) 
 VALUES ('Susan',3);

 INSERT INTO users (username,role_id) 
 VALUES ('David',3);