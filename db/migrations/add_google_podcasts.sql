begin;

alter table podcasts add column gp_feed_id varchar;

alter table tracks add column gp_episode_id varchar;

commit;