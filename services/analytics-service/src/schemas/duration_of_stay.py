from datetime import date

from pydantic import BaseModel, ConfigDict


class DurationOfStayPoint(BaseModel):
    """One day's duration-of-stay statistics, in minutes"""

    visit_date: date
    sample_size: int
    avg_duration_minutes: float
    median_duration_minutes: float
    min_duration_minutes: float
    max_duration_minutes: float

    model_config = ConfigDict(from_attributes=True)


class DurationOfStayResponse(BaseModel):
    """Response schema for the duration-of-stay endpoint"""

    series: list[DurationOfStayPoint]
