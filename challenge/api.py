from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
import pandas as pd
from datetime import datetime
from .model import DelayModel

app = FastAPI()

# Initialize the model
model = DelayModel()

class FlightData(BaseModel):    
    OPERA: str
    TIPOVUELO: str
    MES: int = Field(..., ge=1, le=12)  # Esto asegura que el mes esté entre 1 y 12
    Fecha_I: str = "2017-01-01 00:00:00"
    Fecha_O: str = "2017-01-01 00:15:00"

    @field_validator('Fecha_I', 'Fecha_O')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError('Incorrect date format, should be YYYY-MM-DD HH:MM:SS')
        return v


    @field_validator('MES')
    def validate_mes(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('MES must be between 1 and 12')
        return v

    @field_validator('TIPOVUELO')
    def validate_tipovuelo(cls, v):
        if v not in ['I', 'N']:
            raise ValueError('TIPOVUELO must be "I" or "N"')
        return v

    @field_validator('OPERA')
    def validate_opera(cls, v):
        valid_airlines = [
            'Grupo LATAM', 'Sky Airline', 'Copa Air', 'Latin American Wings',
            'Aerolineas Argentinas'
        ]
        if v not in valid_airlines:
            raise ValueError(f'OPERA must be one of {valid_airlines}')
        return v

class FlightDataList(BaseModel):
    flights: List[FlightData]

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }


@app.post("/predict", status_code=200)
async def post_predict(flight_data_list: FlightDataList) -> dict:
    if model._model is None:
        raise HTTPException(status_code=500, detail="Model not loaded or trained.")

    try:
        # Convert the list of FlightData to a DataFrame
        data = pd.DataFrame([flight.dict() for flight in flight_data_list.flights])

        # Preprocess the data
        features = model.preprocess(data)

        # Make predictions
        predictions = model.predict(features)

    except Exception as e:
        # Aquí puedes capturar más detalles del error
        print(f"Error en la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

    return {"predict": predictions}