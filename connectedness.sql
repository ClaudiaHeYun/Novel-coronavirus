-- select number of incoming routes, country, total number of incoming passengers
select count(), airports.country, sum(traffic.passengers)
from traffic
join airports
-- incoming flights
on traffic.arrival_code == airports.iata
group by country
limit 10;