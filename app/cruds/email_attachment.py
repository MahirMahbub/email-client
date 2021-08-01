from sqlalchemy import and_

from app.cruds.table_repository import TableRepository
from db import models


class EmailAttachmentCrud(TableRepository):

    def __init__(self, db) -> None:
        super().__init__(db=db, entity=models.EmailAttachment)

    def create_email_attachment(self, email_id, attachments):
        """
            "file_name": part["filename"],
            "attachment_id": base64.b64decode(part["body"]["attachmentId"]),
            "file_type": part["mimeType"]
        """
        if not attachments == []:
            for attachment in attachments:
                attachment_obj = self.entity(attachment_id=attachment["attachment_id"],
                                             file_name=attachment["file_name"],
                                             file_type=attachment["file_type"],
                                             email_id=email_id)
                self.db.add(attachment_obj)

    def get_attachments_by_email_id(self, email_id):
        return self.db.query(self.entity).filter(self.entity.email_id == email_id).all()

    def get_attachment_details_by_attachment_id(self, attachment_id, message_id):
        return self.db.query(self.entity).filter(and_(self.entity.id == attachment_id,
                                                      self.entity.email_id == message_id)).first()
