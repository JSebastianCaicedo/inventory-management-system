CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL
);

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre TEXT,
    sku TEXT UNIQUE,
    unidad TEXT
);

CREATE TABLE inventario (
    id SERIAL PRIMARY KEY,
    producto_id INT REFERENCES productos(id),
    cantidad NUMERIC
);