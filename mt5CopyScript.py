import MetaTrader5 as mt5

MASTER_LOGIN = 5038347062
MASTER_PASSWORD = "Wa@nAp6f"
MASTER_SERVER = "MetaQuotes-Demo"

SLAVE_LOGIN = 5038438610
SLAVE_PASSWORD = "Av@hJ1Kx"
SLAVE_SERVER = "MetaQuotes-Demo"

mt5.initialize(path=MASTER_PATH, login=MASTER_LOGIN, password=MASTER_PASSWORD, server=MASTER_SERVER)

mt5.initialize(path=SLAVE_PATH, login=SLAVE_LOGIN, password=SLAVE_PASSWORD, server=SLAVE_SERVER)