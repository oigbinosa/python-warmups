from fastapi import FastAPI, HTTPException

from ex1_purchase_request import PurchaseRequest

app = FastAPI(title="Purchase Requests API")

requests_db: dict[str, PurchaseRequest] = {}  # in-memory "database" for this exercise


@app.post("/requests", status_code=201)
def create_request(request: PurchaseRequest) -> PurchaseRequest:
    if request.id in requests_db:
        raise HTTPException(
            status_code=409, detail=f"request {request.id} already exists"
        )

    requests_db[request.id] = request
    return request


@app.get("/requests/{request_id}")
def get_request(request_id: str) -> PurchaseRequest:
    # if not found → raise HTTPException(status_code=404, detail="...")
    if request_id not in requests_db:
        raise HTTPException(status_code=404, detail="it's not here")
    return requests_db[request_id]
