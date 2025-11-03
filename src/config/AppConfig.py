import os

from dotenv import load_dotenv


class AppConfig:
    def __init__(
        self,
        admin_id: str,
        sqlite_absolute_path: str,
        admin_username: str,
        admin_password: str,
    ):
        self.admin_id = admin_id
        self.sqlite_absolute_path = sqlite_absolute_path
        self.admin_username = admin_username
        self.admin_password = admin_password
        return

    @staticmethod
    def load():
        load_dotenv()
        admin_id = os.getenv("ADMIN_ID")
        sqlite_absolute_path = os.getenv("SQLITE_ABSOLUTE_PATH")
        admin_username = os.getenv("ADMIN_USERNAME")
        admin_password = os.getenv("ADMIN_PASSWORD")
        if (
            admin_id == None
            or sqlite_absolute_path == None
            or admin_username == None
            or admin_password == None
        ):
            raise Exception(
                "please configure your .env file before serving cfasuite\ncheckout https://github.com/phillip-england/cfasuite for more information"
            )
        return AppConfig(admin_id, sqlite_absolute_path, admin_username, admin_password)
