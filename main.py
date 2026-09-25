import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client

load_dotenv()

app = FastAPI(title="VeritasAI KYC API")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


class KYCData(BaseModel):
    pan_number: str
    full_name: str


def clean_pan(pan: str):
    return pan.replace(" ", "").strip().upper()


def clean_name(name: str):
    return " ".join(name.strip().upper().split())


def valid_pan(pan: str):
    return re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan) is not None


def save_result(pan, name, status, reason):
    record = {
        "pan_number": pan,
        "full_name": name,
        "status": status,
        "verification_reason": reason
    }

    if status == "VERIFIED":
        record["verified_at"] = datetime.now(timezone.utc).isoformat()

    result = (
        supabase
        .table("kyc_applications")
        .insert(record)
        .execute()
    )

    return result.data[0]


@app.get("/")
def home():
    return {"message": "VeritasAI KYC API is running"}


@app.post("/kyc")
def verify_kyc(data: KYCData):

    pan = clean_pan(data.pan_number)
    name = clean_name(data.full_name)

    # Basic validation
    if not valid_pan(pan):
        record = save_result(
            pan,
            name,
            "FAILED",
            "Invalid PAN format"
        )

        return {
            "success": True,
            "kyc_status": "FAILED",
            "message": "Invalid PAN format",
            "data": record
        }

    if not name:
        record = save_result(
            pan,
            name,
            "FAILED",
            "Full name is required"
        )

        return {
            "success": True,
            "kyc_status": "FAILED",
            "message": "Full name is required",
            "data": record
        }

    # Check PAN in reference data
    result = (
        supabase
        .table("kyc_reference")
        .select("pan_number, full_name")
        .eq("pan_number", pan)
        .limit(1)
        .execute()
    )

    reference = result.data

    if not reference:
        status = "MANUAL_REVIEW"
        reason = "PAN not found in reference records"

    else:
        reference_name = clean_name(reference[0]["full_name"])

        if reference_name == name:
            status = "VERIFIED"
            reason = "PAN and name matched"

        else:
            status = "FAILED"
            reason = "Name does not match PAN record"

    record = save_result(
        pan,
        name,
        status,
        reason
    )

    return {
        "success": True,
        "kyc_status": status,
        "message": reason,
        "data": record
    }


@app.get("/kyc")
def get_kyc_records():

    result = (
        supabase
        .table("kyc_applications")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return {
        "success": True,
        "count": len(result.data),
        "data": result.data
    }