create table podcasts(
    id integer primary key autoincrement,
    name varchar not null,
    yc_album_id integer
);

create unique index PODCASTS_YC_ALBUM_ID on podcasts(yc_album_id);

create table tracks(
    id integer primary key autoincrement,
    podcast_id integer references podcasts(id) not null,
    tg_message_id integer not null,
    publish_date timestamp not null,
    yc_track_id integer
);

create unique index TRACKS_TG_MESSAGE_ID on tracks(tg_message_id);
create unique index TRACKS_YC_TRACK_ID on tracks(yc_track_id);

create table podcast_tag(
    podcast_id integer references podcasts(id) not null,
    tag_id integer references tags(id) not null,
    primary key (podcast_id, tag_id)
);

create table tags(
    id integer primary key autoincrement,
    tag varchar not null unique
);
