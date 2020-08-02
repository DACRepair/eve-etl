from requests import Session


class ESISession(Session):
    def __init__(self):
        super(ESISession, self).__init__()
        self.headers.update({
            "Accept": "application/json",
            "User-Agent": "EVE-ETL by DACRepair <dacrepair@gmail.com>"
        })
