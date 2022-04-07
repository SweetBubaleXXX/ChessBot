create table if not exists users (
    id INT PRIMARY KEY NOT NULL,
    username VARCHAR(33) NOT NULL,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0
);