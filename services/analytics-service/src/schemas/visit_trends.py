from datetime import date

from pydantic import BaseModel, ConfigDict


class VisitTrendPoint(BaseModel):
    """Visit count for a single day, optionally scoped to one filter/group value"""

    visit_date: date
    group_value: str | None = None
    visit_count: int

    model_config = ConfigDict(from_attributes=True)


class VisitTrendsResponse(BaseModel):
    """Response schema for the visit-trends endpoint"""

    series: list[VisitTrendPoint]


class MunicipalityOption(BaseModel):
    """A selectable (country, municipality) pair for the municipality filter"""

    country_code: str
    municipality: str

    model_config = ConfigDict(from_attributes=True)


class FilterOptionsResponse(BaseModel):
    """Response schema for the filter-options endpoint"""

    vehicle_types: list[str]
    country_codes: list[str]
    municipalities: list[MunicipalityOption]
