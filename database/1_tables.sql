
CREATE TABLE xm_data_hourly_per_agent (
    value FLOAT,
    record_timestamp TIMESTAMP,
    unique(record_timestamp) 
);

CREATE TABLE records (
    id_record SERIAL PRIMARY KEY,
    id_service INTEGER,
    record_timestamp TIMESTAMP,
    FOREIGN KEY (record_timestamp) REFERENCES xm_data_hourly_per_agent(record_timestamp)	
);

CREATE TABLE injection (
    id_record INTEGER,
    value FLOAT,
    FOREIGN KEY (id_record) REFERENCES records(id_record)
);

CREATE TABLE consumption (
    id_record iNTEGER,
    value FLOAT,
    FOREIGN KEY (id_record) REFERENCES records(id_record)
);


create table services(
	id_service SERIAL primary key,
	id_market Integer,
	cdi Integer,
	voltage_level integer,
	unique(id_market),
	unique(cdi),
	unique(voltage_level)
);

ALTER TABLE records 
ADD CONSTRAINT fk_records_service 
FOREIGN KEY (id_service) REFERENCES services(id_service);

CREATE TABLE tariffs (
    id_market INTEGER NOT NULL,
    voltage_level INTEGER NOT NULL,
    cdi INTEGER,  -- Can be null, as specified
    G FLOAT,
    T FLOAT,
    D FLOAT,
    R FLOAT,
    C FLOAT,
    P FLOAT,
    CU FLOAT,
    FOREIGN KEY (id_market) REFERENCES services(id_market),
    FOREIGN KEY (cdi) REFERENCES services(cdi),
    FOREIGN KEY (voltage_level) REFERENCES services(voltage_level)
);



