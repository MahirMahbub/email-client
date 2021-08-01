import datetime

from sqlalchemy import and_

from app.cruds.table_repository import TableRepository
from db import models


class EmailDetailsCrud(TableRepository):

    def __init__(self, db) -> None:
        super().__init__(db=db, entity=models.EmailDetails)

    def create_message_details(self, subject: str,
                               from_address: str,
                               message_id: str,
                               thread_id: int,
                               email_account_provider_id: int,
                               body: str,
                               operation_datetime: datetime,
                               history_id: str,
                               is_read: bool,
                               type_: str,
                               contact_id: int,
                               account_id: int):
        check_message = self.get_message_by_thread_id_and_message_id(message_id, thread_id)
        if check_message is None:
            email_details_object = self.entity(subject=subject,
                                               from_address=from_address,
                                               message_id=message_id,
                                               thread_id=thread_id,
                                               email_account_provider_id=email_account_provider_id, body=body,
                                               operation_datetime=operation_datetime, history_id=history_id,
                                               is_read=is_read, type=type_, contact_id=contact_id,
                                               account_id=account_id)
        else:
            return check_message
        self.db.add(email_details_object)
        self.db.flush()
        return email_details_object

    def get_message_by_thread_id_and_message_id(self, message_id, thread_id):
        return self.db.query(self.entity).filter(
            and_(self.entity.thread_id == thread_id, self.entity.message_id == message_id)).first()

    def get_message_list_by_thread_id(self, account_id: int, thread_id: str, email_provider_id):
        return self.db.query(self.entity).filter(
            and_(self.entity.account_id == account_id,
                 self.entity.thread_id == thread_id,
                 self.entity.email_account_provider_id == email_provider_id)
        ).order_by(self.entity.operation_datetime).all()

    def update_mail_seen_unseen_status(self, message_id, thread_id, account_id, mail_provider_id, is_seen):
        return self.db.query(self.entity).filter(and_(self.entity.message_id == message_id,
                                                      self.entity.thread_id == thread_id,
                                                      self.entity.account_id == account_id,
                                                      self.entity.email_account_provider_id == mail_provider_id)
                                                 ).update({"is_read": is_seen}, synchronize_session='fetch')

    def update_mail_read_status(self, message_id, thread_id, account_id, mail_provider_id):
        return self.db.query(self.entity).filter(and_(self.entity.message_id == message_id,
                                                      self.entity.thread_id == thread_id,
                                                      self.entity.account_id == account_id,
                                                      self.entity.email_account_provider_id == mail_provider_id)
                                                 ).update({"is_read": True}, synchronize_session='fetch')

    def get_message_by_message_id(self, message_id):
        return self.db.query(self.entity).filter(self.entity.message_id == message_id).first()
