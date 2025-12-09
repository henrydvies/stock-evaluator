from fastapi import APIRouter, Depends, HTTPException, status

from app.core.fundamentals_service import FundamentalsService, FundamentalsDataError
