"""
EC2 Account Management Server
This Flask server runs on the EC2 instance to receive and store trading account credentials
from the main application.
"""

from flask import Flask, request, jsonify
import json
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File to store account configurations
ACCOUNTS_CONFIG_FILE = "/home/ubuntu/trading_accounts.json"
SCRIPT_CONFIG_FILE = "/home/ubuntu/copy_trading_config.py"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "EC2 Account Server is running"
    })

@app.route('/update-accounts', methods=['POST'])
def update_accounts():
    """Receive and store trading account credentials"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['userId', 'masterAccount', 'slaveAccounts']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate master account
        master = data['masterAccount']
        master_required = ['login', 'password', 'server']
        for field in master_required:
            if field not in master:
                return jsonify({"error": f"Missing master account field: {field}"}), 400
        
        # Validate slave accounts
        slaves = data['slaveAccounts']
        if not isinstance(slaves, list) or len(slaves) == 0:
            return jsonify({"error": "At least one slave account is required"}), 400
        
        for i, slave in enumerate(slaves):
            for field in master_required:
                if field not in slave:
                    return jsonify({"error": f"Missing slave account {i+1} field: {field}"}), 400
        
        logger.info(f"Received account update for user: {data['userId']}")
        logger.info(f"Master account: {master['login']}")
        logger.info(f"Slave accounts: {len(slaves)}")
        
        # Store the configuration
        config_data = {
            "userId": data['userId'],
            "updatedAt": datetime.now().isoformat(),
            "masterAccount": master,
            "slaveAccounts": slaves
        }
        
        # Save to JSON file
        try:
            with open(ACCOUNTS_CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved account configuration to: {ACCOUNTS_CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to save accounts config: {e}")
            return jsonify({"error": "Failed to save configuration"}), 500
        
        # Generate Python configuration file for the copy trading script
        try:
            generate_script_config(config_data)
            logger.info(f"Generated script configuration: {SCRIPT_CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Failed to generate script config: {e}")
            return jsonify({"error": "Failed to generate script configuration"}), 500
        
        # Restart the copy trading script to pick up new config
        try:
            restart_copy_trading_script()
            logger.info("Copy trading script restart initiated")
        except Exception as e:
            logger.warning(f"Failed to restart copy trading script: {e}")
            # Don't fail the request for this, just log it
        
        return jsonify({
            "success": True,
            "message": "Account configuration updated successfully",
            "userId": data['userId'],
            "masterLogin": master['login'],
            "slaveCount": len(slaves),
            "updatedAt": config_data['updatedAt']
        })
        
    except Exception as e:
        logger.error(f"Error updating accounts: {e}")
        return jsonify({"error": "Internal server error"}), 500

def generate_script_config(config_data):
    """Generate Python configuration file for the copy trading script"""
    master = config_data['masterAccount']
    slaves = config_data['slaveAccounts']
    
    # For now, we'll use the first slave account as the primary slave
    # Later this can be enhanced to support multiple slaves
    primary_slave = slaves[0] if slaves else None
    
    config_content = f'''# Auto-generated configuration file
# Generated at: {config_data['updatedAt']}
# User ID: {config_data['userId']}

# Master Account Configuration
MASTER_LOGIN = {master['login']}
MASTER_PASSWORD = "{master['password']}"
MASTER_SERVER = "{master['server']}"

# Primary Slave Account Configuration
SLAVE_LOGIN = {primary_slave['login'] if primary_slave else 'None'}
SLAVE_PASSWORD = "{primary_slave['password'] if primary_slave else ''}"
SLAVE_SERVER = "{primary_slave['server'] if primary_slave else ''}"

# All Slave Accounts (for future multi-slave support)
SLAVE_ACCOUNTS = {json.dumps(slaves, indent=2)}

# Terminal Paths (assuming standard installation)
MASTER_PATH = r"C:\\Users\\Administrator\\Desktop\\terminals\\master\\terminal64.exe"
SLAVE_PATH = r"C:\\Users\\Administrator\\Desktop\\terminals\\slave1\\terminal64.exe"

# Copy Trading Settings
COPY_INTERVAL = 1  # seconds

# Discord Webhook (if configured)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1405657359438712903/3SR_iC1jWXOckZKRLv73Gg_l0_3v02v1vEZVwOclXfupq-jN2pUt3GFqLYzTNJZUjFCx"

print("✅ Configuration loaded successfully")
print(f"🎯 Master Account: {{MASTER_LOGIN}}")
print(f"🎯 Slave Accounts: {{len(SLAVE_ACCOUNTS)}}")
'''
    
    with open(SCRIPT_CONFIG_FILE, 'w') as f:
        f.write(config_content)

def restart_copy_trading_script():
    """Restart the copy trading script to pick up new configuration"""
    import subprocess
    import signal
    
    try:
        # Kill existing copy trading processes
        subprocess.run(['pkill', '-f', 'copy_trading'], check=False)
        
        # Wait a moment
        import time
        time.sleep(2)
        
        # Start the copy trading script in the background
        # Assuming the script is in the same directory
        subprocess.Popen([
            'python3', 
            '/home/ubuntu/copy_trading_dynamic.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        logger.info("Copy trading script restarted")
        
    except Exception as e:
        logger.error(f"Failed to restart copy trading script: {e}")
        raise

@app.route('/status', methods=['GET'])
def get_status():
    """Get current configuration status"""
    try:
        if os.path.exists(ACCOUNTS_CONFIG_FILE):
            with open(ACCOUNTS_CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            return jsonify({
                "configured": True,
                "userId": config.get('userId'),
                "updatedAt": config.get('updatedAt'),
                "masterLogin": config.get('masterAccount', {}).get('login'),
                "slaveCount": len(config.get('slaveAccounts', []))
            })
        else:
            return jsonify({
                "configured": False,
                "message": "No account configuration found"
            })
            
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": "Failed to get status"}), 500

if __name__ == '__main__':
    logger.info("Starting EC2 Account Management Server...")
    logger.info(f"Config file location: {ACCOUNTS_CONFIG_FILE}")
    logger.info(f"Script config location: {SCRIPT_CONFIG_FILE}")
    
    # Create config directory if it doesn't exist
    os.makedirs(os.path.dirname(ACCOUNTS_CONFIG_FILE), exist_ok=True)
    
    # Run the Flask server
    app.run(host='0.0.0.0', port=8000, debug=False)
