import calendar
import datetime

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as EnumType, PickleType

from db.database import Base


class AppBaseModelOrm:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    is_active = Column(Boolean, default=True)  # soft delete
    created_by = Column(Integer)
    updated_by = Column(Integer, default=None)
    created_datetime = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_datetime = Column(DateTime(timezone=True), default=None, onupdate=datetime.datetime.utcnow)


class Contact(Base):
    __tablename__: str = "contact"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, nullable=False)
    name = Column(String)
    phone_number = Column(String)
    account_id = Column(String)
    input_source = Column(String)
    provider_uid = Column(String)
    profile_image = Column(String)
    profile_image_content_type = Column(String)


class EmailAccountProvided(AppBaseModelOrm, Base):
    __tablename__ = "email_communication"
    account_id = Column(Integer, nullable=False)  # Type Account
    email = Column(String, nullable=False)
    token = Column(PickleType, nullable=False)
    token_refresh_date = Column(DateTime, nullable=True)
    last_synced_epoch = Column(Integer, default=calendar.timegm((datetime.datetime.now()).timetuple()))
    provider = Column(String)


class EmailCommunicationType(EnumType):
    SEND = "Send"
    RECEIVE = "Receive"
    REPLY = "Reply"


class EmailDetails(AppBaseModelOrm, Base):
    __tablename__ = "email_details"
    subject = Column(String)
    from_address = Column(String, nullable=False)
    message_id = Column(String, nullable=False)
    thread_id = Column(Integer, nullable=False)  # Type Thread
    email_account_provider_id = Column(Integer, nullable=False)
    body = Column(String)
    operation_datetime = Column(DateTime(timezone=True))
    history_id = Column(String)
    is_read = Column(Boolean, default=False)
    type = Column(String)  # from EmailCommunicationType
    contact_id = Column(Integer, nullable=True)
    account_id = Column(Integer, nullable=False)


class EmailReceiverType(EnumType):
    TO = "To"
    CC = "CC"
    BCC = "BCC"


class EmailReceiver(AppBaseModelOrm, Base):
    __tablename__ = "email_receiver"
    email_id = Column(Integer, nullable=False)
    address = Column(String, nullable=False)
    type = Column(String, default="To")  # from EmailReceiverType


class EmailAttachment(Base):
    __tablename__ = "email_attachment"
    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, nullable=False)
    attachment_id = Column(String, nullable=False)
    file_name = Column(String)
    file_type = Column(String)


class EmailThread(AppBaseModelOrm, Base):
    __tablename__ = "email_thread"
    thread_id = Column(String, nullable=False)
    email = Column(String)
    email_account_provider_id = Column(Integer)
    account_id = Column(Integer, nullable=False)
    assigned_to_user_id = Column(Integer, nullable=True)
    is_closed = Column(Boolean, default=False)
    is_trashed = Column(Boolean, default=False)
    snippet = Column(String)
    subject = Column(String)
    latest_message_email = Column(String)
    is_read = Column(Boolean)
    sync_datetime = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
