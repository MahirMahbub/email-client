from sqlalchemy import and_

from app.cruds.table_repository import TableRepository
from db import models
from db.models import EmailReceiverType


class EmailReceiverCrud(TableRepository):

    def __init__(self, db) -> None:
        super().__init__(db=db, entity=models.EmailReceiver)

    def create_address_receiver(self, email_id, address_list, type_):
        for address in address_list:
            receiver_object = self.entity(email_id=email_id,
                                          address=address, type=type_)
            self.db.add(receiver_object)

    def get_receivers_by_email_id(self, email_id):
        return self.db.query(self.entity).filter(self.entity.email_id == email_id).all()

    def get_to_receivers_address_by_email_id(self, email_id):
        return self.db.query(self.entity.address).filter(and_(self.entity.email_id == email_id,
                                                              self.entity.type == EmailReceiverType.TO)).all()

    def get_cc_receivers_address_by_email_id(self, email_id):
        return self.db.query(self.entity.address).filter(and_(self.entity.email_id == email_id,
                                                              self.entity.type == EmailReceiverType.CC)).all()

    def get_bcc_receivers_address_by_email_id(self, email_id):
        return self.db.query(self.entity.address).filter(and_(self.entity.email_id == email_id,
                                                              self.entity.type == EmailReceiverType.BCC)).all()
