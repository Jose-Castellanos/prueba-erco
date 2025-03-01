COPY xm_data_hourly_per_agent(record_timestamp, value) FROM '/pt-data/xm_data_hourly_per_agent.csv' DELIMITER ',' CSV HEADER;

ALTER TABLE records DISABLE TRIGGER ALL;

COPY records(id_record, id_service,record_timestamp) FROM '/pt-data/records.csv' DELIMITER ',' CSV HEADER;

ALTER TABLE records ENABLE TRIGGER ALL;

COPY injection(id_record, value) FROM '/pt-data/injection.csv' DELIMITER ',' CSV HEADER;

COPY consumption(id_record, value) FROM '/pt-data/consumption.csv' DELIMITER ',' CSV HEADER;

COPY services(id_service, id_market, cdi, voltage_level) FROM '/pt-data/services.csv' DELIMITER ',' CSV HEADER;

COPY tariffs(id_market,voltage_level,cdi,G,T,D,R,C,P,CU) FROM '/pt-data/tariffs.csv' DELIMITER ',' CSV HEADER;
