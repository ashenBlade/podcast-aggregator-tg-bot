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