from sqlalchemy import and_, cast, Date

from app.cruds.email_account_provider import EmailAccountProvidedCrud
from app.cruds.table_repository import TableRepository
from db import models


class EmailThreadCrud(TableRepository):

    def __init__(self, db) -> None:
        super().__init__(db=db, entity=models.EmailThread)

    def get_thread_by_thread_id(self, thread_id, account_id, email_account_provider_id):
        return self.db.query(self.entity). \
            filter(and_(self.entity.thread_id == thread_id,
                        self.entity.account_id == account_id,
                        self.entity.email_account_provider_id == email_account_provider_id)).first()

    def get_thread_by_id(self, thread_id):
        return self.db.query(self.entity).filter(self.entity.id == thread_id).first()

    def create_email_thread(self, account_id, email, thread_id):
        thread_object = self.entity(thread_id=thread_id,
                                    email=email, email_account_provider_id=EmailAccountProvidedCrud(
                                        db=self.db).get_email_account_provider_table_id_by_email(
                                        email=email, account_id=account_id)[0],
                                    account_id=account_id, is_closed=False, is_trashed=False)
        self.db.add(thread_object)
        self.db.flush()
        return thread_object

    def get_threads_by_email_and_account_id(self, email, account_id):
        return self.db.query(self.entity).filter(
            and_(self.entity.email == email, self.entity.account_id == account_id)).order_by(
            self.entity.updated_datetime.desc()).all()

    def update_thread_read_status(self, thread_id, account_id, mail_provider_id):
        return self.db.query(self.entity).filter(and_(self.entity.thread_id == thread_id,
                                                      self.entity.account_id == account_id,
                                                      self.entity.email_account_provider_id == mail_provider_id)
                                                 ).update({"is_read": True}, synchronize_session='fetch')

    def get_filtered_data(self, is_closed, contact_email, date_ranges, account_id, email_provider_id):
        # if assigned_id == "Unassigned":
        #     assigned_id = None
        #
        # if not assigned_id == "All":
        #     assigned_id = assigned_id

        filter_statement = None
        if date_ranges is not None:
            filter_statement = cast(self.entity.updated_datetime, Date)

        thread = self.db.query(self.entity).filter(
            and_(self.entity.account_id == account_id,
                 self.entity.email_account_provider_id == email_provider_id)).filter(
            self.entity.is_closed == is_closed)
        # if not assigned_id == "All":
        #     thread = thread.filter(self.entity.id == self.entityAssigneeAssociation.thread_id).filter(
        #         self.entityAssigneeAssociation.assignee_id == assigned_id)
        if not contact_email == "All":
            thread = thread.filter(self.entity.latest_message_email.contains(contact_email))
        if date_ranges is not None:
            thread = thread.filter(filter_statement.in_(date_ranges))
        return thread.order_by(
            self.entity.sync_datetime.desc()).all()

    def update_thread_seen_unseen_status(self, thread_id, account_id, mail_provider_id, is_seen):
        return self.db.query(self.entity).filter(and_(self.entity.thread_id == thread_id,
                                                      self.entity.account_id == account_id,
                                                      self.entity.email_account_provider_id == mail_provider_id)
                                                 ).update({"is_read": is_seen}, synchronize_session='fetch')

    def change_status(self, thread_id, is_closed):
        return self.db.query(self.entity).filter(self.entity.id == thread_id).update(
            {"is_closed": is_closed})
