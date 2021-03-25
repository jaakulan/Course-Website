CREATE TABLE accounts (
    password TEXT,
    username TEXT,
    utorid text,
    instructor boolean,
    primary key(utorid)
);
CREATE TABLE marks (
    utorid text,
    a1 integer,
    a2 integer,
    a3 integer,
    midterm integer,
    final integer,
    lab integer,
    foreign key(utorid) references accounts(utorid)
);
CREATE TABLE remarks (
    utorid text,
    reason text,
    a1 boolean,
    a2 boolean,
    a3 boolean,
    midterm boolean,
    lab boolean,
    final boolean,
    foreign key(utorid) references accounts(utorid)
);
CREATE TABLE feedback (
    instructorid text,
    likeinstructor text,
    improveinstructor text,
    likelabs text,
    improvelabs text,
    foreign key(instructorid) references accounts(utorid)
);
