from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import asyncio
from datetime import datetime, timezone

router = APIRouter(prefix="/kairos", tags=["kairos"])

# Global execution control
execution_state = {
    "is_running": False,
    "current_task_id": None,
    "stop_requested": False,
    "last_started": None,
    "last_stopped": None
}

class StopRequest(BaseModel):
    reason: Optional[str] = "User requested stop"

@router.get("/status")
async def get_execution_status():
    """Get current execution status"""
    return {
        "success": True,
        "data": execution_state
    }

@router.post("/stop")
async def stop_execution(request: StopRequest):
    """Gracefully stop current execution"""
    if not execution_state["is_running"]:
        return {
            "success": True,
            "message": "No execution in progress",
            "data": execution_state
        }
    
    # Set stop flag
    execution_state["stop_requested"] = True
    execution_state["last_stopped"] = datetime.now(timezone.utc).isoformat()
    
    # Wait briefly for graceful shutdown
    await asyncio.sleep(0.5)
    
    # Force reset state
    execution_state["is_running"] = False
    execution_state["current_task_id"] = None
    
    return {
        "success": True,
        "message": f"Execution stopped gracefully. Reason: {request.reason}",
        "data": execution_state
    }

@router.post("/start")
async def start_execution(task_id: str):
    """Mark execution as started (called by engine)"""
    execution_state["is_running"] = True
    execution_state["current_task_id"] = task_id
    execution_state["stop_requested"] = False
    execution_state["last_started"] = datetime.now(timezone.utc).isoformat()
    
    return {
        "success": True,
        "message": "Execution started",
        "data": execution_state
    }

@router.post("/complete")
async def complete_execution():
    """Mark execution as completed (called by engine)"""
    execution_state["is_running"] = False
    execution_state["current_task_id"] = None
    execution_state["stop_requested"] = False
    
    return {
        "success": True,
        "message": "Execution completed",
        "data": execution_state
    }

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "kairos-engine"}
