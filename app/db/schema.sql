-- Role Model
CREATE TABLE IF NOT EXISTS roles
(id SERIAL PRIMARY KEY,
 name VARCHAR(64) UNIQUE,
 "default" BOOLEAN DEFAULT FALSE,
 permissions INT DEFAULT 0
 );

 CREATE INDEX default_idx ON roles ("default");

-- Inserting the Admin, Moderator, and user roles
-- Roles have different permissions which are designated
-- in increasing powers of two.
-- Permissions: FOLLOW | COMMENT | WRITE | MODERATE | ADMIN
-- Values:         1   |    2    |   4   |    8     |  16
 INSERT INTO roles (name,permissions) VALUES ('Admin',1+2+4+8+16);
 INSERT INTO roles (name,permissions) VALUES ('Moderator',1+2+4+8);
 INSERT INTO roles (name,"default",permissions) VALUES ('User',TRUE,1+2+4);
 
 -- User Model
 CREATE TABLE IF NOT EXISTS users
 (id SERIAL PRIMARY KEY,
 email VARCHAR(64) UNIQUE,
 username VARCHAR(64) UNIQUE,
 password_hash VARCHAR(128) NOT NULL,
 confirmed BOOLEAN DEFAULT FALSE,
 name VARCHAR(64),
 location VARCHAR(64),
 about_me TEXT,
 member_since DATE NOT NULL DEFAULT CURRENT_DATE,
 last_seen TIMESTAMP NOT NULL DEFAULT now(),
 avatar_hash VARCHAR(32),
 role_id INT REFERENCES roles (id));

 CREATE UNIQUE INDEX user_username_ci_idx ON users (lower(username));
 CREATE UNIQUE INDEX user_email_ci_idx ON users (lower(email));

-- Blog Post Model
CREATE TABLE IF NOT EXISTS posts 
(id SERIAL PRIMARY KEY,
body TEXT,
body_html TEXT,
time_stamp TIMESTAMP NOT NULL DEFAULT now(),
author_id INT REFERENCES users (id) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS follow 
(follower_id INT REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE,
followed_id INT REFERENCES users (id) ON UPDATE CASCADE ON DELETE CASCADE,
time_stamp TIMESTAMP NOT NULL DEFAULT now(),
CONSTRAINT follow_pkey PRIMARY KEY (follower_id,followed_id));

