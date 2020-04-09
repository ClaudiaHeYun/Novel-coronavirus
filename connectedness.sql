-- -- select number of incoming routes, country, total number of incoming passengers
-- select count(), airports.country, sum(traffic.passengers)
-- from traffic
-- join airports
-- -- incoming flights
-- on traffic.arrival_code == airports.iata
-- group by country
-- limit 10;

select *,
	(
		select airports.country
		from airports
		where airports.iata = departure_code
	) as departure_country,
	(
		select airports.country
		from airports
		where airports.iata = arrival_code
	) as arrival_country
from (
	select t.departure_code, t.arrival_code, t.passengers
	from traffic as t
	join airports as a
	on a.iata = t.departure_code
);