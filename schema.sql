CREATE TABLE categories (
    id serial PRIMARY KEY,
    category text NOT NULL UNIQUE
);

CREATE TABLE contacts (
    id serial PRIMARY KEY,
    name text NOT NULL,
    phone varchar(15),
    email text,
    category_id integer NOT NULL REFERENCES categories (id) ON DELETE CASCADE
);