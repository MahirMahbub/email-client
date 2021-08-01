import base64
import calendar
import io
import json
import os.path
import pickle
from datetime import datetime, timedelta
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itertools import chain
from typing import Optional, List

import google_auth_httplib2
import httplib2
from dateutil import parser
from fastapi import UploadFile
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from oauth2client import client
from oauth2client.client import OAuth2Credentials
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.cruds.email_account_provider import EmailAccountProvidedCrud as dbEmailProvider
from app.cruds.email_thread import EmailThreadCrud as dbEmailThread
from app.cruds.email_details import EmailDetailsCrud as dbEmailDetails
from app.cruds.email_receiver import EmailReceiverCrud as dbEmailReceiver
from app.cruds.email_attachment import EmailAttachmentCrud as dbEmailAttachment
from app.schemas import EmailCreate
from app.custom_classes.contact_client import ContactModel, ContactClient
from db.models import EmailAccountProvided
# If modifying these scopes, delete the file token.pickle.
from db.models import EmailCommunicationType, EmailReceiverType

# import datetime as DateTime
GOOGLE_SCOPES = os.getenv("GOOGLE_SCOPES").split(",")
# SCOPES = os.getenv('GMAIL_AUTH_SCOPE').split(",")
CLIENT_SECRET_FILE = os.getcwd() + '/app/custom_classes/email/credentials.json'


class GmailUtilities(object):

    def __init__(self, db: Session, account_id: int) -> None:
        self.db = db
        self.account_id = account_id
        self.provider = "Gmail"

    def authenticate(self, authorize_code):
        credentials = client.credentials_from_clientsecrets_and_code(
            CLIENT_SECRET_FILE, GOOGLE_SCOPES, authorize_code)
        credential_to_object = self._credential_object_to_json(credentials)
        object_to_pickle = self._object_to_pickle(credentials)
        token_email = credential_to_object["id_token"]["email"]
        add_token_to_db = self.create_credential_object(email=token_email,
                                                        token=object_to_pickle,
                                                        )
        # set_active_email = self.set_active_email(email=token_email)
        self.db.commit()
        return add_token_to_db

    @staticmethod
    def get_credential_object_from_file():
        if os.path.exists('app/custom_classes/email/token.pickle'):
            with open('app/custom_classes/email/token.pickle', 'rb') as token:
                creds = pickle.load(token)
            return creds
        else:
            return None

    def set_active_email(self, email):
        try:
            crud_object = dbEmailProvider(db=self.db)
            crud_object.set_active_email(email=email,
                                         account_id=self.account_id)
            self.db.flush()
        except Exception as e:
            print(e)
            return False
        return True

    def create_credential_object(self, email: str, token: pickle):
        try:
            crud_object = dbEmailProvider(db=self.db)
            crud_object.create_email_credential(email=email,
                                                account_id=self.account_id,
                                                token=token,
                                                provider=self.provider)
            self.db.flush()
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    def get_dummy_last_sync_time_epoch_from_date(past_date=1):
        return calendar.timegm((datetime.today() - timedelta(days=past_date)).timetuple())

    @staticmethod
    def _pickle_to_object(token: pickle):
        deserialized_token = pickle.loads(token)
        return deserialized_token

    @staticmethod
    def _object_to_pickle(token: object):
        serialized_token = pickle.dumps(token)
        return serialized_token

    @staticmethod
    def _credential_object_to_json(credential: Credentials):
        return json.loads(credential.to_json())

    def update_credential_object(self, email: str, token: pickle):
        try:
            crud_object = dbEmailProvider(db=self.db)
            crud_object.update_email_credential(email=email,
                                                account_id=self.account_id,
                                                token=token)
            self.db.flush()
        except Exception as e:
            print(e)
            return False
        return True

    def mail_log_in(self, *, email: str, service_name: Optional[str] = 'gmail', credential):
        # print("Can not find Email Token", credential)
        # if not credentials or not credentials.valid:
        if credential and credential.expired and credential.refresh_token:
            credential.refresh(Request())
            self.update_credential_object(email=email, token=pickle.dumps(credential))
        else:
            assert "Credential Not Found"
        service = build(service_name, 'v1', credentials=credential)
        http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())
        # service.users().label().create(userId=self.user_id,body=).execute()
        return service, http, credential

    def get_all_messages(self, service: build,
                         http: google_auth_httplib2.AuthorizedHttp,
                         created_date: str,
                         page_token: Optional[str] = None):

        message_ids_object = self.get_message_list_object(created_date, page_token, service)
        if message_ids_object is not None:
            gmail_msg_list = message_ids_object.execute()
            message_ids = gmail_msg_list["messages"]

            messages_details_list = self.get_message_details_in_batch_from_message_list(http, message_ids, service)
            next_page_token = gmail_msg_list.get("nextPageToken", -1)
            if next_page_token == -1:
                return {
                    "found": True,
                    "data": {
                        "messages": messages_details_list,
                        "nextPageToken": None,
                        "resultSizeEstimate": gmail_msg_list["resultSizeEstimate"]
                    }
                }
            else:
                return {
                    "found": True,
                    "data": {
                        "messages": messages_details_list,
                        "nextPageToken": gmail_msg_list["nextPageToken"],
                        "resultSizeEstimate": gmail_msg_list["resultSizeEstimate"]
                    }
                }
        else:
            return {
                "found": False,
                "data": None
            }

    def get_all_thread(self, service: build,
                       http: google_auth_httplib2.AuthorizedHttp,
                       last_sync_date: str,
                       page_token: Optional[str] = None):
        thread_ids_object = self.get_thread_list_object(last_sync_date, page_token, service)
        if thread_ids_object is not None:
            gmail_thread_list = thread_ids_object.execute()
            thread_ids = gmail_thread_list["threads"]

            thread_details_list = self.get_thread_details_from_thread_list(http, thread_ids, service)
            next_page_token = gmail_thread_list.get("nextPageToken", -1)
            if next_page_token == -1:
                return {
                    "found": True,
                    "data": {
                        "thread": thread_details_list,
                        "nextPageToken": None,
                        "resultSizeEstimate": gmail_thread_list["resultSizeEstimate"]
                    }
                }
            else:
                return {
                    "found": True,
                    "data": {
                        "thread": thread_details_list,
                        "nextPageToken": gmail_thread_list["nextPageToken"],
                        "resultSizeEstimate": gmail_thread_list["resultSizeEstimate"]
                    }
                }
        else:
            return {
                "found": False,
                "data": None
            }

    def get_updated_message(self, service: build, http, content_id):

        message_list = []
        message_history_obj = self.get_message_history_object(service=service, content_id=content_id,
                                                              history_types=["messageAdded"])
        if message_history_obj is not None:
            gmail_history = message_history_obj.execute()
            # print(gmail_history)
            histories = gmail_history["history"]
            for history in histories:
                message_list += history["messages"]
        # print(message_list)
        messages_details_list = self.get_message_details_in_batch_from_message_list(http, message_list, service)
        if messages_details_list:
            return {
                "found": True,
                "data": messages_details_list
            }
        else:
            return {
                "found": False,
                "data": None
            }

    @staticmethod
    def get_thread_details_from_thread_list(http, thread_ids, service):
        thread_list = []

        def get_gmail_thread(request_id, response, exception):
            if exception is not None:
                print('thread.get failed for thread id {}: {}'.format(request_id, exception))
            else:
                thread_list.append(response)

        batch = service.new_batch_http_request(callback=get_gmail_thread)
        for thread in thread_ids:
            batch.add(service.users().threads().get(userId='me', id=thread['id'], format="minimal"),
                      request_id=thread['id'])
        batch.execute(http=http)
        return thread_list

    @staticmethod
    def _get_updated_message_list_by_last_sync_date(last_sync_date, service, http):
        thread_list = []
        thread_id_objects: build = service.users().threads().list(userId='me',
                                                                  q="after: " + str(last_sync_date),
                                                                  maxResults=90).execute()
        if not thread_id_objects.get('threads', -1) == -1:
            thread_list += thread_id_objects['threads']
        else:
            return None
        while not thread_id_objects.get('nextPageToken', -1) == -1:
            thread_id_objects = service.users().threads().list(userId='me',
                                                               pageToken=thread_id_objects['nextPageToken'],
                                                               q="after: " + str(last_sync_date),
                                                               maxResults=90).execute()
            thread_list += thread_id_objects["threads"]

        messages_list = []

        def get_gmail_thread_message(request_id, response, exception):
            if exception is not None:
                print('thread.get failed for thread id {}: {}'.format(request_id, exception))
            else:
                messages_list.append((response['messages']))

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        thread_list_chunk = list(divide_chunks(thread_list, 90))
        for chunk_thread_list in thread_list_chunk:
            batch = service.new_batch_http_request(callback=get_gmail_thread_message)
            for thread in chunk_thread_list:
                batch.add(service.users().threads().get(userId='me', id=thread['id']),
                          request_id=thread['id'])
            batch.execute()
        messages_list = list(chain.from_iterable(messages_list))
        return messages_list

    @staticmethod
    def get_message_list_object(created_date, page_token, service):
        if page_token is None:
            message_ids_object = service.users().messages().list(userId='me',
                                                                 q="from:me OR in:inbox to:me category:personal after: " + str(
                                                                     created_date))
        else:
            message_ids_object = service.users().messages().list(userId='me', pageToken=page_token,
                                                                 q="from:me OR in:inbox to:me category:personal after: " + str(
                                                                     created_date))
        return message_ids_object

    @staticmethod
    def get_thread_list_object(created_date, page_token, service):
        if page_token is None:
            thread_ids_object = service.users().threads().list(userId='me',
                                                               q="from:me OR in:inbox to:me category:personal after: " + str(
                                                                   created_date))
        else:
            thread_ids_object = service.users().threads().list(userId='me', pageToken=page_token,
                                                               q="in:inbox after: " + str(created_date))
        # print(thread_ids_object)
        return thread_ids_object

    @staticmethod
    def get_message_history_object(service, content_id, history_types):
        message_ids_object = service.users().history().list(userId='me', startHistoryId=content_id,
                                                            historyTypes=history_types)
        return message_ids_object

    @staticmethod
    def get_message_details_in_batch_from_message_list(http, message_ids, service):
        messages_list = []

        def get_gmail_message(request_id, response, exception):
            if exception is not None:
                print('messages.get failed for message id {}: {}'.format(request_id, exception))
            else:
                messages_list.append(response)

        if message_ids is None:
            return []

        batch = service.new_batch_http_request(callback=get_gmail_message)
        for msg_id in message_ids:
            batch.add(service.users().messages().get(userId='me', id=msg_id['id']), request_id=msg_id['id'])
        batch.execute()
        # for i in messages_list:
        #     if i["threadId"] == "177440ec04b2401e":
        #         print(i["snippet"])
        return messages_list

    @staticmethod
    def build_sdk(*, service_name: Optional[str] = 'gmail', credential):
        print(service_name)
        # http = httplib2.Http()
        # http = credential.authorize(http)
        # service = build('gmail', 'v1', credentials=credential)
        # # http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())
        # return http, service
        service = build(service_name, 'v1', credentials=credential)
        http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())
        return http, service

    def get_message_by_credentials(self, credential, email, from_file, page_token):
        if not credential or credential.invalid:
            try:
                service, http, credential_object = self.mail_log_in(email=email, credential=credential)
            except:
                return None
        else:
            http, service = self.build_sdk(credential=credential)
        if from_file:
            created_date = self.get_dummy_last_sync_time_epoch_from_date()
        else:
            crud_object = dbEmailProvider(db=self.db)
            created_date = crud_object.get_last_sync_epoch_from_email_communication_object(email=email,
                                                                                           account_id=self.account_id)
        messages = self.get_all_messages(service=service, http=http,
                                         created_date=created_date, page_token=page_token)
        return messages

    def get_updated_message_by_credential(self, credential, content_id, email):
        if not credential or credential.invalid:
            try:
                service, http, credential_object = self.mail_log_in(email=email, credential=credential)
            except:
                return None
        else:
            http, service = self.build_sdk(credential=credential)
        messages = self.get_updated_message(service=service, http=http, content_id=content_id)
        return messages

    def get_thread_by_credentials(self, credential, email, from_file, account_id):
        # data = []
        email_provider_crud_object = dbEmailProvider(db=self.db)
        from_file = False
        http = None
        if not credential or credential.invalid:
            try:
                service, http, credential = self.mail_log_in(email=email, credential=credential)
            except:
                return None
        elif credential is None:
            return None
        else:
            service = build('gmail', 'v1', credentials=credential)
            http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())
        if from_file:
            last_sync_date = self.get_dummy_last_sync_time_epoch_from_date()
        else:
            email_provider_crud_object = dbEmailProvider(db=self.db)
            last_sync_date = email_provider_crud_object.get_last_sync_epoch_from_email_communication_object(email=email,
                                                                                                            account_id=self.account_id)
        latest_message = self._get_updated_message_list_by_last_sync_date(last_sync_date=last_sync_date,
                                                                          service=service,
                                                                          http=http)  # (service.users().messages().get(userId='me', id=msg_id['id']), request_id=msg_id['id'])
        current_time = calendar.timegm(datetime.now().timetuple())
        email_provider_crud_object.update_last_sync_date(current_time, email, self.account_id)
        email_provider_id = email_provider_crud_object.get_email_account_provider_table_id_by_email(email=email,
                                                                                                    account_id=account_id)
        if not latest_message == [] and latest_message is not None:
            # latest_message_details = self.get_message_details_in_batch_from_message_list(http, latest_message, service)
            attributes = ["From", "Date", "Subject", "To", "Cc", "Bcc"]
            for message in latest_message:
                existing_message = dbEmailDetails(db=self.db).get_message_by_message_id(
                    message_id=message.get("id", None))
                if existing_message:
                    continue
                data_from_header = self._get_attributes_from_header(message=message, attributes=attributes)
                # print(message, data_from_header)
                data_from_header["message_id"] = message.get("id", None)
                thread_id = message.get("threadId", None)
                thread_found = dbEmailThread(db=self.db).get_thread_by_thread_id(thread_id, account_id,
                                                                                 email_provider_id)
                if thread_found is None and not thread_found == []:
                    email_thread_object = dbEmailThread(db=self.db).create_email_thread(account_id, email, thread_id)
                else:
                    email_thread_object = thread_found

                snippet = ""
                subject = ""
                from_email = ""
                is_read = None

                # modified_date = email_thread_object.sync_datetime.replace(tzinfo=pytz.UTC)
                # if modified_date is not None:
                #     modified_date = modified_date - DateTime.timedelta(seconds=5)

                data_from_header["thread_id"] = email_thread_object.id
                data_from_header["historyId"] = message.get("historyId", None)
                data_from_header.update(self.get_message_body_and_attachments(message))
                data_from_header["is_read"]: bool = False if 'UNREAD' in message.get("labelIds", []) else True
                data_from_header[
                    "email_account_provider_id"] = \
                    email_provider_crud_object.get_email_account_provider_table_id_by_email(email=email,
                                                                                            account_id=account_id)[0]

                data_from_header["type"] = self.get_email_communication_type(from_email=data_from_header["From"],
                                                                             email=email,
                                                                             thread_id=data_from_header["thread_id"],
                                                                             message_id=data_from_header["message_id"])
                # if modified_date is None:
                #     modified_date = self._string_date_to_date_object(data_from_header["Date"])
                #     snippet = data_from_header["body"]
                #     # print(snippet)
                #     subject = data_from_header["Subject"]
                #     from_email = data_from_header["From
                #     is_read = data_from_header["is_read"]
                #     # print("HERE")
                # elif modified_date <= self._string_date_to_date_object(data_from_header["Date"]):
                #         modified_date = self._string_date_to_date_object(data_from_header["Date"])
                #         snippet = data_from_header["body"]
                #         subject = data_from_header["Subject"]
                #         from_email = data_from_header["From"]
                #         is_read = data_from_header["is_read"]
                # print("Header: ",data_from_header)
                modified_date = self._string_date_to_date_object(data_from_header["Date"])
                snippet = data_from_header["body"]
                subject = data_from_header["Subject"]
                from_email = data_from_header["From"]
                is_read = data_from_header["is_read"]
                # print("HERE")
                """
                Write Contact Extract and DB operation here 
                """
                name__, email_addr = self.get_email_and_name(data_from_header["From"])
                self.create_contact_from_from_and_reciepent_list(data_from_header, account_id)
                contact_id__ = None

                contact = ContactModel()
                contact.name = name__
                contact.account_id = account_id
                contact.input_source = "Gmail"
                contact.phone = ""
                if not email_addr == email:
                    contact.email = email_addr

                    try:
                        contact_id__ = ContactClient(db=self.db).create_or_get_existing_contact(model=contact).id
                    except Exception as e:
                        contact_id__ = 0
                else:
                    contact.email = self.get_email_and_name(data_from_header["To"].split(",")[0])[1]
                    try:
                        contact_id__ = ContactClient(db=self.db).create_or_get_existing_contact(model=contact).id
                    except Exception as e:
                        contact_id__ = 0
                email_details_object = dbEmailDetails(db=self.db).create_message_details(
                    subject=data_from_header["Subject"],
                    from_address=self.get_email_and_name(
                        data_from_header["From"])[1],
                    message_id=data_from_header["message_id"],
                    thread_id=data_from_header["thread_id"],
                    email_account_provider_id=data_from_header[
                        "email_account_provider_id"],
                    body=data_from_header["body"],
                    operation_datetime=self._string_date_to_date_object(
                        data_from_header["Date"]),
                    history_id=data_from_header["historyId"],
                    is_read=data_from_header["is_read"],
                    type_=data_from_header["type"],
                    contact_id=contact_id__,
                    account_id=account_id)
                email_thread_object.snippet = snippet
                # print("SUBJECT: ",subject )
                email_thread_object.sync_datetime = modified_date
                email_thread_object.subject = subject
                if not self.get_email_and_name(from_email)[1] == email:
                    email_thread_object.latest_message_email = from_email
                else:
                    email_thread_object.latest_message_email = data_from_header["To"].split(",")[0]
                email_thread_object.is_read = is_read

                self.create_to_cc_bcc_address(dbEmailReceiver(db=self.db), data_from_header, email_details_object)

                dbEmailAttachment(db=self.db).create_email_attachment(email_id=email_details_object.id,
                                                                      attachments=data_from_header["attachment"])
                self.db.commit()

    @staticmethod
    def _string_date_to_date_object(string):
        date = parser.parse(string)
        # date = date.replace(tzinfo=DateTime.timezone.utc)
        return date.astimezone()
        # return date

    @staticmethod
    def decode_base64(data, altchars=b'+/'):
        """Decode base64, padding being optional.

        :param data: Base64 data as an ASCII byte string
        :returns: The decoded byte string.

        """
        # data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
        # missing_padding = len(data) % 4
        # if missing_padding:
        #     data += b'=' * (4 - missing_padding)
        return base64.urlsafe_b64decode(data)

    def create_to_cc_bcc_address(self, crud_object, data_from_header, email_details_object):
        to_address_list = self.extract_to_address(address=data_from_header["To"])
        crud_object.create_address_receiver(email_id=email_details_object.id,
                                            address_list=to_address_list,
                                            type_=EmailReceiverType.TO)
        cc_address_list = self.extract_to_address(address=data_from_header["Cc"])
        crud_object.create_address_receiver(email_id=email_details_object.id,
                                            address_list=cc_address_list,
                                            type_=EmailReceiverType.CC)
        bcc_address_list = self.extract_to_address(address=data_from_header["Bcc"])
        crud_object.create_address_receiver(email_id=email_details_object.id,
                                            address_list=bcc_address_list,
                                            type_=EmailReceiverType.BCC)

    def get_message_body_and_attachments(self, message):
        data = {"attachment": [], "body": ""}
        payload = message.get("payload", None)
        if payload is None:
            return data
        message_part = payload.get("parts", None)
        # if message_part is None:
        #     return data
        if message_part is None:

            body = payload.get("body", None)
            if body is not None:
                dat = body.get("data", "")

                if not dat == "" and dat is not None:
                    data["body"] = dat
                    # print("DATA: ", data["body"], message["historyId"])

        elif message_part is not None:
            for part in message_part:
                body_snippet = self.get_body_from_parts(part)
                if body_snippet is not None:
                    data["body"] = body_snippet
                attachment_data = self.get_attachments_from_part(part)
                if attachment_data is not None:
                    data["attachment"].append(attachment_data)
                if part["mimeType"] == "multipart/alternative":
                    inner_message_part = part["parts"]
                    for inner_part in inner_message_part:

                        body_snippet = self.get_body_from_parts(inner_part)
                        if body_snippet is None:
                            data["body"] = body_snippet
                        inner_attachment_data = self.get_attachments_from_part(inner_part)
                        if inner_attachment_data is not None:
                            data["attachment"].append(inner_attachment_data)
        return data

    @staticmethod
    def get_attachments_from_part(part):
        if not part["filename"] == "":
            response = {
                "file_name": part["filename"],
                "attachment_id": part["body"]["attachmentId"],
                "file_type": part["mimeType"]
            }
            # print(response)
            return response
        else:
            return None
            # subject = self.get_subject_of_email(message)

    @staticmethod
    def get_body_from_parts(part):
        data = None
        if part["mimeType"] == "text/html":
            data = part["body"]["data"]
            # if data != "":
            #     data = base64.urlsafe_b64decode(bytes(data, 'utf-8'))
        elif part["mimeType"] == "text/plain":
            data = part["body"]["data"]
        # print("Body: ")
        # print(data)
        # print("PART DATA:", data)
        return data

    def get_credentials(self, email, from_file=False):
        credential = None
        if not from_file:
            crud_object = dbEmailProvider(db=self.db)
            credential_object: EmailAccountProvided = crud_object.get_credential_object(email=email,
                                                                                        account_id=self.account_id)
            if credential_object:
                credential = credential_object
            else:
                credential = None
        else:
            credential = self.get_credential_object_from_file()
        return credential

    @staticmethod
    def _get_attributes_from_header(message, attributes):
        attributes_lower = [x.lower() for x in attributes]
        payload = message.get("payload", {})
        data = {}
        if not payload == {}:
            headers = payload.get("headers", [])
            if headers:
                for header in headers:
                    if header["name"] in attributes:
                        data[header["name"]] = header["value"]
                    elif header["name"] in attributes_lower:
                        data[header["name"].capitalize()] = header["value"]
                    # if header["name"] == "from":
                    #     data["From"] = header["value"]

        for attr in attributes:
            if attr not in data.keys():
                data[attr] = None
        # print(data)
        return data

    def get_email_communication_type(self, from_email, email, thread_id, message_id):

        if thread_id == message_id:
            if email in from_email:
                return EmailCommunicationType.SEND
            elif not email in from_email:
                return EmailCommunicationType.RECEIVE
            else:
                return EmailCommunicationType.REPLY

    def get_thread_details_by_credentials(self, account_id, thread_id, email_):
        email_provider_id = dbEmailProvider(db=self.db).get_email_account_provider_table_id_by_email(email=email_,
                                                                                                     account_id=account_id)
        messages = dbEmailDetails(self.db).get_message_list_by_thread_id(account_id=account_id, thread_id=thread_id,
                                                                         email_provider_id=email_provider_id)
        message_list = []
        for message in messages:
            response = {}
            response["id"] = message.id
            response["messageId"] = message.message_id
            response["threadId"] = message.thread_id
            response["subject"] = message.subject
            response["from"] = self.get_email_and_name(message.from_address)[1]
            response["name"] = self._get_contact_name_by_conversion_call(
                account_id, message.from_address).replace('"', '') \
                if self._get_contact_name_by_conversion_call(
                account_id, message.from_address) is not None else None
            from app.services.communication.email import EmailService
            response["userImage"] = "https://ui-avatars.com/api/?name=" + EmailService().name_splitter_plus(
                self._get_contact_name_by_conversion_call(account_id, message.from_address).replace('"', '')
                if self._get_contact_name_by_conversion_call(account_id, message.from_address) is not None else None,
                self.get_email_and_name(message.from_address)[1])
            #                     EmailService().name_splitter_plus(
            # Gmail(db=self.db, account_id=account_id)._get_email_and_name(message.from_address)[0],
            # Gmail(db=self.db, account_id=account_id)._get_email_and_name(message.from_addressl)[1]),
            response["to"] = ','.join(map(str, [address[0] for address in
                                                dbEmailReceiver(db=self.db).get_to_receivers_address_by_email_id(
                                                    email_id=message.id)]))
            response["cc"] = ','.join(map(str, [address[0] for address in
                                                dbEmailReceiver(db=self.db).get_cc_receivers_address_by_email_id(
                                                    email_id=message.id)]))
            response["bcc"] = ','.join(map(str, [address[0] for address in
                                                 dbEmailReceiver(db=self.db).get_bcc_receivers_address_by_email_id(
                                                     email_id=message.id)]))
            response["date"] = message.operation_datetime
            response["channel"] = "Email"
            response["attachments"] = dbEmailAttachment(db=self.db).get_attachments_by_email_id(email_id=message.id)
            # try:
            response["message"] = self.decode_base64(message.body) if (
                    message.body is not None and not message.body == "") else None
            # except :
            #     response["message"] = message.body
            #     print(message.body)

            message_list.append(response)

        return message_list

    @staticmethod
    def _get_contact_name_by_conversion_call(account_id, email_):
        contact_id__ = ""
        contact = ContactModel()
        contact.email = email_
        contact.account_id = account_id
        contact.input_source = "Gmail"
        contact.ref_id = ""
        contact.phone = ""
        try:
            contact_id__ = ContactClient().create_or_get_existing_contact(model=contact).name
        except Exception as e:
            print(e)
            contact_id__ = email_
        # print("Name", contact_id__, contact.id)

        return contact_id__

    def extract_to_address(self, address):
        if address is None:
            return []
        else:
            address_list = address.split(",")

            return [self.get_email_and_name(addr)[1] for addr in address_list]

    @staticmethod
    def get_email_and_name(email):
        temp = email.split("<")
        if (len(temp)) > 1:
            temp[1] = temp[1].replace(">", "")
            temp[0] = temp[0].rstrip()

            return temp
        else:
            return None, temp[0]

    def send_mail(self, credential: OAuth2Credentials, files, account_id: int, email_description: EmailCreate,
                  message_id=None):
        service = None
        http = None
        if not credential or credential.invalid:
            try:
                service, http, credential = self.mail_log_in(email=email_description.from_email,
                                                             credential=credential)
            except  Exception as e:
                print("Can not create SDK, Why: ", e)
                # return None
        elif credential is None:
            return None
        else:
            # http, service = self.build_sdk(credential)
            service = build('gmail', 'v1', credentials=credential)
        header_dict = {"In-Reply-To": None, "References": None, "thread_id": None, "Message-Id": None}

        if message_id is not None:
            message = service.users().messages().get(userId="me", id=message_id).execute(http=http)
            if message is not None:
                header_dict["thread_id"] = message["threadId"]
                headers = message["payload"]["headers"]
                # print(headers)
                for element in headers:
                    # print(element)
                    if element["name"] == "In-Reply-To":
                        header_dict["In-Reply-To"] = element["value"]
                    # else:
                    #     header_dict["In-Reply-To"] = message_id
                    if element["name"] == "References":
                        header_dict["References"] = element["value"]
                    if element["name"] == "Message-Id" or element["name"] == "Message-ID":
                        header_dict["Message-Id"] = element["value"]
                    # else:
                    #     header_dict["References"] = message_id
        # print("Header1", header_dict)
        if header_dict["In-Reply-To"] is None or header_dict["In-Reply-To"] == "":
            header_dict["In-Reply-To"] = header_dict["Message-Id"]
        if header_dict["References"] is None or header_dict["References"] == "":
            header_dict["References"] = header_dict["Message-Id"]
        # print("Header2", header_dict)
        try:
            body = self.create_message_with_attachment(email_description.from_email, email_description.to_email,
                                                       email_description.cc_email, email_description.bcc_email,
                                                       email_description.subject, email_description.email_description,
                                                       files, in_reply_to=header_dict["In-Reply-To"],
                                                       reference=header_dict["References"],
                                                       thread_id=header_dict['thread_id'],
                                                       message_id=message_id
                                                       )
        except Exception as error:
            print('An error occurred: %s' % error)
            raise error
        try:
            # print('Body: ', body)
            message = service.users().messages().send(userId="me", body=body).execute(http=http)
            return message
        except Exception as error:
            print('An error occurred: %s' % error)

    def create_message_with_attachment(self, from_email, to_list, cc_list, bcc_list, subject, body,
                                       file_list: List[UploadFile], in_reply_to, reference, thread_id=None,
                                       message_id=None):

        message = MIMEMultipart()

        message['to'] = ", ".join([self.get_email_and_name(email)[1] for email in to_list])
        if cc_list:
            message['cc'] = ", ".join([self.get_email_and_name(email)[1] for email in cc_list])
        if bcc_list:
            message['bcc'] = ", ".join([self.get_email_and_name(email)[1] for email in bcc_list])
        message['from'] = from_email
        if subject is not None:
            message['subject'] = subject
        # if in_reply_to is not None:
        #     message['In-Reply-To'] = in_reply_to
        #     message['References'] = reference

        msg = MIMEText(body, "html")
        message.attach(msg)
        # msg = MIMEText(body, "plain")
        # message.attach(msg)
        if file_list:
            for file in file_list:
                content_type = file.content_type
                if content_type is None:
                    content_type = 'application/octet-stream'
                main_type, sub_type = content_type.split('/', 1)
                # if main_type == 'text':
                #     msg = MIMEText(file.file.read().as_string(), _subtype=sub_type)
                # elif main_type == 'image':
                #     msg = MIMEImage(file.file.read(), _subtype=sub_type)
                # elif main_type == 'audio':
                #     msg = MIMEAudio(file.file.read(), _subtype=sub_type)
                # else:
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(file.file.read())
                filename = file.filename
                msg.add_header('Content-Disposition', 'attachment', filename=filename)
                # if message_id is not None:
                # message['In-Reply-To']

                message.attach(msg)
        message.add_header('References', reference)
        message.add_header('In-Reply-To', in_reply_to)
        if thread_id is None:
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        else:
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode(), "threadId": thread_id}

    def get_connected_mail_list(self, account_id):
        crud_object = dbEmailProvider(db=self.db)
        email_address_list = crud_object.get_connected_mail_list_by_account_id(account_id)
        if email_address_list:
            return {
                "exist": True,
                "email": email_address_list
            }
        else:
            return {
                "exist": False,
                "email": email_address_list
            }

    def change_label_seen(self, account_id, email, thread_id, credential, from_file=False):
        data = []
        from_file = False
        http = None
        if not credential or credential.invalid:
            try:
                service, http, credential = self.mail_log_in(email=email, credential=credential)
            except:
                return None
        elif credential is None:
            return None
        else:
            service = build('gmail', 'v1', credentials=credential)
            http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())

        thread_object = dbEmailThread(db=self.db).get_thread_by_id(thread_id=thread_id)
        mail_provider_id = dbEmailProvider(db=self.db).get_email_account_provider_table_id_by_email(email=email,
                                                                                                    account_id=account_id)
        mails_of_thread = dbEmailDetails(db=self.db).get_message_list_by_thread_id(account_id=account_id,
                                                                                   thread_id=thread_id,
                                                                                   email_provider_id=mail_provider_id)

        def change_label(request_id, response, exception):
            if exception is not None:
                print('messages.get failed for message id {}: {}'.format(request_id, exception))
                assert exception
            else:
                dbEmailDetails(db=self.db).update_mail_read_status(message_id=response["id"],
                                                                   thread_id=thread_object.id,
                                                                   account_id=account_id,
                                                                   mail_provider_id=mail_provider_id)

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        mails_of_thread_chunk = list(divide_chunks(mails_of_thread, 35))

        if not mails_of_thread is None and not mails_of_thread == []:
            for mail_of_thread_as_chunk in mails_of_thread_chunk:
                batch = service.new_batch_http_request(callback=change_label)
                for message in mail_of_thread_as_chunk:
                    batch.add(
                        service.users().messages().modify(userId='me', id=message.message_id,
                                                          body={"removeLabelIds": ["UNREAD"]}),
                        request_id=message.message_id)
                batch.execute()
        update_response = dbEmailThread(db=self.db).update_thread_read_status(thread_id=thread_object.thread_id,
                                                                              account_id=account_id,
                                                                              mail_provider_id=mail_provider_id)
        if update_response:
            self.db.commit()
        else:
            assert "Cannot Change Label"

    def get_attachment(self, attachment_id, email, message_id, thread_id, credential, from_file):
        if not credential or credential.invalid:
            try:
                service, http, credential = self.mail_log_in(email=email, credential=credential)
            except:
                return None
        elif credential is None:
            return None
        else:
            service = build('gmail', 'v1', credentials=credential)
            http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())

        crud_object = dbEmailProvider(db=self.db)
        message_object = dbEmailDetails(db=self.db).get_message_by_thread_id_and_message_id(message_id=message_id,
                                                                                            thread_id=thread_id)
        message_table_id = None
        if message_object is not None:
            message_table_id = message_object.id
        else:
            assert "Can not get Message Object"
        attachment_object = dbEmailAttachment(db=self.db).get_attachment_details_by_attachment_id(
            attachment_id=attachment_id,
            message_id=message_table_id)

        response = service.users().messages().attachments().get(userId='me', messageId=message_id,
                                                                id=attachment_object.attachment_id).execute()
        data = self.decode_base64(response["data"])
        stream = io.BytesIO(data)

        response = StreamingResponse(iter([stream.getvalue()]),
                                     media_type=attachment_object.file_type
                                     )

        response.headers["Content-Disposition"] = "attachment; filename=" + attachment_object.file_name

        return response

    def create_contact_from_from_and_reciepent_list(self, data_from_header, account_id):
        for mail_list in [data_from_header["From"], data_from_header["To"], data_from_header["Bcc"],
                          data_from_header["Cc"]]:
            if mail_list != "" and mail_list is not None:
                data_split = mail_list.split(',')
                for email_detail_ in data_split:
                    name__, email_addr = self.get_email_and_name(email_detail_)
                    contact_id__ = None

                    contact = ContactModel()
                    contact.email = email_addr
                    contact.name = name__
                    contact.account_id = account_id
                    contact.input_source = "Gmail"
                    contact.phone = ""
                    ContactClient().create_or_get_existing_contact(model=contact)
                    del contact

    def mark_seen_status(self, account_id, email, thread_id, is_seen, credential, from_file):
        data = []
        from_file = False
        http = None
        if not credential or credential.invalid:
            try:
                service, http, credential = self.mail_log_in(email=email, credential=credential)
            except:
                return None
        elif credential is None:
            return None
        else:
            service = build('gmail', 'v1', credentials=credential)
            http = google_auth_httplib2.AuthorizedHttp(credential, http=httplib2.Http())

        thread_object = dbEmailThread(db=self.db).get_thread_by_id(thread_id=thread_id)
        mail_provider_id = dbEmailProvider(db=self.db).get_email_account_provider_table_id_by_email(email=email,
                                                                                                    account_id=account_id)
        mails_of_thread = dbEmailDetails(db=self.db).get_message_list_by_thread_id(account_id=account_id,
                                                                                   thread_id=thread_id,
                                                                                   email_provider_id=mail_provider_id)
        res = False

        def change_seen_unseen_label(request_id, response, exception):
            if exception is not None:
                print('messages.get failed for message id {}: {}'.format(request_id, exception))
                assert exception.status_code
            else:
                dbEmailDetails(db=self.db).update_mail_seen_unseen_status(message_id=response["id"],
                                                                          thread_id=thread_object.id,
                                                                          account_id=account_id,
                                                                          mail_provider_id=mail_provider_id,
                                                                          is_seen=is_seen)

        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]

        mails_of_thread_chunk = list(divide_chunks(mails_of_thread, 35))

        if not mails_of_thread is None and not mails_of_thread == []:
            for mail_of_thread_as_chunk in mails_of_thread_chunk:
                batch = service.new_batch_http_request(callback=change_seen_unseen_label)
                for message in mail_of_thread_as_chunk:
                    if is_seen:
                        batch.add(
                            service.users().messages().modify(userId='me', id=message.message_id,
                                                              body={"removeLabelIds": ["UNREAD"]}),
                            request_id=message.message_id)
                    else:
                        batch.add(
                            service.users().messages().modify(userId='me', id=message.message_id,
                                                              body={"addLabelIds": ["UNREAD"]}),
                            request_id=message.message_id)
                batch.execute()
        update_response = dbEmailThread(db=self.db).update_thread_seen_unseen_status(thread_id=thread_object.thread_id,
                                                                                     account_id=account_id,
                                                                                     mail_provider_id=mail_provider_id,
                                                                                     is_seen=is_seen)
        if update_response:
            self.db.commit()
            return update_response
        else:
            assert "Cannot Change Label"
