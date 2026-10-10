from pydantic import BaseModel, ConfigDict


class MonthlyVisitPoint(BaseModel):
    """Visit count for a single year/month bucket"""

    year: int
    month: int
    season: str
    visit_count: int

    model_config = ConfigDict(from_attributes=True)


class MonthlyTrendsResponse(BaseModel):
    """Response schema for the monthly-trends endpoint"""

    series: list[MonthlyVisitPoint]


class WeekdayVisitPoint(BaseModel):
    """Visit count for a single ISO day-of-week (1=Monday..7=Sunday)"""

    day_of_week: int
    visit_count: int

    model_config = ConfigDict(from_attributes=True)


class WeekdayTrendsResponse(BaseModel):
    """Response schema for the weekday-trends endpoint"""

    series: list[WeekdayVisitPoint]
