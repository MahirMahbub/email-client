import pickle
from datetime import datetime

from sqlalchemy import and_

from app.cruds.table_repository import TableRepository
from db import models


class EmailAccountProvidedCrud(TableRepository):

    def __init__(self, db) -> None:
        super().__init__(db=db, entity=models.EmailAccountProvided)
        # EmailAccountProvided

    def create_email_credential(self, email: str, account_id: int, token: pickle, provider: str):
        token_obj = self.entity(email=email, account_id=account_id, token=token, provider=provider)
        self.db.add(token_obj)

    def find_active_email_provider(self, provider_id: int, account_id: int):
        item = self.db.query(self.entity) \
            .filter(self.entity.account_id == account_id, self.entity.id == provider_id,
                    self.entity.is_active == True).first()
        return item

    def clear_email_provider(self, provider_id: int, account_id: int):
        return self.db.query(self.entity) \
            .filter(self.entity.account_id == account_id, self.entity.id == provider_id).update({"is_active": False})

    def clear_current_active_email(self, account_id):
        return self.db.query(self.entity) \
            .filter(self.entity.account_id == account_id).update({"is_active": False})

    def set_active_email(self, email: str, account_id: int):
        set_existing_email_false = self.clear_current_active_email(account_id)
        if set_existing_email_false:
            return self.db.query(self.entity) \
                .filter(self.entity.account_id == account_id,
                        self.entity.email == email) \
                .update({"is_active": True})

        else:
            return False

    def find_first_active_by_account(self, account_id: int):
        item = self.db.query(self.entity).filter(
            self.entity.account_id == account_id,
            self.entity.is_active == True
        ).first()
        return item

    def get_credential_object(self, email: str, account_id: int):
        cred = self.db.query(self.entity.token).filter(
            and_(self.entity.account_id == account_id,
                 self.entity.email == email,
                 self.entity.is_active == True)).first()
        # print("Credential ", cred)
        if cred is not None:
            return pickle.loads(cred[0])
        else:
            return None

    def get_current_date_from_email_communication_object(self, email, account_id):
        email_communication_created_at = (self.db.query(self.entity.created_datetime).filter(
            and_(self.entity.account_id == account_id,
                 self.entity.email == email)).first())
        date_object = email_communication_created_at.date()
        return str(date_object.year) + '/' + str(date_object.month) + '/' + str(date_object.day)

    def get_last_sync_epoch_from_email_communication_object(self, email, account_id):
        email_communication_last_sync_epoch = self.db.query(self.entity.last_synced_epoch).filter(
            and_(self.entity.account_id == account_id,
                 self.entity.email == email)).first()
        return email_communication_last_sync_epoch[0]

    def update_email_credential(self, email, account_id, token):
        update_response = self.db.query(self.entity).filter(
            and_(self.entity.email == email,
                 self.entity.account_id == account_id)).update(
            {"token": token, "token_refresh_date": datetime.now()})
        return update_response

    def update_last_sync_date(self, last_sync_date, email, account_id):
        update_response = self.db.query(self.entity).filter(
            and_(self.entity.email == email,
                 self.entity.account_id == account_id)).update(
            {"last_synced_epoch": last_sync_date})
        return update_response

    def get_email_account_provider_table_id_by_email(self, email, account_id):
        return self.db.query(self.entity.id).filter(and_(self.entity.email == email,
                                                         self.entity.account_id == account_id)).first()

    def get_connected_mail_list_by_account_id(self, account_id):
        return [r.email for r in self.db.query(self.entity.email).filter(
            self.entity.account_id == account_id,
            self.entity.is_active == True
        )]

    def get_actives_by_account(self, account_id: int):
        items = self.db.query(self.entity) \
            .filter(and_(self.entity.account_id == account_id, self.entity.is_active == True)) \
            .all()
        return items

    # def create_email_thread_assignment(self, user_id, thread_id):
    #     assign_thread_object = self.get_assigned_owner(thread_id=thread_id)
    #     if assign_thread_object is None:
    #         assign_thread_object = models.EmailThreadAssigneeAssociation(thread_id=thread_id,
    #                                                                      assignee_id=user_id)
    #         self.db.add(assign_thread_object)
    #         self.db.flush()
    #     else:
    #         self.db.query(models.EmailThreadAssigneeAssociation).filter(
    #             models.EmailThreadAssigneeAssociation.thread_id == thread_id).update({"assignee_id": user_id})
    #         self.db.commit()
    #         assign_thread_object = self.get_assigned_owner(thread_id=thread_id)
    #     return assign_thread_object
    #
    # def get_assigned_owner(self, thread_id):
    #
    #     return self.db.query(models.EmailThreadAssigneeAssociation).filter(
    #         models.EmailThreadAssigneeAssociation.thread_id == thread_id).first()
