from typing import Union, Optional, List

from fastapi import HTTPException, status

# from app.custom_classes.conversion_client import ContactModel, ConversionClient
from app.cruds.email_account_provider import EmailAccountProvidedCrud as dbEmailProvider
from app.cruds.email_thread import EmailThreadCrud as dbEmailThread
from app.custom_classes.contact_client import ContactClient, ContactModel
from app.custom_classes.date_generator import DateGenerator
from app.custom_classes.email.email_configuration import GmailUtilities
from app.custom_classes.email.email_configuration_data import GmailData
from app.enums import DateFilters
from db import models


# from db.schemas import NotificationMessage


class EmailService(object):

    @staticmethod
    def authenticate(db, authorize_code, account_id, provider: str = "Gmail"):
        provider_obj = None
        if provider == "Gmail":
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            try:
                email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                                  email=None,
                                                                                  authenticate=True)
                messages = email_communication_object.authenticate(authorize_code=authorize_code)
                return messages
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                    detail="Can not authenticate")
        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="No Such Provider Found")

    @staticmethod
    def get_all_email(db, email: str, account_id, provider: str = "Gmail", page_token=None):
        provider_obj = None
        if provider == "Gmail":
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            try:
                email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                                  email=email)
                messages = email_communication_object.get_all_mails(page_token=page_token)
                return messages
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                    detail="Can not get mails")
        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="No Such Provider Found")

    @staticmethod
    def get_updated_email(db, email: str, account_id, content_id: str, provider: str = "Gmail", is_data=True):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                              email=email)
            messages = email_communication_object.get_updated_messages(content_id=content_id)
            return messages
        else:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="No Such Provider Found")

    @staticmethod
    def get_all_thread(db, email: str, account_id, provider: str = "Gmail", is_data=False):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                              email=email)
            # print("Credential Found", email_communication_object.credential)
            if email_communication_object.credential:
                try:
                    thread = email_communication_object.get_all_thread(account_id=account_id)
                    if thread == [] or thread is None:
                        return {
                            "found": False,
                            'data': []
                        }
                    else:
                        return {
                            "found": True,
                            'data': thread
                        }
                except Exception as e:
                    print(e)
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                        detail="Internal Error Occurred While Syncing")
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Not Authenticated")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Such Provider Found")

    @staticmethod
    def get_thread_details(db, email: str, account_id, thread_id, provider: str = "Gmail", is_data=False):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:

            email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                              email=email)
            thread = email_communication_object.get_thread_details(account_id=account_id, thread_id=thread_id,
                                                                   email=email)
            return thread

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Such Provider Found")

    @staticmethod
    def send_mail(db, files, account_id, email_description, message_id, provider: str = "Gmail", is_data=False):
        """
        return sample
        {
            "id": "178da9b15fb194f3",
            "threadId": "178da9b15fb194f3",
            "labelIds": [
            "SENT"
            ]
        }
        """

        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            try:
                email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                                  email=email_description.from_email)

                send_email_details = email_communication_object.send_mail(files=files, account_id=account_id,
                                                                          email_description=email_description,
                                                                          message_id=message_id)
                # print(send_email_details)
                return send_email_details
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                    detail="Cannot sent mail")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Such Provider Found")

    @staticmethod
    def get_connected_mail_list(db, account_id, provider: str = "Gmail", is_data=False):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            try:
                email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                                  email=None,
                                                                                  authenticate=True)

                send_email_details = email_communication_object.get_connected_mail_list(account_id=account_id)
                # print(send_email_details)
                return send_email_details
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                    detail="Cannot get connected email list")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Such Provider Found")

    # def active_connected_mail(self, db, account_id, email, provider: str = "Gmail", is_data=False):
    #     provider_obj = None
    #     if provider == "Gmail" and is_data == True:
    #         provider_obj = GmailData(db=db, account_id=account_id)
    #     if provider == "Gmail" and is_data == False:
    #         provider_obj = Gmail(db=db, account_id=account_id)
    #     if provider is not None:
    #         try:
    #             email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
    #                                                                               email=email,
    #                                                                               authenticate=True)
    #
    #             send_email_details = email_communication_object.active_connected_mail(account_id=account_id,
    #                                                                                     email=email )
    #             # print(send_email_details)
    #             return send_email_details
    #         except:
    #             raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #                                 detail="Cannot get connected email list")
    #     else:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                             detail="No Such Provider Found")
    @staticmethod
    def change_label_seen(db, account_id, email, thread_id, provider: str = "Gmail", is_data=False):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            # try:
            email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                              email=email)

            change_label_response = email_communication_object.change_label_seen(account_id=account_id, email=email,
                                                                                 thread_id=thread_id)
            return change_label_response
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Such Provider Found")

    @staticmethod
    def get_attachment(db, account_id, email, attachment_id, message_id, thread_id, provider: str = "Gmail",
                       is_data=False):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            # try:
            email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                              email=email)

            attachment_response = email_communication_object.get_attachment(attachment_id=attachment_id, email=email,
                                                                            message_id=message_id,
                                                                            thread_id=thread_id)
            # print(send_email_details)
            return attachment_response

    # def assign_user_to_thread(self, db, user_id, thread_id, user):
    #     from app.cruds.email import Email as dbEmail
    #     crud_object = dbEmail(db=db)
    #     assignment_object = crud_object.create_email_thread_assignment(user_id=user_id, thread_id=thread_id)
    #     thread_details = crud_object.get_thread_by_id(thread_id=thread_id)
    #     if user_id is not None:
    #         print(NotificationMessage().user_assigned_to_email + str(thread_details.subject))
    #         try:
    #             ConversionClient().send_real_time_notification(receiver_account_id=user.account_id,
    #                                                            receiver_user_id=user_id,
    #                                                            notification_type="Email_Thread_Assigned",
    #                                                            notification_header="Email Thread Assigned",
    #                                                            notification_message=NotificationMessage().
    #                                                            user_assigned_to_email + " " + "'" + str(
    #                                                                thread_details.subject) + "'",
    #                                                            object_=thread_details,
    #                                                            token=user.token)
    #         except Exception as e:
    #             print(e)
    #     if assignment_object is not None:
    #         db.commit()
    #         return {
    #             "data":
    #                 {
    #                     "thread_id": assignment_object.thread_id,
    #                     "user_id": int(
    #                         assignment_object.assignee_id) if assignment_object.assignee_id is not None else None
    #                 }
    #         }
    #     else:
    #         return {
    #             "data": None
    #         }
    #
    # @staticmethod
    # def get_assigned_owner(db, thread_id):
    #     from app.cruds.email import Email as dbEmail
    #     crud_object = dbEmail(db=db)
    #     assignment_object = crud_object.get_assigned_owner(thread_id)
    #     if assignment_object:
    #         return {
    #             "data": {
    #                 "user_id": int(
    #                     assignment_object.assignee_id) if assignment_object.assignee_id is not None else None,
    #                 "thread_id": assignment_object.thread_id
    #             }
    #         }
    #     else:
    #         return {
    #             "data": {
    #                 "user_id": None,
    #                 "thread_id": thread_id
    #             }
    #         }
    #
    # def change_status(self, db, thread_id, is_closed):
    #     from app.cruds.email import Email as dbEmail
    #     crud_object = dbEmail(db=db)
    #     assignment_object = crud_object.change_status(thread_id, is_closed)
    #     if assignment_object:
    #         db.commit()
    #         return {
    #             "success": True
    #         }
    #     else:
    #         return {
    #             "success": False
    #         }
    #
    @staticmethod
    def name_splitter_plus(name: str, email):
        try:
            # print("Name ", name)
            if name is not None and not name == "":
                # first_name, last_name = name.split(" ", 2)
                # return first_name + "+" + last_name
                return name.replace(" ", "+")
            else:
                return email
        except Exception as e:
            print(e)
            return email
    #
    @staticmethod
    def _get_contact_name_by_conversion_call(db, account_id, email_):
        contact = ContactModel()
        contact.email = email_
        contact.account_id = account_id
        contact.input_source = "Gmail"
        contact.ref_id = ""
        contact.phone = ""
        from app.custom_classes.contact_client import ContactClient
        try:
            contact_id__ = ContactClient(db=db).create_or_get_existing_contact(model=contact).name
        except Exception as e:
            print(e)
            contact_id__ = email_
        # print("Name", contact_id__, contact.id)

        return contact_id__

    def get_filter(self, db, is_closed, contact_email, date, email, account_id):

        crud_object = dbEmailProvider(db=db)
        date_ranges = None
        if not date == DateFilters.ALL_TIME:
            # print("NOT ALL TIME")
            date_ranges = DateGenerator(date)
        # print(date_ranges)
        email_provider_id = crud_object.get_email_account_provider_table_id_by_email(email=email, account_id=account_id)
        assignment_object = dbEmailThread(db=db).get_filtered_data(is_closed, contact_email, date_ranges,
                                                                   account_id, email_provider_id)

        if assignment_object:
            db.commit()

            return {
                "success": True,
                "data": [
                    {
                        "id": thread.id,
                        "subject": thread.subject,
                        "userImage": "https://ui-avatars.com/api/?name=" +
                                     self._get_contact_name_by_conversion_call(
                                         db=db,
                                         account_id=account_id,
                                         email_=GmailUtilities(db=db, account_id=account_id).get_email_and_name(
                                             thread.latest_message_email)[
                                             1])
                        if
                        self._get_contact_name_by_conversion_call(
                            db=db,
                            account_id=account_id,
                            email_=GmailUtilities(db=db, account_id=account_id).get_email_and_name(
                                thread.latest_message_email)[
                                1])
                        else
                        "https://ui-avatars.com/api/?name=" +
                        GmailUtilities(db=db, account_id=account_id).get_email_and_name(thread.latest_message_email)[1],
                        "isOnline": False,
                        "isSeen": thread.is_read,
                        "name": self._get_contact_name_by_conversion_call(
                            db=db, account_id=account_id,
                            email_=GmailUtilities(db=db, account_id=account_id).get_email_and_name(
                                thread.latest_message_email)[
                                1]),
                        "contact_email":
                            GmailUtilities(db=db, account_id=account_id).get_email_and_name(
                                thread.latest_message_email)[1],
                        "date": thread.sync_datetime,
                        "channel": "Email",
                        "is_closed": thread.is_closed,
                        # "user_id": self._checking_user_id(db, thread),
                        "contact_id": EmailService.__get_contact_id_by_conversion_call(account_id, db, thread)
                    } for thread in assignment_object]
            }
        else:
            return {
                "success": False
            }

    # @staticmethod
    # def _checking_user_id(db, thread):
    #     from app.cruds.email_account_provider import EmailAccountProvidedCrud as dbEmail
    #     user_id = None
    #     if dbEmail(db=db).get_assigned_owner(thread_id=thread.id) is not None:
    #         user_id = dbEmail(db=db).get_assigned_owner(thread_id=thread.id).assignee_id
    #         if user_id is not None:
    #             user_id = int(user_id)
    #     else:
    #         user_id = None
    #     return user_id

    @staticmethod
    def __get_contact_id_by_conversion_call(account_id, db, thread):
        contact = ContactModel()
        contact.email = GmailUtilities(db=db, account_id=account_id).get_email_and_name(thread.latest_message_email)[1]
        contact.account_id = account_id
        contact.input_source = "Gmail"
        contact.ref_id = ""
        contact.name = GmailUtilities(db=db, account_id=account_id).get_email_and_name(thread.latest_message_email)[0]
        contact.phone = ""
        try:
            contact_id__ = ContactClient(db).create_or_get_existing_contact(model=contact).id
        except Exception as e:
            print(e)
            contact_id__ = 1
        return contact_id__

    @staticmethod
    def mark_seen_status(db, account_id, email, thread_id, is_seen, provider="Gmail", is_data=False):
        provider_obj = None
        if provider == "Gmail" and is_data == True:
            provider_obj = GmailData(db=db, account_id=account_id)
        if provider == "Gmail" and is_data == False:
            provider_obj = GmailUtilities(db=db, account_id=account_id)
        if provider is not None:
            # try:
            email_communication_object = EmailCommunicationViaProviderService(mail_provider_object=provider_obj,
                                                                              email=email)
            try:
                change_label_response = email_communication_object.mark_seen_status(account_id=account_id, email=email,
                                                                                    thread_id=thread_id,
                                                                                    is_seen=is_seen)
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail="Cannot Update Mail Read Status")
            return change_label_response == 1
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="No Such Provider Found")


class EmailCommunicationViaProviderService:

    def __init__(self, mail_provider_object: Union[GmailUtilities], email: Union[None, str], from_file: bool = False,
                 authenticate=False):
        self.email = email
        self.from_file = from_file
        self.mail_provider_object: Union[GmailUtilities] = mail_provider_object
        # print(authenticate)
        if not authenticate:
            self.credential = self.mail_provider_object.get_credentials(email, from_file)

    def authenticate(self, authorize_code):
        token_pickle = self.mail_provider_object.authenticate(authorize_code)
        return token_pickle

    def get_all_mails(self, page_token: Optional[str] = None):
        messages = self.mail_provider_object.get_message_by_credentials(self.credential, self.email, self.from_file,
                                                                        page_token)
        return messages

    def get_updated_messages(self, content_id: str):
        messages = self.mail_provider_object.get_updated_message_by_credential(self.credential, content_id, self.email)
        return messages

    def get_all_thread(self, account_id):
        thread = self.mail_provider_object.get_thread_by_credentials(credential=self.credential, email=self.email,
                                                                     from_file=self.from_file, account_id=account_id)
        return thread

    def get_thread_details(self, account_id, thread_id, email):
        messages: List[models.EmailDetails] = self.mail_provider_object.get_thread_details_by_credentials(
            account_id=account_id,
            thread_id=thread_id,
            email_=email)
        return messages

    def send_mail(self, files, account_id, email_description, message_id):
        send_mail_response = self.mail_provider_object.send_mail(credential=self.credential,
                                                                 files=files,
                                                                 account_id=account_id,
                                                                 email_description=email_description,
                                                                 message_id=message_id)
        return send_mail_response

    def get_connected_mail_list(self, account_id):
        mail_list = self.mail_provider_object.get_connected_mail_list(account_id=account_id)
        return mail_list

    def change_label_seen(self, account_id, email, thread_id):
        change_label_response = self.mail_provider_object.change_label_seen(account_id=account_id, email=email,
                                                                            thread_id=thread_id,
                                                                            credential=self.credential,
                                                                            from_file=-self.from_file)
        return change_label_response

    def get_attachment(self, attachment_id, email, message_id, thread_id):
        attachment_response = self.mail_provider_object.get_attachment(attachment_id=attachment_id,
                                                                       email=email,
                                                                       message_id=message_id,
                                                                       thread_id=thread_id,
                                                                       credential=self.credential,
                                                                       from_file=-self.from_file)
        return attachment_response

    def mark_seen_status(self, account_id, email, thread_id, is_seen):
        mark_seen_status_response = self.mail_provider_object.mark_seen_status(account_id=account_id, email=email,
                                                                               thread_id=thread_id,
                                                                               is_seen=is_seen,
                                                                               credential=self.credential,
                                                                               from_file=-self.from_file)
        return mark_seen_status_response
