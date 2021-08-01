from sqlalchemy.orm import Session

from app.cruds.table_repository import TableRepository
from db import models


class ContactCrud(TableRepository):

    def __init__(self, db) -> None:
        super().__init__(db=db, entity=models.Contact)

    def store(self, item, checker=None):
        item = item.dict(exclude_unset=True)
        exist = False
        if checker:
            exist = self.db.query(self.entity).filter_by(**checker).first()
        if not exist:
            ocr_model_object = self.entity(**item)
            self.db.add(ocr_model_object)
            return ocr_model_object
        else:
            return exist
