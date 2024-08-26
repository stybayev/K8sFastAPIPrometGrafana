CREATE SCHEMA IF NOT EXISTS content;
ALTER SCHEMA content OWNER TO postgres;

CREATE TABLE IF NOT EXISTS content.films (
    movie_id uuid NOT NULL
);

CREATE TABLE IF NOT EXISTS content.likes (
    user_id uuid NOT NULL,
    movie_id uuid NOT NULL,
    likes smallint NOT NULL
);

CREATE TABLE IF NOT EXISTS content.users (
    user_id uuid NOT NULL
);

COPY content.films FROM '/data/movies.csv' DELIMITER ',' CSV HEADER;
COPY content.users FROM '/data/users.csv' DELIMITER ',' CSV HEADER;
COPY content.likes FROM '/data/likes.csv' DELIMITER ',' CSV HEADER;

CREATE INDEX IF NOT EXISTS idx_user_id ON content.likes(user_id);
CREATE INDEX IF NOT EXISTS idx_movie_id ON content.likes(movie_id);
CREATE INDEX IF NOT EXISTS idx_likes ON content.likes(likes);