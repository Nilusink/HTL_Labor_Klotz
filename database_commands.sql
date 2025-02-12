create table customer_data
(
    id          int auto_increment
        primary key,
    salutation  varchar(32)  not null,
    first_name  varchar(255) not null,
    last_name   varchar(255) not null,
    birthday    date,
    street      varchar(255),
    postal_code int,
    city        varchar(255),
    email       varchar(255)
);
