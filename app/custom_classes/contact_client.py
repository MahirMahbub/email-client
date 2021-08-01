from sqlalchemy.orm import Session

from app.cruds.contact import ContactCrud
from db.database import SessionLocal

'''
----------------> Models
'''


class ContactModel:
    id: int = 0
    email: str = ""
    name: str = ""
    phone: str = ""
    account_id: int = 0
    input_source: str = ""
    ref_id: str = ""
    profile_image: str = ""
    profile_image_content_type: str = ""


'''
<---------------- Models
'''


class ContactClient:

    def __init__(self, db=None):
        if db is None:
            self.db = SessionLocal()
        else:
            self.db: Session = db

    #
    # def get_user_by_id(self, user_id: int):
    #     uri = self.url('/api/v1/users/user-and-active-account?user_id=' + user_id)
    #     response = requests.get(uri)
    #     data = response.json()
    #     return data

    def create_or_get_existing_contact(self, model: ContactModel):
        item = {
            "email": model.email,
            "name": model.name.replace('"', '') if model.name is not None else "",
            "phoneNumber": model.phone if model.phone is not None else "",
            "accountId": model.account_id,
            "inputSource": model.input_source if model.input_source is not None else "",
            "providerUid": model.ref_id if model.ref_id is not None else "",
            "profileImage": model.profile_image if model.profile_image is not None else None,
            "profileImageContentType": model.profile_image_content_type if model.profile_image_content_type is not None
            else ""
        }
        data = ContactCrud(db=self.db).store(checker={"email": model.email}, item=item)
        self.db.commit()
        return data

    #
    # def check_web_widget_exist(self, account_id):
    #     url_path = self.url("/api/v1/interservice/chat-flow/status")
    #     response = requests.get(url=url_path, json=None, params={"account-id": account_id})
    #     return json.loads(response.content)
    #
    # def get_contact_list_by_group_id(self, group_id, include_contacts):
    #     url_path = self.url(
    #         "/api/v1/contact-group/{0}/contacts?include_contacts={1}".format(group_id, include_contacts))
    #     response = requests.get(url=url_path)
    #
    #     data = response.json()
    #     contact_list = []
    #     if not data["ids"] == []:
    #         contacts = data["contacts"]
    #         for contact in contacts:
    #             id_ = contact["contact"]["id"]
    #             email = contact["email"]
    #             has_subscribed_email = contact["contact"]["has_subscribed_email"]
    #             contact_list.append((email, id_, has_subscribed_email))
    #
    #     return contact_list

    # def send_real_time_notification(self, *, token=None,
    #                                 receiver_account_id,
    #                                 receiver_user_id=None,
    #                                 notification_message,
    #                                 notification_type,
    #                                 notification_header,
    #                                 object_):
    #
    #     if receiver_user_id is not None:
    #         url_path = self.url(
    #             "/api/v1/interservice/notification/send/"
    #             "{receiver_account_id}/"
    #             "{receiver_user_id}/"
    #             "{notification_message}/"
    #             "{notification_type}/"
    #             "{notification_header}".format(
    #                 receiver_account_id=receiver_account_id,
    #                 receiver_user_id=receiver_user_id,
    #                 notification_message=notification_message,
    #                 notification_type=notification_type,
    #                 notification_header=notification_header))
    #     else:
    #         url_path = self.url(
    #             "/api/v1/interservice/notification/send/"
    #             "{receiver_account_id}/"
    #             "{notification_message}/"
    #             "{notification_type}/"
    #             "{notification_header}".format(
    #                 receiver_account_id=receiver_account_id,
    #                 notification_message=notification_message,
    #                 notification_type=notification_type,
    #                 notification_header=notification_header))
    #
    #     payload = jsonable_encoder(object_)
    #     # print(payload)
    #     # auth = BearerAuth(token),
    #     response = requests.post(url=url_path, data=json.dumps(payload))
    #     return response.json()
    #
    # async def get_chat_bot_response(self, account_id: int, message: str):
    #     payload = {
    #         'accountId': account_id,
    #         'message': message
    #     }
    #
    #     url_path = self.url("/api/v1/interservice/chatbot/auto-reply/facebook")
    #     try:
    #         response = requests.post(url=url_path, json=payload)
    #         status_code = response.status_code
    #         if status_code == 200:
    #             data = response.json()
    #             return data
    #         else:
    #             return None
    #     except Exception as e:
    #         print("Fb Chat bot inter-service error!")
    #         return None
    #
    # def get_package_limits(self, account_id: int, range_type: str = None, for_datetime_utc: datetime = None):
    #     params = {
    #         'range_type': range_type,
    #         'for_datetime_utc': for_datetime_utc
    #     }
    #
    #     url_path = self.url("/api/v1/interservice/accounts/" + str(account_id) + "/limits-and-range")
    #     try:
    #         response = requests.get(url=url_path, params=params)
    #         status_code = response.status_code
    #         if status_code == 200:
    #             data = response.json()
    #             return data
    #         else:
    #             return None
    #     except Exception as e:
    #         print("Packages limits inter-service error!")
    #         return None
