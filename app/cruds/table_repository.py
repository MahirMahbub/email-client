from typing import TypeVar, Generic

from sqlalchemy.orm import Session

from db import models
from db.database import Base

T = TypeVar('T')


class TableRepository:
    entity: Generic[T] = None
    db: Session = NotImplementedError

    def __init__(self, db: Session, entity: Generic[T]):
        self.db: Session = db
        self.entity: Base = entity

    def store(self, item):
        item = item.dict(exclude_unset=True)
        ocr_model_object = self.entity(**item)
        self.db.add(ocr_model_object)
        return ocr_model_object

    def get(self, id_: int):
        return self.db.query(self.entity).filter(self.entity.id == id_).first()

    def gets(self):
        return self.db.query(self.entity).all()

    def update(self, id_, item):
        item_dict = item.dict(exclude_unset=True)
        return self.db.query(self.entity).filter(self.entity.id == id_).update(item_dict)