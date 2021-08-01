from sqlalchemy.orm import Session

from app.custom_classes.email.email_configuration import GmailUtilities


class GmailData(GmailUtilities):

    def __init__(self, db: Session, account_id: int) -> None:
        super().__init__(db, account_id)
        self.db = db
        self.account_id = account_id
        self.provider = "Gmail"

    def get_thread_by_credentials(self, credential, email, from_file, account_id):
        return {
            "found": True,
            'data':
                [
                    {
                        "id": 1,
                        'subject': "No Subject",
                        'userImage': "https://pbs.twimg.com/profile_images/517863945/mattsailing_400x400.jpg",
                        'isOnline': False,
                        'isSeen': False,
                        'name': "masum1",
                        "from": 'mahd@gmail.com',
                        'snippet': "awesome message1",
                        'date': "2021-01-19 14:33:18.848000 +00:00",
                        'channel': "Email"
                    },
                    {
                        "id": 1,
                        'subject': "No Subject2",
                        'userImage': "https://pbs.twimg.com/profile_images/517863945/mattsailing_400x400.jpg",
                        'isOnline': False,
                        'isSeen': False,
                        'name': "masum2",
                        "from": 'mahe@gmail.com',
                        'snippet': "awesome message2",
                        'date': "2021-01-19 12:33:18.848000 +00:00",
                        'channel': "Email"
                    },
                    {
                        "id": 1,
                        'subject': "No Subject3",
                        'userImage': "https://pbs.twimg.com/profile_images/517863945/mattsailing_400x400.jpg",
                        'isOnline': False,
                        'isSeen': False,
                        'name': "masum3",
                        "from": 'mah@gmail.com',
                        'snippet': "awesome message1",
                        'date': "2021-01-19 12:11:18.848000 +00:00",
                        'channel': "Email"
                    },
                ]
        }

    def get_thread_details_by_credentials(self, account_id, thread_id):
        return {
            "found": True,
            'data':
                [
                    {
                        "id": 1,
                        "messageId": 3,
                        "threadId": 1,
                        'subject': "No Subject3",
                        'name': "masum3",
                        "from": 'mah@gmail.com',
                        "to": "masum <masum@gnail.com, mahir@gmail.com",
                        "cc": "madman@gmail.com",
                        "bcc": "Gig <gig@fmaol.com",
                        'message': "awesome message1",
                        'date': "2021-01-19 12:11:18.848000 +00:00",
                        'channel': "Email",
                        'attachments':
                            [
                                {
                                    "id": 2,
                                    "attachment_id": 3,
                                    "file_name": "a.txt",
                                    "file_type": "file/pdf"
                                }
                            ]
                    },
                    {
                        "id": 2,
                        "messageId": 2,
                        "threadId": 1,
                        'subject': "No Subject2222",
                        'name': "Foeman",
                        "from": 'maddsfsh@gmail.com',
                        "to": "ffmasum <mdfffasum@gnail.com, mahfir@gmail.com",
                        "cc": "maffdman@gmail.com",
                        "bcc": "Giffg <gifg@fmaol.com",
                        'message': "bwesome message1",
                        'date': "2021-01-19 12:11:18.848000 +00:00",
                        'channel': "Email",
                        'attachments':
                            [
                                {
                                    "id": 4,
                                    "attachment_id": 4,
                                    "file_name": "ssds.txt",
                                    "file_type": "file/text"
                                }
                            ]
                    },
                ]
        }