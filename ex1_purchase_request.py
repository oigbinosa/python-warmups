from pydantic import BaseModel, ValidationError, field_validator, json, model_validator


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(c, value: int) -> int:
        if value <= 0:
            raise ValueError("quantity cannot be less than or equal to zero")
        return value


class PurchaseRequest(BaseModel):
    id: str
    vendor: str
    lineItems: list[LineItem]
    total: float

    @model_validator(mode="after")
    def total_matches_line_items(self) -> PurchaseRequest:
        expected = sum(item.quantity * item.unit_price for item in self.lineItems)
        if abs(expected - self.total) > 0.01:
            raise ValueError(
                f"total {self.total} does not match line items sum {expected:.2f}"
            )
        # self is the fully built object, so self.line_items and self.total are ready to use
        # compute the expected total from the line items
        # if it doesn't match self.total, raise ValueError("...")
        return self  # always return self


if __name__ == "__main__":
    # print(valid_request.model_dump_json(indent=2))

    with open("purchaseRequests.json") as file:
        data = json.load(file)

    for request in data:
        try:
            PurchaseRequest.model_validate(request)
        except ValidationError as e:
            print(f"{request['id']}: rejected\n{e}\n")
