import MetaTrader5 as mt5
import subprocess
import time
import multiprocessing
import sys

MASTER_PATH = r"C:\Users\Administrator\Desktop\terminals\master\terminal64.exe"
SLAVE_PATH = r"C:\Users\Administrator\Desktop\terminals\slave\terminal64.exe"

MASTER_LOGIN = 5038347062
MASTER_PASSWORD = "Wa@nAp6f"
MASTER_SERVER = "MetaQuotes-Demo"

SLAVE_LOGIN = 5038438610
SLAVE_PASSWORD = "Av@hJ1Kx"
SLAVE_SERVER = "MetaQuotes-Demo"

def start_mt5_terminal(path):
    try:
        subprocess.Popen([path, "/portable"])
        time.sleep(5)  # Give MT5 some time to start
    except Exception as e:
        print(f"Error starting MT5 terminal: {e}")

def init_account(login, password, server, terminal_path):
    if not mt5.initialize(path=terminal_path, login=login, password=password, server=server):
        print(f"Failed to initialize MT5 account {login}: {mt5.last_error()}")
        return False
    print(f"Account {login} logged in successfully on terminal: {terminal_path}")
    return True

def master_process():
    """Process to handle master terminal connection"""
    print("Starting master terminal process...")
    if init_account(MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER, MASTER_PATH):
        print("Master account connected successfully")
        # Add your master account logic here
        # For example, monitor for new trades
        time.sleep(10)  # Keep connection alive for demo
    mt5.shutdown()

def slave_process():
    """Process to handle slave terminal connection"""
    print("Starting slave terminal process...")
    if init_account(SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER, SLAVE_PATH):
        print("Slave account connected successfully")
        # Add your slave account logic here
        # For example, place copied trades
        time.sleep(10)  # Keep connection alive for demo
    mt5.shutdown()

if __name__ == "__main__":
    # --- Launch Master & Slave terminals in portable mode ---
    print("Launching MT5 terminals...")
    start_mt5_terminal(MASTER_PATH)
    start_mt5_terminal(SLAVE_PATH)
    
    # Wait a bit more for terminals to fully initialize
    time.sleep(10)
    
    # --- Create separate processes for each terminal connection ---
    print("Creating separate processes for terminal connections...")
    
    master_proc = multiprocessing.Process(target=master_process)
    slave_proc = multiprocessing.Process(target=slave_process)
    
    # Start both processes
    master_proc.start()
    slave_proc.start()
    
    # Wait for both processes to complete
    master_proc.join()
    slave_proc.join()
    
    print("Both terminal processes completed.")
