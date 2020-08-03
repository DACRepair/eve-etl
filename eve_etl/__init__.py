from eve_etl.Common import config
from eve_etl.ESI import EVEAuth

auth = EVEAuth(client_id=config.get("ESI", "client_id"),
               client_secret=config.get("ESI", "client_secret"),
               redir_url=config.get("ESI", "redir_url"),
               scope=[config.get("ESI_Scope", str(x)) for x in config.options("ESI_Scope")])
