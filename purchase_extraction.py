from datetime import date

from pydantic import BaseModel, Field


class PurchaseExtraction(BaseModel):
    vendor: str = Field(description="Company supplying the item")
    item: str = Field(description="What is being ordered, including model numbers")
    quantity: int = Field(description="Number of units ordered")
    needed_by: date | None = Field(
        default=None,
        description="Delivery or deadline date in YYYY-MM-DD; null if no date is stated",
    )
