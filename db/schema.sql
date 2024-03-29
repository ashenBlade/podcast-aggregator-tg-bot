begin;
create table podcasts(
    id integer primary key autoincrement,
    name varchar not null,
    yc_album_id integer,
    gp_feed_id varchar null,
    ap_podcast_id varchar
);

create unique index PODCASTS_YC_ALBUM_ID on podcasts(yc_album_id);
create unique index PODCASTS_GP_FEED_ID on podcasts(gp_feed_id);
create unique index PODCASTS_AP_PODCAST_ID on podcasts(ap_podcast_id);

create table tracks(
    id integer primary key autoincrement,
    podcast_id integer references podcasts(id) not null,
    tg_message_id integer not null,
    publish_date timestamp not null,
    yc_track_id integer,
    ap_track_id integer null,
    gp_episode_id varchar
);

create unique index TRACKS_TG_MESSAGE_ID on tracks(tg_message_id);
create unique index TRACKS_YC_TRACK_ID on tracks(yc_track_id);
create unique index TRACKS_GP_EPISODE_ID on tracks(gp_episode_id);
create unique index TRACKS_AP_TRACK_ID on tracks(ap_track_id);
commit;