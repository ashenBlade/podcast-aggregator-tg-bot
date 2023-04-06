begin;

alter table podcasts add column ap_podcast_id varchar null default null;

alter table tracks add column ap_track_id integer null default null;

commit;