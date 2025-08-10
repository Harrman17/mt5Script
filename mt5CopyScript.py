import MetaTrader5 as mt5
import time
import sys
import os
import subprocess

# === CONFIG ===
MASTER_PATH = r"C:\Users\Administrator\Desktop\terminals\master\terminal64.exe"
SLAVE_PATH = r"C:\Users\Administrator\Desktop\terminals\slave1\terminal64.exe"
COPY_INTERVAL = 1  # seconds

# Credentials from env vars
MASTER_LOGIN = int(os.getenv("MASTER_LOGIN", 0))
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "")
MASTER_SERVER = os.getenv("MASTER_SERVER", "")

SLAVE_LOGIN = int(os.getenv("SLAVE_LOGIN", 0))
SLAVE_PASSWORD = os.getenv("SLAVE_PASSWORD", "")
SLAVE_SERVER = os.getenv("SLAVE_SERVER", "")


def launch_mt5_with_login(exe_path, login, password, server):
    """Create config file and launch MT5 logged in."""
    if not login or not password or not server:
        print(f"⚠️ Missing login details for {exe_path}")
        return
    
    print(f"📝 Login details for {exe_path}:")
    print(f"  Login: {login}")
    print(f"  Password: {password}")
    print(f"  Server: {server}")

    config_path = os.path.join(os.path.dirname(exe_path), "login.ini")
    with open(config_path, "w") as f:
        f.write(f"Login={login}\n")
        f.write(f"Password={password}\n")
        f.write(f"Server={server}\n")
        f.write("AutoConfiguration=1\n")
        f.write("EnableNews=0\n")

    print(f"🚀 Launching MT5 at {exe_path} with /config:{config_path}")
    subprocess.Popen([exe_path, f"/config:{config_path}"])
    time.sleep(5)  # wait for MT5 to initialize


def connect_and_login(path):
    """Connect to MT5 — assumes it's already running/logged in."""
    if not mt5.initialize(path=path):
        print(f"❌ Failed to initialize MT5 at {path}")
        return False

    account_info = mt5.account_info()
    if account_info:
        print(f"✅ Connected: {account_info.login} @ {account_info.server}")
        return True
    else:
        print("❌ MT5 initialized but not logged in.")
        return False


def shutdown_mt5():
    mt5.shutdown()


def get_positions():
    return mt5.positions_get() or []


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
    positions = get_positions()
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
    # Step 1 — Launch MT5 terminals logged in
    launch_mt5_with_login(MASTER_PATH, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER)
    launch_mt5_with_login(SLAVE_PATH, SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER)

    # Step 2 — Start trade copier loop
    while True:
        connect_and_login(MASTER_PATH)
        master_positions = get_positions()
        master_snapshot = positions_to_dict(master_positions)
        shutdown_mt5()

        connect_and_login(SLAVE_PATH)
        slave_positions = get_positions()
        slave_snapshot = positions_to_dict(slave_positions)

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
    print("🚀 Trade copier starting...")
    main()
