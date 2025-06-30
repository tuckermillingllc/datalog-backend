from sqlalchemy.orm import Session
from app import models, schemas

def get_logs(db: Session):
    return db.query(models.Log).all()

def create_log(db: Session, log: schemas.LogCreate):
    db_log = models.Log(message=log.message)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
