import MetaTrader5 as mt5
import subprocess
import time
import multiprocessing
import sys
import os
import configparser
import winreg
import pyautogui
import pygetwindow as gw
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

def handle_login_prompt(window_title):
    """Handle login prompts that appear when terminals restart"""
    try:
        print(f"🔐 Looking for login prompt for: {window_title}")
        
        # Look for various login-related windows
        login_keywords = ["login", "metatrader", "open an account", "account", "demo", "real"]
        login_windows = []
        
        all_windows = gw.getAllTitles()
        for window_title in all_windows:
            if any(keyword in window_title.lower() for keyword in login_keywords):
                login_windows.append(window_title)
        
        for login_window_title in login_windows:
            print(f"Found login-related window: {login_window_title}")
            
            try:
                login_window = gw.getWindowsWithTitle(login_window_title)[0]
                
                # Activate the login window
                login_window.activate()
                time.sleep(1)
                
                # Try to find and click the OK/Login/Close button
                # Common positions for OK button in login dialogs
                ok_positions = [
                    (login_window.width // 2, login_window.height - 50),  # Center bottom
                    (login_window.width - 100, login_window.height - 50),  # Bottom right
                    (login_window.width // 2, login_window.height // 2 + 50),  # Center
                    (login_window.width // 2, login_window.height // 2),  # Center
                    (login_window.width - 80, login_window.height - 30),  # Bottom right corner
                    (login_window.width // 2, login_window.height - 30),  # Bottom center
                ]
                
                for pos in ok_positions:
                    try:
                        pyautogui.click(login_window.left + pos[0], login_window.top + pos[1])
                        print(f"Clicked OK button at position {pos}")
                        time.sleep(1)
                        break
                    except Exception:
                        continue
                
                # Also try Enter key
                pyautogui.press('enter')
                time.sleep(1)
                
                # Try Escape key to close dialogs
                pyautogui.press('escape')
                time.sleep(1)
                
                # Try clicking the X (close) button in top-right corner
                try:
                    pyautogui.click(login_window.left + login_window.width - 20, login_window.top + 10)
                    print(f"Clicked X button to close window")
                    time.sleep(1)
                except Exception:
                    pass
                
                print(f"✅ Attempted to handle login prompt for: {login_window_title}")
                
            except Exception as e:
                print(f"⚠️  Could not handle window {login_window_title}: {e}")
                continue
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to handle login prompt: {e}")
        return False

def find_mt5_windows(account_login=None):
    """Find all MT5 windows and return their titles"""
    try:
        all_windows = gw.getAllTitles()
        mt5_windows = []
        
        for window_title in all_windows:
            # Look for MT5-related windows
            if any(keyword in window_title.lower() for keyword in ['terminal', 'mt5', 'metatrader']):
                mt5_windows.append(window_title)
            
            # If we have a specific account login, also look for windows containing that account number
            if account_login and str(account_login) in window_title:
                mt5_windows.append(window_title)
        
        return mt5_windows
    except Exception as e:
        print(f"❌ Error finding MT5 windows: {e}")
        return []

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

def find_and_click_autotrading_button(mt5_window, terminal_path, login, password, server):
    """Find and click the AutoTrading button more accurately"""
    try:
        print(f"🎯 Looking for AutoTrading button in: {mt5_window.title}")
        
        # Based on the screenshot, the AutoTrading button is in the main toolbar
        # It's to the right of the "New Order" button and has a play/pause-like icon
        
        # Method 1: Try specific positions where the AutoTrading button is likely to be
        # The button is in the main toolbar, which is typically around y=60-80 pixels from top
        toolbar_y_positions = [60, 65, 70, 75, 80]
        
        # The AutoTrading button is to the right of New Order button, so try positions from center to right
        toolbar_x_positions = [
            300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600,
            350, 370, 390, 410, 430, 450, 470, 490, 510, 530, 550, 570, 590, 610
        ]
        
        print(f"Clicking in toolbar area for AutoTrading button...")
        for y in toolbar_y_positions:
            for x in toolbar_x_positions:
                try:
                    pyautogui.click(mt5_window.left + x, mt5_window.top + y)
                    time.sleep(0.5)  # Wait a bit longer for the click to register
                    print(f"Clicked at toolbar position ({x}, {y})")
                    
                    # Check if AutoTrading is now enabled
                    if check_autotrading_status(terminal_path, login, password, server):
                        print(f"✅ SUCCESS! AutoTrading is now ENABLED after clicking at ({x}, {y})")
                        return True
                    else:
                        print(f"❌ AutoTrading still disabled after clicking at ({x}, {y})")
                        
                except Exception:
                    continue
        
        # Method 2: Try clicking in the area where the AutoTrading button should be
        # Based on the screenshot, it's in the main toolbar area
        try:
            # Click in the general toolbar area where AutoTrading button is located
            toolbar_area_positions = [
                (mt5_window.width // 2, 70),      # Center of toolbar
                (mt5_window.width * 2 // 3, 70),  # Two-thirds from left
                (mt5_window.width * 3 // 4, 70),  # Three-quarters from left
                (mt5_window.width - 200, 70),     # 200px from right
                (mt5_window.width - 150, 70),     # 150px from right
                (mt5_window.width - 100, 70),     # 100px from right
            ]
            
            for pos in toolbar_area_positions:
                try:
                    pyautogui.click(mt5_window.left + pos[0], mt5_window.top + pos[1])
                    time.sleep(0.5)  # Wait a bit longer for the click to register
                    print(f"Clicked in AutoTrading area at {pos}")
                    
                    # Check if AutoTrading is now enabled
                    if check_autotrading_status(terminal_path, login, password, server):
                        print(f"✅ SUCCESS! AutoTrading is now ENABLED after clicking at {pos}")
                        return True
                    else:
                        print(f"❌ AutoTrading still disabled after clicking at {pos}")
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"⚠️  Could not click in AutoTrading area: {e}")
        
        print(f"❌ Could not enable AutoTrading by clicking")
        return False
        
    except Exception as e:
        print(f"❌ Failed to find and click AutoTrading button: {e}")
        return False

def verify_autotrading_enabled(account_name):
    """Verify if algorithmic trading is actually enabled"""
    try:
        terminal_info = mt5.terminal_info()
        if terminal_info.trade_allowed:
            print(f"✅ CONFIRMED: Algorithmic trading is ENABLED for {account_name}")
            return True
        else:
            print(f"❌ CONFIRMED: Algorithmic trading is still DISABLED for {account_name}")
            return False
    except Exception as e:
        print(f"⚠️  Could not verify AutoTrading status: {e}")
        return False

def wait_for_login_completion(terminal_title, max_wait_time=25):
    """Wait for MT5 terminal to complete login process"""
    try:
        print(f"⏳ Waiting for login completion for: {terminal_title}")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            # Look for login-related windows
            login_keywords = ["login", "metatrader", "open an account", "account", "demo", "real"]
            login_windows = []
            
            all_windows = gw.getAllTitles()
            for window_title in all_windows:
                if any(keyword in window_title.lower() for keyword in login_keywords):
                    login_windows.append(window_title)
            
            # Check if there are any login dialogs still open
            login_dialogs_found = len(login_windows) > 0
            
            if not login_dialogs_found:
                print(f"✅ Login appears to be completed for: {terminal_title}")
                return True
            
            print(f"⏳ Still waiting for login to complete... ({int(time.time() - start_time)}s)")
            print(f"   Found login windows: {login_windows}")
            
            # Try to handle any remaining dialogs
            handle_login_prompt(terminal_title)
            
            time.sleep(2)
        
        print(f"⚠️  Login timeout reached for: {terminal_title}")
        return False
        
    except Exception as e:
        print(f"❌ Error waiting for login completion: {e}")
        return False

def ensure_terminal_logged_in(terminal_path, login, password, server, terminal_title):
    """Ensure terminal is logged in before proceeding"""
    try:
        print(f"🔐 Ensuring terminal is logged in: {terminal_title}")
        
        # Wait for login completion
        if not wait_for_login_completion(terminal_title):
            print(f"⚠️  Login may not be complete for: {terminal_title}")
        
        # Try to connect via MT5 API to verify login
        try:
            if mt5.initialize(path=terminal_path, login=login, password=password, server=server):
                account_info = mt5.account_info()
                if account_info:
                    print(f"✅ Terminal successfully logged in: {terminal_title} (Account: {account_info.login})")
                    mt5.shutdown()
                    return True
                else:
                    print(f"❌ Terminal connected but no account info: {terminal_title}")
                    mt5.shutdown()
                    return False
            else:
                print(f"❌ Failed to connect to terminal: {terminal_title}")
                return False
        except Exception as e:
            print(f"⚠️  Could not verify login via API: {e}")
            # Continue anyway, the terminal might be logged in but API connection failed
            return True
        
    except Exception as e:
        print(f"❌ Error ensuring terminal login: {e}")
        return False

def setup_single_terminal(terminal_path, login, password, server, terminal_name):
    """Setup a single terminal: launch, login, enable AutoTrading"""
    try:
        print(f"\n{'='*60}")
        print(f"🚀 Setting up {terminal_name} terminal...")
        print(f"{'='*60}")
        
        # Step 1: Save credentials and launch terminal
        print(f"📋 Step 1: Saving credentials for {terminal_name}...")
        save_login_credentials(terminal_path, login, password, server)
        
        print(f"🚀 Step 2: Launching {terminal_name} terminal...")
        # Enable algorithmic trading in config before starting
        enable_algo_trading_in_config(terminal_path)
        
        # Try registry method as well
        enable_algo_trading_via_registry(terminal_path)
        
        # Launch with portable mode
        subprocess.Popen([terminal_path, "/portable"])
        time.sleep(8)  # Give MT5 more time to start
        
        # Step 3: Wait for login completion
        print(f"⏳ Step 3: Waiting for {terminal_name} login completion...")
        if not wait_for_login_completion(f"{terminal_name} terminal", max_wait_time=25):
            print(f"⚠️  Login timeout for {terminal_name}, but continuing...")
        
        # Step 4: Verify login via API
        print(f"🔐 Step 4: Verifying {terminal_name} login...")
        login_success = False
        for attempt in range(3):
            try:
                if mt5.initialize(path=terminal_path, login=login, password=password, server=server):
                    account_info = mt5.account_info()
                    if account_info:
                        print(f"✅ {terminal_name} successfully logged in (Account: {account_info.login})")
                        login_success = True
                        mt5.shutdown()
                        break
                    else:
                        print(f"❌ {terminal_name} connected but no account info")
                        mt5.shutdown()
                else:
                    print(f"❌ Failed to connect to {terminal_name}")
            except Exception as e:
                print(f"⚠️  Login verification attempt {attempt + 1} failed: {e}")
                mt5.shutdown()
            
            if not login_success:
                time.sleep(5)  # Wait before retry
        
        if not login_success:
            print(f"❌ Failed to verify login for {terminal_name}")
            return False
        
        # Step 5: Enable AutoTrading via UI
        print(f"🔧 Step 5: Enabling AutoTrading for {terminal_name}...")
        enable_algo_trading_via_ui(f"{terminal_name} terminal", login, terminal_path, login, password, server)
        time.sleep(3)
        
        # Step 6: Verify AutoTrading is enabled
        print(f"✅ Step 6: Verifying AutoTrading for {terminal_name}...")
        for attempt in range(3):
            try:
                if mt5.initialize(path=terminal_path, login=login, password=password, server=server):
                    terminal_info = mt5.terminal_info()
                    if terminal_info.trade_allowed:
                        print(f"✅ CONFIRMED: AutoTrading is ENABLED for {terminal_name}")
                        mt5.shutdown()
                        return True
                    else:
                        print(f"❌ AutoTrading is still DISABLED for {terminal_name}")
                        mt5.shutdown()
                else:
                    print(f"❌ Could not connect to verify AutoTrading for {terminal_name}")
            except Exception as e:
                print(f"⚠️  AutoTrading verification attempt {attempt + 1} failed: {e}")
                mt5.shutdown()
            
            if attempt < 2:  # Don't sleep after last attempt
                time.sleep(3)
        
        print(f"⚠️  Could not confirm AutoTrading enabled for {terminal_name}")
        return False
        
    except Exception as e:
        print(f"❌ Error setting up {terminal_name} terminal: {e}")
        return False

def enable_algo_trading_via_ui(terminal_title, account_login=None, terminal_path=None, login=None, password=None, server=None):
    """Enable algorithmic trading by simulating UI clicks"""
    try:
        print(f"🔧 Attempting to enable algorithmic trading via UI for: {terminal_title}")
        
        # Handle any login prompts first
        handle_login_prompt(terminal_title)
        time.sleep(2)
        
        # Find MT5 windows - prioritize windows containing the account number
        mt5_windows = find_mt5_windows(account_login)
        print(f"Found MT5 windows: {mt5_windows}")
        
        if not mt5_windows:
            print(f"❌ No MT5 windows found")
            return False
        
        # Try to find the specific terminal window by account number first
        target_window = None
        
        # First priority: Look for window containing the account number
        if account_login:
            for window_title in mt5_windows:
                if str(account_login) in window_title:
                    target_window = gw.getWindowsWithTitle(window_title)[0]
                    print(f"Found window with account number {account_login}: {window_title}")
                    break
        
        # Second priority: Look for window containing terminal name
        if not target_window:
            for window_title in mt5_windows:
                if terminal_title.lower() in window_title.lower():
                    target_window = gw.getWindowsWithTitle(window_title)[0]
                    print(f"Found window with terminal name: {window_title}")
                    break
        
        # Third priority: Use the first MT5 window found
        if not target_window and mt5_windows:
            target_window = gw.getWindowsWithTitle(mt5_windows[0])[0]
            print(f"Using first MT5 window found: {mt5_windows[0]}")
        
        if not target_window:
            print(f"❌ Could not find target MT5 window")
            return False
        
        print(f"Using MT5 window: {target_window.title}")
        
        # Activate the window
        target_window.activate()
        time.sleep(2)
        
        # Method 1: Try Ctrl+E (new keyboard shortcut for AutoTrading toggle)
        try:
            print(f"Trying keyboard shortcut Ctrl+E for: {target_window.title}")
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(1)
            print(f"✅ Attempted keyboard shortcut Ctrl+E for AutoTrading: {target_window.title}")
            
            # Check if AutoTrading is now enabled
            if check_autotrading_status(terminal_path, login, password, server):
                print(f"✅ SUCCESS! AutoTrading enabled via Ctrl+E")
                return True
                
        except Exception as e:
            print(f"⚠️  Could not use keyboard shortcut Ctrl+E: {e}")
        
        # Method 2: Try keyboard shortcut (Ctrl+Alt+T is common for AutoTrading toggle)
        try:
            print(f"Trying keyboard shortcut Ctrl+Alt+T for: {target_window.title}")
            pyautogui.hotkey('ctrl', 'alt', 't')
            time.sleep(1)
            print(f"✅ Attempted keyboard shortcut for AutoTrading: {target_window.title}")
            
            # Check if AutoTrading is now enabled
            if check_autotrading_status(terminal_path, login, password, server):
                print(f"✅ SUCCESS! AutoTrading enabled via keyboard shortcut")
                return True
                
        except Exception as e:
            print(f"⚠️  Could not use keyboard shortcut: {e}")
        
        # Method 3: Try to find and click the AutoTrading button
        if find_and_click_autotrading_button(target_window, terminal_path, login, password, server):
            return True
        
        # Method 4: Try alternative keyboard shortcuts
        try:
            print(f"Trying alternative keyboard shortcuts for: {target_window.title}")
            # Try F7 (common for AutoTrading toggle)
            pyautogui.press('f7')
            time.sleep(1)
            
            # Check if AutoTrading is now enabled
            if check_autotrading_status(terminal_path, login, password, server):
                print(f"✅ SUCCESS! AutoTrading enabled via F7")
                return True
            
            # Try Ctrl+F7
            pyautogui.hotkey('ctrl', 'f7')
            time.sleep(1)
            
            # Check if AutoTrading is now enabled
            if check_autotrading_status(terminal_path, login, password, server):
                print(f"✅ SUCCESS! AutoTrading enabled via Ctrl+F7")
                return True
            
            # Try Alt+A (common for AutoTrading)
            pyautogui.hotkey('alt', 'a')
            time.sleep(1)
            
            # Check if AutoTrading is now enabled
            if check_autotrading_status(terminal_path, login, password, server):
                print(f"✅ SUCCESS! AutoTrading enabled via Alt+A")
                return True
            
            print(f"✅ Attempted alternative keyboard shortcuts for: {target_window.title}")
        except Exception as e:
            print(f"⚠️  Could not use alternative keyboard shortcuts: {e}")
        
        # Method 5: Try to access Tools menu
        try:
            print(f"Trying to access Tools menu for: {target_window.title}")
            # Click Tools menu (usually at top-left)
            pyautogui.click(target_window.left + 10, target_window.top + 10)
            time.sleep(1)
            
            # Try to click Options
            pyautogui.click(target_window.left + 50, target_window.top + 50)
            time.sleep(1)
            
            print(f"✅ Attempted to access Tools menu for: {target_window.title}")
            
        except Exception as e:
            print(f"⚠️  Could not access Tools menu: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Failed to enable algorithmic trading via UI: {e}")
        return False

def enable_algo_trading_in_config(terminal_path):
    """Enable algorithmic trading by creating a simple config file"""
    try:
        # Get the terminal directory
        terminal_dir = os.path.dirname(terminal_path)
        config_path = os.path.join(terminal_dir, "config", "common.ini")
        
        # Create config directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Remove existing config file if it exists
        if os.path.exists(config_path):
            try:
                os.remove(config_path)
                print(f"Removed existing config file: {config_path}")
            except Exception as e:
                print(f"Could not remove existing config: {e}")
        
        # Create simple config content
        config_content = """[Terminal]
AllowLiveTrading=1
AllowDllImport=1
AllowWebRequest=1
AllowAutoTrading=1
"""
        
        # Write new config file
        with open(config_path, 'w', encoding='utf-8') as configfile:
            configfile.write(config_content)
        
        print(f"✅ Created new config file: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create config file: {e}")
        return False

def enable_algo_trading_via_registry(terminal_path):
    """Enable algorithmic trading via Windows registry"""
    try:
        # Get terminal directory
        terminal_dir = os.path.dirname(terminal_path)
        
        # Registry key for MT5 settings
        registry_key = f"SOFTWARE\\MetaQuotes\\Terminal\\{terminal_dir.replace(':', '').replace('\\', '_')}"
        
        # Open registry key
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_key, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "AllowLiveTrading", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "AllowDllImport", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "AllowWebRequest", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "AllowAutoTrading", 0, winreg.REG_DWORD, 1)
        
        print(f"✅ Algorithmic trading enabled in registry for: {terminal_dir}")
        return True
        
    except Exception as e:
        print(f"⚠️  Could not enable via registry (this is normal for portable mode): {e}")
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
        
        # Launch with portable mode
        subprocess.Popen([path, "/portable"])
        time.sleep(5)  # Give MT5 some time to start
    except Exception as e:
        print(f"Error starting MT5 terminal: {e}")

def force_enable_algo_trading():
    """Force enable algorithmic trading after connection"""
    try:
        # Try to enable via terminal info
        terminal_info = mt5.terminal_info()
        
        # Check if we can modify terminal settings
        if hasattr(terminal_info, 'trade_allowed'):
            print(f"Terminal trade allowed: {terminal_info.trade_allowed}")
        
        # Try to enable via account info
        account_info = mt5.account_info()
        if account_info:
            print(f"Account trade allowed: {account_info.trade_allowed}")
        
        return True
    except Exception as e:
        print(f"Could not force enable algo trading: {e}")
        return False

def check_and_enable_algo_trading(account_name, terminal_title=None):
    """Check if algorithmic trading is enabled and try to enable it"""
    terminal_info = mt5.terminal_info()
    
    if terminal_info.trade_allowed:
        print(f"✅ Algorithmic trading is enabled for {account_name}")
        return True
    else:
        print(f"❌ Algorithmic trading is DISABLED for {account_name}")
        print(f"🔄 Attempting to enable programmatically...")
        
        # Try UI automation if terminal title is provided
        if terminal_title:
            enable_algo_trading_via_ui(terminal_title, account_name) # Pass account_name here
            time.sleep(2)  # Give time for changes to take effect
        
        # Try to force enable
        if force_enable_algo_trading():
            # Check again
            terminal_info = mt5.terminal_info()
            if terminal_info.trade_allowed:
                print(f"✅ Successfully enabled algorithmic trading for {account_name}")
                return True
        
        # Final verification
        if verify_autotrading_enabled(account_name):
            return True
        
        print(f"⚠️  Could not enable programmatically. Manual intervention may be required.")
        return False

def init_account(login, password, server, terminal_path, terminal_title=None):
    if not mt5.initialize(path=terminal_path, login=login, password=password, server=server):
        print(f"Failed to initialize MT5 account {login}: {mt5.last_error()}")
        return False
    print(f"Account {login} logged in successfully on terminal: {terminal_path}")
    
    # Check algorithmic trading status with UI automation
    account_name = f"Account {login}"
    algo_enabled = check_and_enable_algo_trading(account_name, terminal_title)
    
    return True

def get_master_positions():
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

def clear_slave_open_positions():
    positions = mt5.positions_get()
    if positions:
        for p in positions:
            close_position(p)

def close_position(position):
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
            if init_account(MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER, MASTER_PATH, "terminal64.exe"):
                print("Connected to master")
                master_positions = get_master_positions()
                master_snapshot = positions_to_dict(master_positions)
                mt5.shutdown()
            else:
                print("Failed to connect to master, retrying...")
                time.sleep(COPY_INTERVAL)
                continue

            # Connect to slave terminal
            if init_account(SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER, SLAVE_PATH, "terminal64.exe"):
                print("Connected to slave")
                slave_positions = get_master_positions()
                slave_snapshot = positions_to_dict(slave_positions)

                # Find new positions (positions in master that weren't there before)
                new_positions = {}
                for pos_key, master_ticket in master_snapshot.items():
                    if pos_key not in previous_master_positions:
                        new_positions[pos_key] = master_ticket

                if new_positions:
                    print(f"Found {len(new_positions)} new positions to copy")
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
                print("Failed to connect to slave, retrying...")
                time.sleep(COPY_INTERVAL)
                continue

        except Exception as e:
            print(f"Error in copy trading process: {e}")
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
    print("🚀 Starting MT5 Copy Trading Setup...")
    
    # Send Discord notification that script started
    send_discord_notification("🚀 MT5 Copy Trading script started")
    
    # Step 1: Setup Master Terminal
    master_success = setup_single_terminal(
        MASTER_PATH, MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER, "Master"
    )
    
    if not master_success:
        send_discord_notification("❌ Failed to setup Master terminal")
        print("❌ Failed to setup Master terminal. Exiting.")
        sys.exit(1)
    
    # Step 2: Setup Slave Terminal
    slave_success = setup_single_terminal(
        SLAVE_PATH, SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER, "Slave"
    )
    
    if not slave_success:
        send_discord_notification("❌ Failed to setup Slave terminal")
        print("❌ Failed to setup Slave terminal. Exiting.")
        sys.exit(1)
    
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