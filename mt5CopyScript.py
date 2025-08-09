import MetaTrader5 as mt5
import time
import sys
import os

# === CONFIG ===
MASTER_PATH = "C:\\Users\\Administrator\\Desktop\\terminals\master\\terminal64.exe"

SLAVE_PATH = "C:\\Users\Administrator\\Desktop\\terminals\\slave1\\terminal64.exe"
COPY_INTERVAL = 1  # seconds

# Get credentials from env vars (set by backend or manually for now)
MASTER_LOGIN = int(os.getenv("MASTER_LOGIN", 0))
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "")
MASTER_SERVER = os.getenv("MASTER_SERVER", "")

SLAVE_LOGIN = int(os.getenv("SLAVE_LOGIN", 0))
SLAVE_PASSWORD = os.getenv("SLAVE_PASSWORD", "")
SLAVE_SERVER = os.getenv("SLAVE_SERVER", "")

def connect_and_login(path, login, password, server):
    if not mt5.initialize(path=path):
        print(f"❌ Failed to initialize MT5 at {path}")
        sys.exit()

    authorized = mt5.login(login, password, server)
    if not authorized:
        print(f"❌ Failed to log in: {login} on {server}")
        sys.exit()

    print(f"✅ Logged in: {login} on {server}")
    return True

def shutdown_mt5():
    mt5.shutdown()

def get_positions():
    return mt5.positions_get()

def copy_position_to_slave(position):
    symbol = position.symbol
    volume = position.volume
    order_type = position.type
    price = mt5.symbol_info_tick(symbol).ask if order_type == 0 else mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 10,
        "magic": 123456,
        "comment": "Trade copied",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Trade failed: retcode={result.retcode}, message: {result.comment}")
    else:
        print(f"✅ Trade copied: {symbol}, {volume} lots, {'BUY' if order_type == 0 else 'SELL'}")

def clear_slave_open_positions():
    positions = mt5.positions_get()
    if positions:
        for p in positions:
            close_position(p)

def close_position(position):
    order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price = mt5.symbol_info_tick(position.symbol).bid if order_type == mt5.ORDER_TYPE_SELL else mt5.symbol_info_tick(position.symbol).ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": position.symbol,
        "volume": position.volume,
        "type": order_type,
        "position": position.ticket,
        "price": price,
        "deviation": 10,
        "magic": 123456,
        "comment": "Close position",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    mt5.order_send(request)

def positions_to_dict(positions):
    return {p.ticket: (p.symbol, p.volume, p.type) for p in positions}

def main():
    while True:
        # Connect to master
        connect_and_login(MASTER_PATH, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER)
        master_positions = get_positions()
        master_snapshot = positions_to_dict(master_positions)
        shutdown_mt5()

        # Connect to slave
        connect_and_login(SLAVE_PATH, SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER)
        slave_positions = get_positions()
        slave_snapshot = positions_to_dict(slave_positions)

        # Sync
        if master_snapshot != slave_snapshot:
            print("🔁 Desync detected — syncing now")
            clear_slave_open_positions()
            for p in master_positions:
                copy_position_to_slave(p)
        else:
            print("✅ Slave is already in sync with master")

        shutdown_mt5()
        time.sleep(COPY_INTERVAL)

if __name__ == "__main__":
    print("🚀 Trade copier started")
    main()
