import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Date, ForeignKey, Text
from backend.app.db.base import Base


class MLRun(Base):
    __tablename__ = "ml_runs"

    run_id = Column(String(50), primary_key=True, index=True)
    run_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    model_name = Column(String(100), nullable=False)
    horizon_days = Column(Integer, nullable=False, default=30)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    wape = Column(Float, nullable=False)
    parameters_json = Column(Text, nullable=True)
    selection_reason = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)


class Forecast(Base):
    __tablename__ = "forecasts"

    forecast_id = Column(String(50), primary_key=True, index=True)
    run_id = Column(String(50), ForeignKey("ml_runs.run_id"), nullable=True, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    model_name = Column(String(100), nullable=False, default="Gradient Boosting Regressor")
    forecast_date = Column(Date, nullable=False, index=True)
    horizon_days = Column(Integer, nullable=False, default=30)
    predicted_demand = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    is_forecast = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
