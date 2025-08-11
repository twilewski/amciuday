from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db import get_session
from app.models.models import SpinHistory, Recipe
from app.models.schemas import SpinHistoryResponse, RecipeResponse

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/", response_model=List[SpinHistoryResponse])
def get_spin_history(
    meal: Optional[str] = Query(None, description="Filter by meal type"),
    from_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    session: Session = Depends(get_session)
):
    """Get spin history with optional filters."""
    statement = select(SpinHistory, Recipe).join(Recipe).order_by(SpinHistory.spun_at.desc())
    
    # Apply meal filter
    if meal:
        if meal not in ["breakfast", "lunch", "snack", "dinner"]:
            raise HTTPException(status_code=400, detail="Invalid meal type")
        statement = statement.where(SpinHistory.meal_type == meal)
    
    # Apply date filters
    if from_date:
        from_datetime = datetime.combine(from_date, datetime.min.time())
        statement = statement.where(SpinHistory.spun_at >= from_datetime)
    
    if to_date:
        to_datetime = datetime.combine(to_date, datetime.max.time())
        statement = statement.where(SpinHistory.spun_at <= to_datetime)
    
    results = session.exec(statement).all()
    
    return [
        SpinHistoryResponse(
            id=history.id,
            recipe=RecipeResponse(
                id=recipe.id,
                title=recipe.title,
                source=recipe.source,
                url=recipe.url,
                meal_type=recipe.meal_type,
                time_minutes=recipe.time_minutes,
                image_url=recipe.image_url,
                tags=recipe.tags,
                steps_excerpt=recipe.steps_excerpt
            ),
            meal_type=history.meal_type,
            allow_one_extra=history.allow_one_extra,
            spun_at=history.spun_at
        )
        for history, recipe in results
    ]


@router.delete("/")
def clear_history(session: Session = Depends(get_session)):
    """Clear all spin history."""
    statement = select(SpinHistory)
    history_entries = session.exec(statement).all()
    
    for entry in history_entries:
        session.delete(entry)
    
    session.commit()
    return {"message": f"Cleared {len(history_entries)} history entries"}


@router.delete("/{history_id}")
def delete_history_entry(
    history_id: int,
    session: Session = Depends(get_session)
):
    """Delete a specific history entry."""
    history_entry = session.get(SpinHistory, history_id)
    if not history_entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    session.delete(history_entry)
    session.commit()
    
    return {"message": "History entry deleted"}