from pydantic import BaseModel, ConfigDict


class HourlyVisitPoint(BaseModel):
    """Visit count for a single hour-of-day bucket"""

    hour_of_day: int
    visit_count: int

    model_config = ConfigDict(from_attributes=True)


class RushHourResponse(BaseModel):
    """Response schema for the rush-hour endpoint"""

    series: list[HourlyVisitPoint]
