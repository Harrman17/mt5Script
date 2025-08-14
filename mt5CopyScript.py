import MetaTrader5 as mt5
import subprocess
import time
import multiprocessing
import sys
import os
import configparser
import winreg
import requests

MASTER_PATH = r"C:\Users\Administrator\Desktop\terminals\master\terminal64.exe"
SLAVE_PATH = r"C:\Users\Administrator\Desktop\terminals\slave1\terminal64.exe"

MASTER_LOGIN = 5038347062
MASTER_PASSWORD = "Wa@nAp6f"
MASTER_SERVER = "MetaQuotes-Demo"

SLAVE_LOGIN = 5038438610
SLAVE_PASSWORD = "Av@hJ1Kx"
SLAVE_SERVER = "MetaQuotes-Demo"

COPY_INTERVAL = 1  # seconds

def enable_algo_trading_in_config(terminal_path):
    """Enable algorithmic trading by creating comprehensive config files"""
    try:
        # Get the terminal directory
        terminal_dir = os.path.dirname(terminal_path)
        config_dir = os.path.join(terminal_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # 1. Create/update common.ini
        common_config_path = os.path.join(config_dir, "common.ini")
        common_config_content = """[Terminal]
AllowLiveTrading=1
AllowDllImport=1
AllowWebRequest=1
AllowAutoTrading=1
AllowExternalExperts=1
AllowExternalSignals=1
AllowExternalAlerts=1
AllowSendNotifications=1
AllowSendEmail=1
AllowSendSMS=1
AllowSendPush=1
AllowSendWebRequest=1
AllowSendFTP=1
AllowSendTerminal=1
AllowSendTerminalEmail=1
AllowSendTerminalSMS=1
AllowSendTerminalPush=1
AllowSendTerminalWebRequest=1
AllowSendTerminalFTP=1
AllowSendTerminalTerminal=1
"""
        
        with open(common_config_path, 'w', encoding='utf-8') as configfile:
            configfile.write(common_config_content)
        
        print(f"✅ Created comprehensive common.ini: {common_config_path}")
        
        # 2. Create/update terminal.ini
        terminal_config_path = os.path.join(config_dir, "terminal.ini")
        terminal_config_content = """[Terminal]
AllowLiveTrading=1
AllowDllImport=1
AllowWebRequest=1
AllowAutoTrading=1
AllowExternalExperts=1
AllowExternalSignals=1
AllowExternalAlerts=1
AllowSendNotifications=1
AllowSendEmail=1
AllowSendSMS=1
AllowSendPush=1
AllowSendWebRequest=1
AllowSendFTP=1
AllowSendTerminal=1
AllowSendTerminalEmail=1
AllowSendTerminalSMS=1
AllowSendTerminalPush=1
AllowSendTerminalWebRequest=1
AllowSendTerminalFTP=1
AllowSendTerminalTerminal=1
"""
        
        with open(terminal_config_path, 'w', encoding='utf-8') as configfile:
            configfile.write(terminal_config_content)
        
        print(f"✅ Created terminal.ini: {terminal_config_path}")
        
        # 3. Create/update experts.ini
        experts_config_path = os.path.join(config_dir, "experts.ini")
        experts_config_content = """[Experts]
AllowLiveTrading=1
AllowDllImport=1
AllowWebRequest=1
AllowAutoTrading=1
AllowExternalExperts=1
AllowExternalSignals=1
AllowExternalAlerts=1
AllowSendNotifications=1
AllowSendEmail=1
AllowSendSMS=1
AllowSendPush=1
AllowSendWebRequest=1
AllowSendFTP=1
AllowSendTerminal=1
AllowSendTerminalEmail=1
AllowSendTerminalSMS=1
AllowSendTerminalPush=1
AllowSendTerminalWebRequest=1
AllowSendTerminalFTP=1
AllowSendTerminalTerminal=1
"""
        
        with open(experts_config_path, 'w', encoding='utf-8') as configfile:
            configfile.write(experts_config_content)
        
        print(f"✅ Created experts.ini: {experts_config_path}")
        
        # 4. Create/update profiles.ini
        profiles_config_path = os.path.join(config_dir, "profiles.ini")
        profiles_config_content = """[Profiles]
Default=Default
"""
        
        with open(profiles_config_path, 'w', encoding='utf-8') as configfile:
            configfile.write(profiles_config_content)
        
        print(f"✅ Created profiles.ini: {profiles_config_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create config files: {e}")
        return False

def enable_algo_trading_via_registry(terminal_path):
    """Enable algorithmic trading via Windows registry"""
    try:
        # Get terminal directory
        terminal_dir = os.path.dirname(terminal_path)
        
        # Try multiple registry keys
        registry_keys = [
            f"SOFTWARE\\MetaQuotes\\Terminal\\{terminal_dir.replace(':', '').replace('\\', '_')}",
            "SOFTWARE\\MetaQuotes\\Terminal",
            "SOFTWARE\\MetaQuotes\\Terminal\\Common",
            f"SOFTWARE\\MetaQuotes\\Terminal\\{os.path.basename(terminal_dir)}"
        ]
        
        for registry_key in registry_keys:
            try:
                # Try to create/open registry key
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_key) as key:
                    winreg.SetValueEx(key, "AllowLiveTrading", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowDllImport", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowWebRequest", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowAutoTrading", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowExternalExperts", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowExternalSignals", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowExternalAlerts", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendNotifications", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendEmail", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendSMS", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendPush", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendWebRequest", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendFTP", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminal", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminalEmail", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminalSMS", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminalPush", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminalWebRequest", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminalFTP", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, "AllowSendTerminalTerminal", 0, winreg.REG_DWORD, 1)
                
                print(f"✅ Algorithmic trading enabled in registry: {registry_key}")
                return True
                
            except Exception as e:
                print(f"⚠️  Could not set registry key {registry_key}: {e}")
                continue
        
        print(f"⚠️  Could not enable via registry for any key")
        return False
        
    except Exception as e:
        print(f"⚠️  Could not enable via registry: {e}")
        return False

def force_enable_autotrading_via_api(terminal_path, login, password, server):
    """Try to force enable AutoTrading via MT5 API"""
    try:
        if mt5.initialize(path=terminal_path, login=login, password=password, server=server):
            # Try to get terminal info and check if we can modify settings
            terminal_info = mt5.terminal_info()
            print(f"Terminal info - Trade allowed: {terminal_info.trade_allowed}")
            print(f"Terminal info - Trade mode: {terminal_info.trade_mode}")
            print(f"Terminal info - Connected: {terminal_info.connected}")
            print(f"Terminal info - Trade allowed: {terminal_info.trade_allowed}")
            
            # Try to get account info
            account_info = mt5.account_info()
            if account_info:
                print(f"Account info - Trade allowed: {account_info.trade_allowed}")
                print(f"Account info - Trade mode: {account_info.trade_mode}")
                print(f"Account info - Trade expert: {account_info.trade_expert}")
            
            mt5.shutdown()
            return True
        else:
            print(f"❌ Could not initialize MT5 for API access")
            mt5.shutdown()
            return False
    except Exception as e:
        print(f"⚠️  Could not force enable via API: {e}")
        mt5.shutdown()
        return False

def save_login_credentials(terminal_path, login, password, server):
    """Save login credentials in MT5 terminal to avoid login prompts"""
    try:
        # Get the terminal directory
        terminal_dir = os.path.dirname(terminal_path)
        
        # MT5 stores credentials in the config directory
        config_dir = os.path.join(terminal_dir, "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Create or update the accounts.ini file
        accounts_path = os.path.join(config_dir, "accounts.ini")
        
        config = configparser.ConfigParser()
        if os.path.exists(accounts_path):
            config.read(accounts_path, encoding='utf-8')
        
        # Create account section
        account_section = f"Account{login}"
        if account_section not in config:
            config[account_section] = {}
        
        # Save credentials
        config[account_section]['Login'] = str(login)
        config[account_section]['Password'] = password
        config[account_section]['Server'] = server
        config[account_section]['SavePassword'] = '1'
        config[account_section]['AutoLogin'] = '1'
        
        # Write the configuration
        with open(accounts_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        print(f"✅ Saved login credentials for account {login}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save login credentials: {e}")
        return False

def start_mt5_terminal(path):
    """Start MT5 terminal in headless mode"""
    try:
        # Save login credentials before starting
        if "master" in path.lower():
            save_login_credentials(path, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER)
        elif "slave" in path.lower():
            save_login_credentials(path, SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER)
        
        # Enable algorithmic trading in config before starting
        enable_algo_trading_in_config(path)
        
        # Try registry method as well
        enable_algo_trading_via_registry(path)
        
        # Launch with portable mode and headless flags
        subprocess.Popen([path, "/portable", "/headless"])
        time.sleep(10)  # Give MT5 more time to start in headless mode
        print(f"✅ Started MT5 terminal: {path}")
    except Exception as e:
        print(f"❌ Error starting MT5 terminal: {e}")

def wait_for_terminal_ready(terminal_path, login, password, server, max_attempts=30):
    """Wait for terminal to be ready and connected"""
    print(f"⏳ Waiting for terminal to be ready...")
    
    for attempt in range(max_attempts):
        try:
            if mt5.initialize(path=terminal_path, login=login, password=password, server=server):
                account_info = mt5.account_info()
                if account_info:
                    print(f"✅ Terminal ready! Account: {account_info.login}")
                    mt5.shutdown()
                    return True
                else:
                    print(f"⚠️  Terminal connected but no account info (attempt {attempt + 1})")
                    mt5.shutdown()
            else:
                print(f"⚠️  Terminal not ready yet (attempt {attempt + 1})")
        except Exception as e:
            print(f"⚠️  Connection attempt {attempt + 1} failed: {e}")
            mt5.shutdown()
        
        time.sleep(5)  # Wait 5 seconds between attempts
    
    print(f"❌ Terminal not ready after {max_attempts} attempts")
    return False

def check_autotrading_status(terminal_path, login, password, server):
    """Check if AutoTrading is currently enabled"""
    try:
        if mt5.initialize(path=terminal_path, login=login, password=password, server=server):
            terminal_info = mt5.terminal_info()
            mt5.shutdown()
            return terminal_info.trade_allowed
        else:
            mt5.shutdown()
            return False
    except Exception as e:
        print(f"⚠️  Could not check AutoTrading status: {e}")
        mt5.shutdown()
        return False

def setup_single_terminal(terminal_path, login, password, server, terminal_name):
    """Setup a single terminal: launch, wait for connection, verify AutoTrading"""
    try:
        print(f"\n{'='*60}")
        print(f"🚀 Setting up {terminal_name} terminal...")
        print(f"{'='*60}")
        
        # Step 1: Save credentials and launch terminal
        print(f"📋 Step 1: Saving credentials for {terminal_name}...")
        save_login_credentials(terminal_path, login, password, server)
        
        print(f"🚀 Step 2: Launching {terminal_name} terminal...")
        start_mt5_terminal(terminal_path)
        
        # Step 3: Wait for terminal to be ready
        print(f"⏳ Step 3: Waiting for {terminal_name} terminal to be ready...")
        if not wait_for_terminal_ready(terminal_path, login, password, server):
            print(f"❌ {terminal_name} terminal not ready")
            return False
        
        # Step 4: Try to force enable AutoTrading via API
        print(f"🔧 Step 4: Attempting to force enable AutoTrading for {terminal_name}...")
        force_enable_autotrading_via_api(terminal_path, login, password, server)
        
        # Step 5: Verify AutoTrading is enabled
        print(f"✅ Step 5: Verifying AutoTrading for {terminal_name}...")
        autotrading_enabled = False
        for attempt in range(10):  # Increased attempts
            try:
                if check_autotrading_status(terminal_path, login, password, server):
                    print(f"✅ CONFIRMED: AutoTrading is ENABLED for {terminal_name}")
                    autotrading_enabled = True
                    break
                else:
                    print(f"❌ AutoTrading is DISABLED for {terminal_name} (attempt {attempt + 1})")
                    
                    # Try to restart terminal if AutoTrading is still disabled after several attempts
                    if attempt == 5:
                        print(f"🔄 Attempting to restart {terminal_name} terminal to enable AutoTrading...")
                        # Kill existing process
                        try:
                            subprocess.run(['taskkill', '/f', '/im', 'terminal64.exe'], 
                                         capture_output=True, check=False)
                            time.sleep(5)
                        except:
                            pass
                        
                        # Restart with different flags
                        try:
                            subprocess.Popen([terminal_path, "/portable", "/headless", "/autotrading"])
                            time.sleep(15)
                        except:
                            pass
                    
            except Exception as e:
                print(f"⚠️  AutoTrading verification attempt {attempt + 1} failed: {e}")
            
            if attempt < 9:  # Don't sleep after last attempt
                time.sleep(3)
        
        if not autotrading_enabled:
            print(f"⚠️  AutoTrading could not be enabled for {terminal_name}, but continuing anyway...")
            # Don't exit, just continue with the setup
            return True
        
        return autotrading_enabled
        
    except Exception as e:
        print(f"❌ Error setting up {terminal_name} terminal: {e}")
        return False

def init_account(login, password, server, terminal_path):
    """Initialize MT5 account connection"""
    if not mt5.initialize(path=terminal_path, login=login, password=password, server=server):
        print(f"❌ Failed to initialize MT5 account {login}: {mt5.last_error()}")
        return False
    
    account_info = mt5.account_info()
    if account_info:
        print(f"✅ Account {login} logged in successfully on terminal: {terminal_path}")
        return True
    else:
        print(f"❌ Account {login} connected but no account info")
        mt5.shutdown()
        return False

def get_master_positions():
    """Get all open positions from master account"""
    return mt5.positions_get()

def get_safe_tick_price(symbol, order_type):
    """Get tick price with fallback to symbol info if tick is not available"""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        # Fallback to symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"❌ Cannot get price info for {symbol}")
            return None
        
        if order_type == 0:  # BUY
            return symbol_info.ask
        else:  # SELL
            return symbol_info.bid
    else:
        if order_type == 0:  # BUY
            return tick.ask
        else:  # SELL
            return tick.bid

def copy_position_to_slave(position):
    """Copy a position from master to slave account"""
    symbol = position.symbol
    volume = position.volume
    order_type = position.type  # 0 = buy, 1 = sell
    
    price = get_safe_tick_price(symbol, order_type)
    if price is None:
        print(f"❌ Cannot get price for {symbol}, skipping trade")
        return False

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
        return False
    else:
        print(f"✅ Trade copied: {symbol}, {volume} lots, {'BUY' if order_type == 0 else 'SELL'}")
        return True

def close_position(position):
    """Close a position"""
    order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    
    price = get_safe_tick_price(position.symbol, order_type)
    if price is None:
        print(f"❌ Cannot get price for {position.symbol}, skipping close")
        return False

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

    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Close failed: retcode={result.retcode}, message: {result.comment}")
        return False
    return True

def positions_to_dict(positions):
    """Convert positions to a dictionary for comparison, using symbol+volume+type as key"""
    if positions is None:
        return {}
    return {(p.symbol, p.volume, p.type): p.ticket for p in positions}

def copy_trading_process():
    """Main copy trading process that runs continuously"""
    print("Starting copy trading process...")
    
    # Track previously seen master positions
    previous_master_positions = {}
    
    while True:
        try:
            # Connect to master terminal
            if init_account(MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER, MASTER_PATH):
                print("✅ Connected to master")
                master_positions = get_master_positions()
                master_snapshot = positions_to_dict(master_positions)
                mt5.shutdown()
            else:
                print("❌ Failed to connect to master, retrying...")
                time.sleep(COPY_INTERVAL)
                continue

            # Connect to slave terminal
            if init_account(SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER, SLAVE_PATH):
                print("✅ Connected to slave")
                slave_positions = get_master_positions()
                slave_snapshot = positions_to_dict(slave_positions)

                # Find new positions (positions in master that weren't there before)
                new_positions = {}
                for pos_key, master_ticket in master_snapshot.items():
                    if pos_key not in previous_master_positions:
                        new_positions[pos_key] = master_ticket

                if new_positions:
                    print(f"🎯 Found {len(new_positions)} new positions to copy")
                    # Copy only the new positions
                    for p in master_positions:
                        pos_key = (p.symbol, p.volume, p.type)
                        if pos_key in new_positions:
                            copy_position_to_slave(p)
                else:
                    print("✅ No new positions to copy")

                # Update previous master positions
                previous_master_positions = master_snapshot.copy()
                
                mt5.shutdown()
            else:
                print("❌ Failed to connect to slave, retrying...")
                time.sleep(COPY_INTERVAL)
                continue

        except Exception as e:
            print(f"❌ Error in copy trading process: {e}")
            mt5.shutdown()
        
        time.sleep(COPY_INTERVAL)

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1405657359438712903/3SR_iC1jWXOckZKRLv73Gg_l0_3v02v1vEZVwOclXfupq-jN2pUt3GFqLYzTNJZUjFCx"

def send_discord_notification(message):
    """Send simple notification to Discord"""
    try:
        payload = {
            "content": message,
            "username": "MT5 Copy Trading Bot"
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✅ Discord notification sent: {message}")
        else:
            print(f"❌ Failed to send Discord notification: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")


if __name__ == "__main__":
    print("🚀 Starting MT5 Copy Trading Setup (Headless Mode)...")
    
    # Send Discord notification that script started
    send_discord_notification("🚀 MT5 Copy Trading script started (Headless Mode)")
    
    # Step 1: Setup Master Terminal
    master_success = setup_single_terminal(
        MASTER_PATH, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER, "Master"
    )
    
    if not master_success:
        send_discord_notification("⚠️ Master terminal setup had issues but continuing...")
        print("⚠️ Master terminal setup had issues but continuing...")
    
    # Step 2: Setup Slave Terminal
    slave_success = setup_single_terminal(
        SLAVE_PATH, SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER, "Slave"
    )
    
    if not slave_success:
        send_discord_notification("⚠️ Slave terminal setup had issues but continuing...")
        print("⚠️ Slave terminal setup had issues but continuing...")
    
    # Step 3: Start Copy Trading
    print(f"\n{'='*60}")
    print("🎯 Both terminals are ready! Starting copy trading...")
    print(f"{'='*60}")
    
    # Send Discord notification that everything is ready
    send_discord_notification("✅ MT5 Copy Trading ready - Both terminals active!")
    
    try:
        copy_trading_process()
    except KeyboardInterrupt:
        send_discord_notification("⏹️ MT5 Copy Trading stopped by user")
        print("\nCopy trading stopped by user")
        mt5.shutdown()
    except Exception as e:
        send_discord_notification(f"❌ MT5 Copy Trading error: {str(e)}")
        print(f"Error: {e}")
        mt5.shutdown()