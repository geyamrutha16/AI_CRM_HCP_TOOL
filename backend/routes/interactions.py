"""
FastAPI routes for interaction management.
Handles CRUD operations for HCP interactions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import Interaction, get_db
from models.schemas import (
    InteractionCreate,
    InteractionResponse,
    InteractionUpdate
)
from typing import List

router = APIRouter(prefix="/interaction", tags=["interactions"])


@router.post("/", response_model=InteractionResponse)
def create_interaction(
    interaction: InteractionCreate,
    db: Session = Depends(get_db)
) -> InteractionResponse:
    """
    Create a new interaction record.
    
    Args:
        interaction: Interaction data
        db: Database session
    
    Returns:
        Created interaction response
    """
    # Create new interaction record
    db_interaction = Interaction(
        doctor_name=interaction.doctor_name,
        summary=interaction.summary,
        sentiment=interaction.sentiment,
        follow_up=interaction.follow_up,
        interaction_text=interaction.interaction_text
    )
    
    # Save to database
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    
    return db_interaction


@router.get("/", response_model=List[InteractionResponse])
def get_interactions(
    skip: int = 0,
    limit: int = 10,
    doctor_name: str = None,
    db: Session = Depends(get_db)
) -> List[InteractionResponse]:
    """
    Retrieve interactions with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        doctor_name: Filter by doctor name (optional)
        db: Database session
    
    Returns:
        List of interactions
    """
    query = db.query(Interaction)
    
    # Filter by doctor name if provided
    if doctor_name:
        query = query.filter(Interaction.doctor_name.ilike(f"%{doctor_name}%"))
    
    # Order by most recent and apply pagination
    interactions = query.order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()
    
    return interactions


@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
) -> InteractionResponse:
    """
    Retrieve a specific interaction by ID.
    
    Args:
        interaction_id: ID of the interaction
        db: Database session
    
    Returns:
        Interaction details
    
    Raises:
        HTTPException: If interaction not found
    """
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    return interaction


@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    interaction_update: InteractionUpdate,
    db: Session = Depends(get_db)
) -> InteractionResponse:
    """
    Update an existing interaction.
    
    Args:
        interaction_id: ID of the interaction
        interaction_update: Updated data
        db: Database session
    
    Returns:
        Updated interaction
    
    Raises:
        HTTPException: If interaction not found
    """
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    # Update only provided fields
    update_data = interaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interaction, field, value)
    
    db.commit()
    db.refresh(interaction)
    
    return interaction


@router.delete("/{interaction_id}")
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Delete an interaction.
    
    Args:
        interaction_id: ID of the interaction
        db: Database session
    
    Returns:
        Confirmation message
    
    Raises:
        HTTPException: If interaction not found
    """
    interaction = db.query(Interaction).filter(
        Interaction.id == interaction_id
    ).first()
    
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    
    db.delete(interaction)
    db.commit()
    
    return {"message": f"Interaction {interaction_id} deleted successfully"}
