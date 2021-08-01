from typing import Optional, List

from fastapi import Depends, status, Query, FastAPI, UploadFile, File
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session

from app import schemas
from app.depends.db_depend import get_db
from app.enums import DateFilters
from app.services.communication.email import EmailService as serviceEmail
from app.utils import catch_not_implemented_exception
from app.cruds.email_account_provider import EmailAccountProvidedCrud as EmailCrud

app = FastAPI()
router = InferringRouter()


@cbv(router)
class Email:
    db: Session = Depends(get_db)

    '''
    Email Providers
    '''  
    @router.get("/providers/accounts/{account_id}")
    def get_providers(self, account_id: int):
        list = []
        items = EmailCrud(self.db).get_actives_by_account(account_id=account_id)
        for item in items:
            data = schemas.EmailProvider()
            data.id = item.id
            data.email = item.email
            data.account_id = item.account_id
            data.provider = item.provider
            list.append(data)
        return list

    @router.delete("/providers/{provider_id}/accounts/{account_id}")
    def delete_providers(self, provider_id: int, account_id: int):
        crud = EmailCrud(self.db)
        item = crud.find_active_email_provider(provider_id=provider_id, account_id=account_id)
        if item:        
            crud.clear_email_provider(provider_id=provider_id, account_id=account_id)
            self.db.commit()
            self.db.refresh(item)

    '''
    Email Inbox
    '''    

    @router.post("/authenticate/", status_code=status.HTTP_201_CREATED)
    @catch_not_implemented_exception
    def authenticate(self, authorize_code: str = Query(..., alias="authorize-code"),
                     account_id: int = Query(..., alias="account-id")):

        api_object = serviceEmail()
        return api_object.authenticate(db=self.db, account_id=account_id, authorize_code=authorize_code)

    @router.get("/filter/")
    @catch_not_implemented_exception
    def get_filter(self, is_closed: Optional[bool] = Query(False, alias="is-closed"),
                   contact_email: Optional[str] = Query("All", alias="contact-email"),
                   date: Optional[DateFilters] = Query(DateFilters.ALL_TIME),
                   account_id: int = Query(..., alias="account-id"),
                   email: str = Query(..., alias="email"),
                   ):

        api_object = serviceEmail()
        db_push_response = api_object.get_all_thread(db=self.db, account_id=account_id, email=email)
        if db_push_response:
            return api_object.get_filter(db=self.db, is_closed=is_closed,
                                         contact_email=contact_email, date=date, email=email, account_id=account_id)
        # else:
        #     from fastapi import HTTPException
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        #                             detail="No Such Provider Found or Error Occured")

    @router.get("/get-thread-details/")
    @catch_not_implemented_exception
    def get_thread_details(self, thread_id: int = Query(..., alias="thread-id"),
                           account_id: int = Query(..., alias="account-id"),
                           email: str = Query(..., alias="email"),
                           mark_seen: Optional[bool] = Query(True, alias="mark-seen")):
        api_object = serviceEmail()
        if mark_seen:
            api_object.change_label_seen(db=self.db, account_id=account_id,
                                         email=email,
                                         thread_id=thread_id)
        return api_object.get_thread_details(db=self.db, account_id=account_id, email=email, thread_id=thread_id)

    @router.post("/mark-seen-status/")
    @catch_not_implemented_exception
    def mark_seen_status(self, thread_id: int = Query(..., alias="thread-id"),
                         account_id: int = Query(..., alias="account-id"),
                         email: str = Query(..., alias="email"),
                         is_seen: bool = Query(..., alias="is-seen")):

        api_object = serviceEmail()
        return api_object.mark_seen_status(db=self.db, account_id=account_id,
                                           email=email,
                                           thread_id=thread_id,
                                           is_seen=is_seen)

    @router.post("/send-mail/")
    @catch_not_implemented_exception
    def send_email(self, *, files: Optional[List[UploadFile]] = File(None),
                   account_id: Optional[int] = Query(None, alias="account-id"),
                   message_id: Optional[str] = Query(None, alias="message-id"),
                   email_description: schemas.EmailCreate = Depends(schemas.EmailCreate.as_form)):
        api_object = serviceEmail()
        if account_id is None:
            account_id = 2
        if email_description.from_email is None:
            email_description.from_email = 'mahirmahbub7@gmail.com'
        # print(files)

        return api_object.send_mail(db=self.db, files=files, account_id=account_id, email_description=email_description,
                                    message_id=message_id)
        # return api_object.

    @router.get("/get-connect-mail-list/")
    @catch_not_implemented_exception
    def get_connected_mail_list(self,
                                account_id: int = Query(..., alias="account-id")):
        api_object = serviceEmail()
        # account_id = 2
        # email = 'mahirmahbub7@gmail.com'
        return api_object.get_connected_mail_list(db=self.db, account_id=account_id)

    # @router.get("/change-label-seen/")
    # @catch_not_implemented_exception
    # def change_label(self,
    #                  account_id: int = Query(..., alias="account-id"),
    #                  email: str = Query(..., alias="email"),
    #                  thread_id: int = Query(..., alias="thread-id")):
    #     api_object = serviceEmail()
    #     # account_id = 2
    #     # email = 'mahirmahbub7@gmail.com'
    #     return api_object.change_label_seen(db=self.db, account_id=account_id,
    #                                         email=email,
    #                                         thread_id=thread_id)

    @router.get("/get-attachment/")
    @catch_not_implemented_exception
    def get_attachment(self,
                       account_id: int = Query(..., alias="account-id"),
                       email: str = Query(..., alias="email"),
                       attachment_id: str = Query(..., alias="attachment-id"),
                       message_id: str = Query(..., alias="message-id"),
                       thread_id: int = Query(..., alias="thread-id")):
        api_object = serviceEmail()
        # account_id = 2
        # email = 'mahirmahbub7@gmail.com'
        return api_object.get_attachment(db=self.db, account_id=account_id, email=email, attachment_id=attachment_id,
                                         message_id=message_id, thread_id=thread_id)

    # @router.post("/assign-thread/")
    # @catch_not_implemented_exception
    # def assign_thread(self, thread_id: int = Query(..., alias="thread-id"),
    #                   user_id: Optional[str] = Query(None, alias="user-id")):
    #     api_object = serviceEmail()
    #     # account_id = 2
    #     # email = 'mahirmahbub7@gmail.com'
    #     return api_object.assign_user_to_thread(db=self.db, user_id=user_id, thread_id=thread_id, user=self.user)
    #
    # @router.get("/get-assigned-owner/")
    # @catch_not_implemented_exception
    # def get_assigned_owner(self, thread_id: int = Query(..., alias="thread-id")):
    #     api_object = serviceEmail()
    #     return api_object.get_assigned_owner(db=self.db, thread_id=thread_id)
    #
    # @router.put("/change-status/")
    # @catch_not_implemented_exception
    # def change_status(self, thread_id: int = Query(..., alias="thread-id"),
    #                   is_closed: bool = Query(..., alias="is-closed")):
    #     api_object = serviceEmail()
    #     return api_object.change_status(db=self.db, thread_id=thread_id, is_closed=is_closed)
