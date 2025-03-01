from fastapi import HTTPException

from exceptions import BillingError, ClientNotFoundError
from schemas import ClientStatsResponse, SystemLoadResponse
from database import db
import logging
from datetime import datetime
from typing import Dict, List, Optional
from starlette import status

logger = logging.getLogger(__name__)

def calculate_energy_bill(client_id: int, year: int, month: int) -> Dict[str, float]:
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            start_date = datetime(year, month, 1)
            end_date = verify_end_date(year, month)
            if validate_client_id(client_id, cur):
                energy_active = calculate_energy_active(client_id, start_date, end_date, cur)
                total_consumption = energy_active["total_consumption"]
                total_concept_energy_active = energy_active["total_concept"]
                commercialization_energy = commercialization_energy_surplus(client_id, start_date, end_date, cur)
                total_injection = commercialization_energy["total_injection"]
                ee1_quantity = min(total_consumption, total_injection)
                ee1_cost = ee1_quantity * (energy_active["cu"] * -1)
                ee2_quantity = calculate_ee2(total_injection,total_consumption)
                ee_2_cost_total= calculate_tarif_ee2(client_id, start_date, end_date, cur, ee2_quantity, total_consumption)

                return {
                    "Energia_Activa": float(total_concept_energy_active),
                    "Excedentes_Energia": float(commercialization_energy["total_concept"]),
                    "Excedentes_Energia_1": float(ee1_cost),
                    "Excedentes_Energia_2": float(ee_2_cost_total)
                }
    except Exception as e:
        logger.error(f"Error calculating bill for client {client_id}: {e}")
        raise

def verify_end_date(year: int, month: int) -> datetime:
    if month == 12:
        return datetime(year + 1, 1, 1)
    else:
        return datetime(year, month + 1, 1)

def validate_client_id(client_id: int, cursor) -> bool:
    cursor.execute("SELECT EXISTS(SELECT 1 FROM services WHERE id_market = %s)", (client_id,))
    exists = cursor.fetchone()[0]
    if not exists:
        logger.error(f"Invalid client_id: {client_id}")
        raise ClientNotFoundError()
    return True

def calculate_energy_active(client_id: int, start_date: datetime, end_date: datetime, cur) -> dict[str, float]:
    cur.execute("""
                select
                    SUM(c.value) as total_consumption,
                    t.cu,
                    SUM(c.value)* t.cu as total_concept
                from
                    consumption c
                join records r on
                    c.id_record = r.id_record
                join services s on
                    r.id_service = s.id_service
                join tariffs t on
                    s.id_market = t.id_market
                    and s.voltage_level = t.voltage_level
                    and (s.cdi = t.cdi
                        or t.cdi is null)
                where
                    s.id_market = %s
                    and r.record_timestamp >= %s
                    and r.record_timestamp < %s
                group by
                    t.cu;
                """, ( client_id,start_date, end_date))

    total_consumption = cur.fetchone()
    return {
        "total_consumption": total_consumption[0] if total_consumption else 0,
        "cu": total_consumption[1] if total_consumption else 0,
        "total_concept": total_consumption[2] if total_consumption else 0
    }

def commercialization_energy_surplus(client_id: int, start_date: datetime, end_date: datetime, cur) ->  dict[str, float]:
    cur.execute("""
                select
                    SUM(i.value),
                    t.C,
                    SUM(i.value) * t.C as total_concept
                from
                    injection i
                join records r on
                    i.id_record = r.id_record
                join services s on
                    r.id_service = s.id_service
                join tariffs t on
                    s.id_market = t.id_market
                    and (s.cdi = t.cdi
                        or t.cdi is null)
                    and s.voltage_level = t.voltage_level
                where
                    s.id_market = %s
                    and r.record_timestamp >= %s
                    and r.record_timestamp < %s
                group by
                    t.C;
                 """, ( client_id,start_date, end_date))
    total_injection = cur.fetchone()
    return {
        "total_injection": total_injection[0] if total_injection else 0,
        "c": total_injection[1] if total_injection else 0,
        "total_concept": total_injection[2] if total_injection else 0
    }

def calculate_ee2(total_injection,total_consumption) -> float:
    if total_injection > total_consumption:
        ee2_quantity = total_injection - total_consumption
    elif total_injection <= total_consumption:
        ee2_quantity = 0
    return ee2_quantity

def calculate_tarif_ee2(client_id: int, start_date: datetime, end_date: datetime, cur, ee2_quantity: float, ea_total: float) -> float:

    cur.execute(
        """
            SELECT records.record_timestamp, consumption.value AS cons, injection.value AS inj, 
                   xm_data_hourly_per_agent.value AS hourly_tariff
            FROM records
            LEFT JOIN consumption ON records.id_record = consumption.id_record
            LEFT JOIN injection ON records.id_record = injection.id_record
            JOIN services ON records.id_service = services.id_service
            JOIN xm_data_hourly_per_agent ON records.record_timestamp = xm_data_hourly_per_agent.record_timestamp
            WHERE services.id_market = %s 
                  AND records.record_timestamp >= %s 
                  AND records.record_timestamp < %s
            ORDER BY records.record_timestamp
        """, (client_id, start_date, end_date,))
    hourly_data = cur.fetchall()
    if not hourly_data or ee2_quantity == 0:
            ee2_cost = 0.0
    else:
            cumulative_injection = 0.0
            ee2_cost_total = 0.0
            cumulative_excess = 0.0
            for timestamp, cons, inj, hourly_tariff in hourly_data:
                cumulative_injection += float(inj or 0)
                if cumulative_injection > ea_total:
                    excess = max(0,cumulative_injection - ea_total - cumulative_excess)
                    cumulative_excess += excess
                    ee2_cost_total += excess * float(hourly_tariff or 0)
            ee2_cost = ee2_cost_total
    return ee2_cost

def client_report(client_id: int) -> List[ClientStatsResponse]:
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            if validate_client_id(client_id, cur):
                cur.execute("""
                            SELECT 
                                TO_CHAR(DATE_TRUNC('month', records.record_timestamp), 'YYYY-MM') AS month,
                                COALESCE(SUM(consumption.value), 0) AS total_consumption,
                                COALESCE(SUM(injection.value), 0) AS total_injection
                            FROM records
                            LEFT JOIN consumption ON records.id_record = consumption.id_record
                            LEFT JOIN injection ON records.id_record = injection.id_record
                            JOIN services ON records.id_service = services.id_service
                            WHERE services.id_market = %s
                            GROUP BY DATE_TRUNC('month', records.record_timestamp)
                            ORDER BY month
                        """, (client_id,))
                        
                stats = cur.fetchall()

                if not stats:
                    logger.warning(f"No statistics found for client {client_id}")
                    return []  # Return empty list if no data
                        
                    # Convert to response model
                result = [
                            ClientStatsResponse(
                                month=row[0],
                                total_consumption=float(row[1]),
                                total_injection=float(row[2])
                            )
                            for row in stats
                        ]
                return result
    except Exception as e:
        logger.error(f"Error report for client {client_id}: {e}")
        raise

def system_load_report() -> List[SystemLoadResponse]:
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        SELECT 
                            DATE_TRUNC('hour', records.record_timestamp) AS timestamp,
                            COALESCE(SUM(consumption.value), 0) AS hourly_load
                        FROM records
                        JOIN consumption ON records.id_record = consumption.id_record
                        GROUP BY DATE_TRUNC('hour', records.record_timestamp)
                        ORDER BY timestamp
                    """)
            stats = cur.fetchall()
            if not stats:
                logger.warning("No system load data found")
                return []  # Return empty list if no data
            result = [
                {
                    "timestamp": row[0],
                    "hourly_load": float(row[1])
                }
                for row in stats
            ]
            return result
    except Exception as e:
        logger.error(f"Error fetching system load data: {e}")
        raise

def calculate_single_concept(client_id: int, year: int, month: int, concept: str) -> dict[str, float]:
    try:
        with db.get_connection() as conn:
            cur = conn.cursor()
            start_date = datetime(year, month, 1)
            end_date = verify_end_date(year, month)
            if validate_client_id(client_id, cur):
                energy_active = calculate_energy_active(client_id, start_date, end_date, cur)
                total_consumption = energy_active["total_consumption"]
                total_concept_energy_active = energy_active["total_concept"]
                commercialization_energy = commercialization_energy_surplus(client_id, start_date, end_date, cur)
                total_injection = commercialization_energy["total_injection"]

                ee2_quantity = calculate_ee2(total_injection,total_consumption)
                if concept.lower() == "ea":     
                    return {
                    "Costo energia activa":float(total_concept_energy_active)
                }
                elif concept.lower() == "ee1":
                    ee1_quantity = min(total_consumption, total_injection)
                    return {
                    "Costo excedentes energia 1": float(ee1_quantity * (energy_active["cu"] * -1))
                    }
                elif concept.lower() == "ee2":
                    concept_ee2 = calculate_tarif_ee2(client_id, start_date, end_date, cur, ee2_quantity, total_consumption)
                    return {
                        "Costo excedentes energia 2": float(concept_ee2)}
                elif concept.lower() == "ee":
                    ee_concept =commercialization_energy["total_concept"]
                    return {
                    "Costo excedentes energia": float(ee_concept)
                    }
                
    except Exception as e:
        logger.error(f"Error calculating concept {concept} for client {client_id}: {e}")
        raise
