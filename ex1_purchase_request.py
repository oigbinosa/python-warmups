from pydantic import BaseModel, field_validator, model_validator, ValidationError


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(c, value: int) -> int:
        if value < 0:
            raise ValueError("quantity cannot be negative")
        return value


class PurchaseRequest(BaseModel):
    id: str
    vendor: str
    lineItems: list[LineItem]
    total: float

    @model_validator(mode="after")
    def total_matches_line_items(self) -> "PurchaseRequest":
        expected = sum(item.quantity * item.unit_price for item in self.lineItems)
        if self.total != expected:
            raise ValueError(
                "total {self.total} does not match line items sum {expected:.2f}"
            )
        # self is the fully built object, so self.line_items and self.total are ready to use
        # compute the expected total from the line items
        # if it doesn't match self.total, raise ValueError("...")
        return self  # always return self


if __name__ == "__main__":
    valid_request = PurchaseRequest(
        id="PR-1001",
        vendor="Northeast Safety Supply",
        lineItems=[
            LineItem(
                description="Insulated work gloves", quantity=10, unit_price=12.50
            ),
            LineItem(description="Hard hat, Class E", quantity=4, unit_price=37.25),
        ],
        total=274.00,
    )
    print(valid_request.model_dump_json(indent=2))

    bad_cases = {
        "negative quantity": dict(
            id="PR-1002",
            vendor="Acme",
            lineItems=[dict(description="Gloves", quantity=-2, unit_price=12.50)],
            total=-25.00,
        ),
        "wrong total": dict(
            id="PR-1003",
            vendor="Acme",
            lineItems=[dict(description="Gloves", quantity=2, unit_price=12.50)],
            total=30.00,
        ),
    }

    for name, data in bad_cases.items():
        try:
            PurchaseRequest(**data)
            print(f"{name}: unexpectedly passed")
        except ValidationError as e:
            print(f"{name}: rejected\n{e}\n")
