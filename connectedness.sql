-- TODO: I'm not great at SQL so I'm not totally sure if this does what we want
select
	count(),
	sum(connections.passengers),
	connections.arrival_country,
	group_concat(case_data.country, ","),
	group_concat(case_data.population, ","),
	group_concat(case_data.confirmed, ","),
	case_data.date
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