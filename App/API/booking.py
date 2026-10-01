from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from App.Database.database import get_db
from App.Database.models import Booking
from App.Schemas.schemas import BookingOut

router = APIRouter(prefix="/bookings", tags=["Booking"])


@router.get("/", response_model=list[BookingOut])
def list_bookings(db: Session = Depends(get_db)) -> list[Booking]:
    return list(db.scalars(select(Booking).order_by(Booking.id.desc())))
