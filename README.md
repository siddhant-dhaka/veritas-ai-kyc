# VeritasAI — Voice-Based KYC Verification System

> An AI-powered voice KYC workflow that collects and confirms customer identity details over a phone call, processes them through a FastAPI backend, performs rule-based verification against a synthetic reference dataset, and persists the result in Supabase.

---

## 🚀 Overview

**VeritasAI** is a voice-first KYC verification prototype designed for telecom customer onboarding.

The system uses **Inya AI by Gnani** as the conversational voice layer. A customer interacts with the agent over a phone call, provides their PAN number and full legal name, and confirms the captured information.

Once the call ends, the structured KYC data is automatically sent to a **FastAPI backend**, where it is normalized, validated, checked against a synthetic KYC reference dataset, assigned a verification status, and stored in **Supabase PostgreSQL**.

### End-to-End Flow

```text
                 CUSTOMER
                    │
                 Phone Call
                    │
                    ▼
            ┌────────────────┐
            │    Inya AI     │
            │  Voice Agent   │
            └───────┬────────┘
                    │
             PAN + Full Name
                    │
                    ▼
            ┌────────────────┐
            │    FastAPI     │
            │    Backend     │
            └───────┬────────┘
                    │
            Normalize + Validate
                    │
                    ▼
            ┌────────────────┐
            │ KYC Reference  │
            │    Dataset     │
            └───────┬────────┘
                    │
              Match / No Match
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      VERIFIED    FAILED   MANUAL_REVIEW
          │         │         │
          └─────────┼─────────┘
                    ▼
            ┌────────────────┐
            │    Supabase    │
            │   PostgreSQL   │
            └────────────────┘
