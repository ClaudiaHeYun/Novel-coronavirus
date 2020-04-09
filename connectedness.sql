-- -- select number of incoming routes, country, total number of incoming passengers
-- select count(), airports.country, sum(traffic.passengers)
-- from traffic
-- join airports
-- -- incoming flights
-- on traffic.arrival_code == airports.iata
-- group by country
-- limit 10;
select count(), sum(connections.passengers), connections.arrival_country, case_data.population, sum(case_data.confirmed), case_data.date
from (
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
	)
 ) as connections
join (
	select ca.date, ca.country, ca.confirmed, co.population
	from cases as ca
	join countries as co
	on ca.country = co.name
) as case_data
on case_data.country = connections.departure_country
group by connections.arrival_country;