from fastapi import Request, HTTPException
from backend.utils.signer import sign_payload
import time

async def validate_signed_request(request: Request):

    pid = request.query_params.get("pid")
    rid = request.query_params.get("rid")
    exp = request.query_params.get("exp")
    sig = request.query_params.get("sig")

    if not pid or not rid or not exp or not sig:
        raise HTTPException(status_code=401, detail="Missing access token")

    # if int(time.time() * 1000) > int(exp):
    #     raise HTTPException(status_code=401, detail="Session expired")
    print("TOKEN VALIDATED:", pid)

    expected = sign_payload(f"{pid}|{rid}|{exp}")

    if expected != sig:
        raise HTTPException(status_code=401, detail="Invalid session")

    return {"pid": pid, "rid": rid}
