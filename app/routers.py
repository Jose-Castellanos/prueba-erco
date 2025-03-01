from typing import  List
from fastapi import APIRouter, HTTPException, Path
from pydantic import PositiveInt
from schemas import  ClientStatsResponse, InvoiceRequest, SystemLoadResponse
from services import calculate_energy_bill, calculate_single_concept, client_report, system_load_report, validate_client_id
from exceptions import BillingError
import logging

router = APIRouter(
    prefix="/api",
    tags=["Billing"],
    responses={404: {"description": "Not found"}}
)

logger = logging.getLogger(__name__)

@router.post("/calculate-invoice", response_model=dict,
    summary="Calcula la factura de energía",
    description="Este endpoint calcula la factura de energía para un cliente en un mes específico.")
async def calculate_invoice(request: InvoiceRequest):
    """
        Calcula la factura de energía.

        - **client_id**: ID del cliente.
        - **year**: Año de la factura.
        - **month**: Mes de la factura.

        **Retorna:**  
        - Un diccionario con el detalle de la factura calculada.

        **Errores posibles:**  
        - 400: Datos inválidos  
        - 500: Error interno en el cálculo  
    """
    try:
        result = calculate_energy_bill(request.client_id, request.year, request.month)
        logger.info(f"Calculated invoice for client {request.client_id}")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to calculate invoice: {e}")
        raise BillingError(detail=str(e))


@router.get("/client-statistics/{client_id}", response_model=List[ClientStatsResponse])
async def client_statistics(client_id: int):
    """
        Obtiene las estadísticas de consumo de un cliente.

        - **client_id**: ID del cliente.

        **Retorna:**  
        - Una lista con las estadísticas de consumo por mes del cliente.

        **Errores posibles:**  
        - 400: Datos inválidos
    """
    try:

        # Implement statistics logic
        logger.info(f"Fetching statistics for client {client_id}")
        result = client_report(client_id) 
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to fetch statistics: {e}")
        raise BillingError(detail=str(e))
    

@router.get("/system-load", response_model=List[SystemLoadResponse])
async def system_load():

    """
        Obtiene la carga del sistema.
        **Retorna:**
        - Una lista con la carga del sistema por hora.
    """
    try:
        # Implement system load logic
        logger.info("Fetching system load data")
        result= system_load_report()
        return result
    except Exception as e:
        logger.error(f"Failed to fetch system load: {e}")
        raise BillingError(detail=str(e))

@router.get("/calculate/{concept}/{client_id}/{year}/{month}")
async def calculate_concept(concept: str,
    client_id: PositiveInt,
    year: int = Path(..., ge=2000, le=2100),
    month: int = Path(..., ge=1, le=12)):
    """
    Calcula un concepto de energía específico para un cliente en un mes determinado.

    - **concept**: Concepto a calcular ('ea', 'ec', 'ee1', 'ee2').
    - **client_id**: ID del cliente.
    - **year**: Año del cálculo.
    - **month**: Mes del cálculo.

    **Retorna:**  
    - Un diccionario con la cantidad y costo del concepto calculado.

    **Errores posibles:**  
    - 400: Concepto inválido o datos inválidos  
    - 404: Cliente no encontrado  
    - 500: Error interno en el cálculo  
    """
    try:
        concepts = {
            "ea": "Energia_Activa",
            "ee1": "Excedentes_Energia_1",
            "ee2": "Excedentes_Energia_2",
            "ee": "Excedentes_Energia"
        }
        if concept.lower() not in concepts:
            raise BillingError(detail="Invalid concept")
        result = calculate_single_concept(client_id, year, month, concept)
        logger.info(f"Calculated {concept} for client {client_id}")
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to calculate {concept}: {e}")
        raise BillingError(detail=str(e))
