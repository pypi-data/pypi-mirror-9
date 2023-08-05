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
    file TEXT UNIQUE NOT NULL,
    version TEXT,
    type TEXT,

    PRIMARY KEY (repo, package, file),
    FOREIGN KEY (repo) REFERENCES repos(name) ON DELETE CASCADE
                                              ON UPDATE CASCADE
);
