# Sales Coach - Backend (Mockable Smallest.ai Integration)

This repository contains a FastAPI-based backend scaffold for a Sales-Coach
roleplay system using Smallest.ai (mockable for offline dev). It includes:

- smallest_wrapper.py: wrapper that uses real Smallest.ai SDK if available
  otherwise falls back to a Mock client for local development / tests.
- personas.py: predefined persona templates used to seed agents.
- analysis.py: conversation analysis heuristics (mock coach) producing scores and suggestions.
- session_manager.py: session lifecycle, conversation flow, and TTS placeholder.
- app/main.py: FastAPI app wiring the endpoints (uses mock by default).
- tests/: unittest-based tests that run in mock mode.

NOTE: This environment has no external network access, so the repo is configured
to default to mock mode. When you run locally, install `smallestai` and set
`SMALLEST_API_KEY` to run with the real SDK.
