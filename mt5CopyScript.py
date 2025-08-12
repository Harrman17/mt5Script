import MetaTrader5 as mt5
import time

MASTER_PATH = r"C:\Users\Administrator\Desktop\terminals\master\terminal64.exe"
SLAVE_PATH = r"C:\Users\Administrator\Desktop\terminals\slave\terminal64.exe"

MASTER_LOGIN = 123456
MASTER_PASSWORD = "master_password"
MASTER_SERVER = "Broker-Server"

SLAVE_LOGIN = 654321
SLAVE_PASSWORD = "slave_password"
SLAVE_SERVER = "Broker-Server"

COPY_INTERVAL = 5  # seconds


def copy_positions():
    master_positions = mt5.positions_get()
    if master_positions is None:
        print("No positions on master account.")
        return

    for pos in master_positions:
        # Your trade copying logic here
        print(f"Copying {pos.symbol} {pos.volume} {pos.type}")


# --- LOGIN TO MASTER ---
if not mt5.initialize(path=MASTER_PATH, login=MASTER_LOGIN, password=MASTER_PASSWORD, server=MASTER_SERVER):
    print(f"Master login failed: {mt5.last_error()}")
    quit()
else:
    print("Master account logged in successfully.")

# --- LOGIN TO SLAVE ---
if not mt5.initialize(path=SLAVE_PATH, login=SLAVE_LOGIN, password=SLAVE_PASSWORD, server=SLAVE_SERVER):
    print(f"Slave login failed: {mt5.last_error()}")
    quit()
else:
    print("Slave account logged in successfully.")

# --- MAIN COPY LOOP ---
try:
    while True:
        copy_positions()
        time.sleep(COPY_INTERVAL)
except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    mt5.shutdown()
