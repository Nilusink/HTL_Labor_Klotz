create table customer_data
(
    id          int auto_increment
        primary key,
    salutation  varchar(32)  not null,
    first_name  varchar(255) not null,
    last_name   varchar(255) not null,
    birthday    date         not null,
    street      varchar(255) not null,
    postal_code int          not null,
    city        varchar(255) not null,
    email       varchar(255) not null
);
