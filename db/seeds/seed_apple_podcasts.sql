begin;

create table apple_podcasts_temp
(
    podcast_id integer,
    apple_podcast_id varchar
);

insert into apple_podcasts_temp(podcast_id, apple_podcast_id)
values
    (1, 'id1209828744'),  -- Podlodka Podcast
    (2, 'id890468606'),   -- SDCast
    (3, 'id1492086611'),  -- Войти в IT
    (4, 'id1449804780'),  -- АйТиБорода
    (5, 'id1466243923'),  -- Сушите вёсла
    (6, 'id256504435'),   -- Радио-Т
    (7, 'id526797445'),   -- Развлекательный IT-подкаст «Радиома»
    (8, 'id1488527416'),  -- ПИЛИМ, ТРЁМ
    (9, 'id1488945593'),  -- Запуск Завтра
    (10, 'id1436711112'); -- ForGeeks Podcast

update podcasts
set ap_podcast_id = (
    select apple_podcast_id
    from apple_podcasts_temp
    where podcast_id = podcasts.id
)
-- keep linter quiet
where exists(
    select 1
    from apple_podcasts_temp
    where podcast_id = podcasts.id
);

drop table apple_podcasts_temp;

commit;