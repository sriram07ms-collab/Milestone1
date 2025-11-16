"""Pydantic schemas for API"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    query: str = Field(..., description="User's question about mutual funds")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    answer: str = Field(..., description="Answer to the user's question")
    source_url: str = Field(..., description="Source URL from Groww")
    scheme_name: Optional[str] = Field(None, description="Scheme name if applicable")
    fact_type: Optional[str] = Field(None, description="Type of fact answered")
    query_type: Optional[str] = Field(None, description="Type of query")
    last_updated: Optional[date] = Field(None, description="Date when data was last updated")


class SchemeInfo(BaseModel):
    """Scheme information schema"""
    scheme_id: int
    scheme_name: str
    category: Optional[str]
    risk_level: Optional[str]
    nav: Optional[float]
    expense_ratio: Optional[str]
    rating: Optional[int]
    fund_size_cr: Optional[float]
    groww_url: str

    class Config:
        from_attributes = True


class SchemeFactInfo(BaseModel):
    """Scheme fact information schema"""
    fact_id: int
    fact_type: str
    fact_value: str
    source_url: str
    extraction_date: date

    class Config:
        from_attributes = True


class SchemeDetailResponse(BaseModel):
    """Response schema for scheme details"""
    scheme: SchemeInfo
    facts: List[SchemeFactInfo]


class SchemesListResponse(BaseModel):
    """Response schema for schemes list"""
    schemes: List[SchemeInfo]
    total: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    database_connected: bool
    llm_configured: bool
    rag_configured: bool = False

