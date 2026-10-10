from pydantic import BaseModel


class RefreshResponse(BaseModel):
    """Response schema returned after a manual stats refresh"""

    status: str
