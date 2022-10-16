drop table if exists uploads;
create table uploads (
  id integer primary key autoincrement,
  title text not null,
  filePath text not null,
  userId integer not null
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null,
  uPass text not null
);