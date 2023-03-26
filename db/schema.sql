create table podcasts(
    id integer primary key autoincrement,
    name varchar not null,
    yc_album_id integer
);

create table yandex_music_published_tracks(
    track_id integer primary key,
    published_time timestamp not null
);

create index YANDEX_MUSIC_PUBLISHED_TRACKS_IDX on yandex_music_published_tracks(track_id);

create table podcast_tag(
    podcast_id integer references podcasts(id) not null,
    tag_id integer references tags(id) not null,
    primary key (podcast_id, tag_id)
);

create table tags(
    id integer primary key autoincrement,
    tag varchar not null unique
);
