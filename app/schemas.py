from typing import Optional, List

from fastapi_camelcase import CamelModel
from pydantic import BaseModel

from app.form import as_form

'''
Inbox Email
'''


class EmailProvider(BaseModel):
    id: Optional[int] = 0
    account_id: Optional[int] = 0
    email: Optional[str] = ''
    provider: Optional[str] = ''

@as_form
class EmailCreate(CamelModel):
    email_description: Optional[str] = None
    subject: Optional[str] = None
    from_email: str
    to_email: List[str]
    cc_email: Optional[List[str]]
    bcc_email: Optional[List[str]]

    class Config:
        orm_mode = True