CREATE TABLE game (
    id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    price VARCHAR(50) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE store_user (
    id INTEGER NOT NULL,
    login VARCHAR(80) NOT NULL,
    password VARCHAR(80) NOT NULL,
    purchased_game_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (login),
    FOREIGN KEY(purchased_game_id) REFERENCES game (id)
);
