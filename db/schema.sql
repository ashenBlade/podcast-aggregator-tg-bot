create table podcasts(
    id integer primary key autoincrement,
    name varchar not null,
    description varchar not null
);

create table yandex_music_providers(
    podcast_id integer references podcasts(id) not null,
    album integer not null,
    primary key (podcast_id, album)
);


create table podcast_tag(
    podcast_id integer references podcasts(id) not null,
    tag_id integer references tags(id) not null,
    primary key (podcast_id, tag_id)
);

create table tags(
    id integer primary key autoincrement,
    tag varchar not null unique
);

insert into tags(tag)
values
    ('frontend'),
    ('backend'),
    ('mobile'),
    ('devops'),
    ('network'),
    ('fullstack'),
    ('web');
