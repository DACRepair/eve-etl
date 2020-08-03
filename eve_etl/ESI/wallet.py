from .session import ESISession


class EVEWallet:
    def __init__(self, corp_id: int = None, auth_token: str = None):
        self.corp_id = corp_id
        self._esi = ESISession()
        self._esi.headers.update({"Authorization": "Bearer {}".format(auth_token)})

    def divisions(self):
        url = "https://esi.evetech.net/v1/corporations/{}/wallets/".format(self.corp_id)
        print(self._esi.get(url=url).text)