"""FastAPI server to handle M-Pesa STK Push callbacks for integration testing.

Stores, validates, and exposes callbacks for test assertions.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import logging
import json
import time
from datetime import datetime

# 🔗 Your SDK models
from mpesa_sdk.mpesa_express import StkPushSimulateCallback

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("callback_received.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# --- In-Memory Storage for Test Assertions ---
received_callbacks: List[Dict[str, Any]] = []

# --- FastAPI App ---
app = FastAPI(
    title="M-Pesa STK Callback Test Server",
    description="Test server for M-Pesa Daraja STK Push callbacks. Stores, validates, and exposes callbacks for integration testing.",
    version="1.1.0",
)


# --- Routes ---
@app.get("/")
def home():
    """Root endpoint that returns server status and available endpoints."""
    return {
        "message": "M-Pesa STK Callback Test Server is running!",
        "endpoints": {
            "callback": "/mpesa/callback (POST)",
            "health": "/health (GET)",
            "received": "/mpesa/callback/received (GET)",
            "clear": "/mpesa/callback/clear (POST)",
        },
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Health check endpoint to verify server is running."""
    return {"status": "healthy"}


@app.post("/mpesa/callback")
async def mpesa_stk_callback(request: Request):
    """Handle M-Pesa STK Push callback.

    Validates the incoming callback, logs it, and stores it for test assertions.
    """
    global received_callbacks
    logger.info("📥 Received new M-Pesa STK Push callback")
    request_id = f"cb-{int(time.time())}-{id(request)}"
    start_time = datetime.now().isoformat()

    try:
        # Read raw body
        body = await request.body()
        body_str = body.decode("utf-8")

        logger.info(f"📥 [{request_id}] Raw callback received:")
        try:
            pretty = json.dumps(json.loads(body_str), indent=2)
            logger.info(f"📥 [{request_id}] \n{pretty}")
        except Exception:
            logger.info(f"📥 [{request_id}] {body_str}")

        # Validate with SDK model
        callback_data: StkPushSimulateCallback = (
            StkPushSimulateCallback.model_validate_json(body_str)
        )

        # Extract key fields
        stk = callback_data.Body.stkCallback
        amount = callback_data.amount or "N/A"
        receipt = callback_data.mpesa_receipt_number or "N/A"
        phone = callback_data.phone_number or "N/A"

        # Log structured info
        logger.info(f"✅ [{request_id}] Validated callback:")
        logger.info(f"  MerchantRequestID: {stk.MerchantRequestID}")
        logger.info(f"  CheckoutRequestID: {stk.CheckoutRequestID}")
        logger.info(
            f"  ResultCode: {stk.ResultCode} ({'Success' if stk.ResultCode == 0 else 'Failed'})"
        )
        logger.info(f"  Amount: {amount}, Receipt: {receipt}, Phone: {phone}")

        # Store in memory for test assertions
        received_callbacks.append(
            {
                "request_id": request_id,
                "timestamp": start_time,
                "raw_body": body_str,
                "parsed": callback_data.model_dump(),
                "result_code": stk.ResultCode,
                "result_desc": stk.ResultDesc,
                "checkout_request_id": stk.CheckoutRequestID,
                "merchant_request_id": stk.MerchantRequestID,
                "amount": amount,
                "receipt": receipt,
                "phone": phone,
            }
        )

        # Acknowledge to Daraja
        return JSONResponse(
            content={"ResultCode": 0, "ResultDesc": "Success"}, status_code=200
        )

    except json.JSONDecodeError as e:
        logger.error(f"❌ [{request_id}] Invalid JSON: {e.msg}")
        raise HTTPException(status_code=400, detail="Invalid JSON")

    except Exception as e:
        logger.error(
            f"❌ [{request_id}] Unexpected error: {type(e).__name__}: {str(e)}"
        )
        return JSONResponse(
            content={"ResultCode": 1, "ResultDesc": "Internal Error"}, status_code=500
        )


# --- 🔬 Debug Endpoints (for tests) ---
@app.get("/mpesa/callback/received")
def get_received_callbacks():
    """Return all received callbacks. Useful for test assertions."""
    return {"count": len(received_callbacks), "callbacks": received_callbacks}


@app.get("/mpesa/callback/latest")
def get_latest_callback():
    """Return the most recent callback."""
    if not received_callbacks:
        raise HTTPException(status_code=404, detail="No callbacks received yet")
    return received_callbacks[-1]


@app.post("/mpesa/callback/clear")
def clear_received_callbacks():
    """Clear all stored callbacks. Use between tests."""
    count = len(received_callbacks)
    received_callbacks.clear()
    logger.info(f"🗑️ Cleared {count} received callbacks")
    return {"cleared": count}
