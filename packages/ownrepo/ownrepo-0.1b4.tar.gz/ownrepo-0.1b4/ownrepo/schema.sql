-- Settings table
DROP TABLE IF EXISTS settings;
CREATE TABLE settings (
    key TEXT PRIMARY KEY UNIQUE NOT NULL,
    value TEXT,
    is_system INTEGER
);

-- Users table
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    name TEXT PRIMARY KEY UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Repositories table
DROP TABLE IF EXISTS repos;
CREATE TABLE repos (
    name TEXT PRIMARY KEY UNIQUE NOT NULL,
    is_public INTEGER NOT NULL
);

-- Inheritances table
DROP TABLE IF EXISTS inheritances;
CREATE TABLE inheritances (
    inherit_from TEXT NOT NULL,
    inherit_to TEXT NOT NULL,
    weight INTEGER NOT NULL,

    PRIMARY KEY (inherit_from, inherit_to),
    FOREIGN KEY (inherit_from) REFERENCES repos(name) ON DELETE CASCADE
                                                      ON UPDATE CASCADE,
    FOREIGN KEY (inherit_to) REFERENCES repos(name) ON DELETE CASCADE
                                                    ON UPDATE CASCADE
);

-- ACLs table
DROP TABLE IF EXISTS acls;
CREATE TABLE acls (
    repo TEXT NOT NULL,
    user TEXT NOT NULL,
    allow_to TEXT NOT NULL,

    PRIMARY KEY (repo, user, allow_to),
    FOREIGN KEY (repo) REFERENCES repos(name) ON DELETE CASCADE
                                              ON UPDATE CASCADE,
    FOREIGN KEY (user) REFERENCES users(name) ON DELETE CASCADE
                                              ON UPDATE CASCADE
);

-- Releases table
DROP TABLE IF EXISTS releases;
CREATE TABLE releases (
    repo TEXT NOT NULL,
    package TEXT NOT NULL,
    file TEXT NOT NULL,
    version TEXT,
    type TEXT,

    PRIMARY KEY (repo, package, file),
    FOREIGN KEY (repo) REFERENCES repos(name) ON DELETE CASCADE
                                              ON UPDATE CASCADE
);
