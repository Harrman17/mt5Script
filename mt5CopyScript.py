import MetaTrader5 as mt5
import time
import os
import sys

# === CONFIG ===
COPY_INTERVAL = 1  # seconds

# Credentials from env vars
MASTER_LOGIN = int(os.getenv("MASTER_LOGIN", 0))
MASTER_PASSWORD = os.getenv("MASTER_PASSWORD", "")
MASTER_SERVER = os.getenv("MASTER_SERVER", "")

SLAVE_LOGIN = int(os.getenv("SLAVE_LOGIN", 0))
SLAVE_PASSWORD = os.getenv("SLAVE_PASSWORD", "")
SLAVE_SERVER = os.getenv("SLAVE_SERVER", "")


def get_positions_for_account(login, password, server):
    if not mt5.initialize(login=login, password=password, server=server):
        print(f"❌ MT5 init failed for login {login}: {mt5.last_error()}")
        return []
    positions = mt5.positions_get() or []
    mt5.shutdown()
    return positions


def copy_position_to_slave(position):
    symbol = position.symbol
    volume = position.volume
    order_type = position.type
    price_tick = mt5.symbol_info_tick(symbol)
    if price_tick is None:
        print(f"❌ Failed to get tick for symbol {symbol}")
        return
    price = price_tick.ask if order_type == mt5.ORDER_TYPE_BUY else price_tick.bid

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
        print(f"✅ Trade copied: {symbol}, {volume} lots, {'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL'}")


def clear_slave_open_positions():
    positions = mt5.positions_get() or []
    for position in positions:
        close_position(position)


def close_position(position):
    order_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    price_tick = mt5.symbol_info_tick(position.symbol)
    if price_tick is None:
        print(f"❌ Failed to get tick for symbol {position.symbol}")
        return
    price = price_tick.bid if order_type == mt5.ORDER_TYPE_SELL else price_tick.ask

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
        print(f"❌ Close position failed: retcode={result.retcode}, message: {result.comment}")
    else:
        print(f"✅ Closed position {position.ticket} on {position.symbol}")


def positions_to_dict(positions):
    return {p.ticket: (p.symbol, p.volume, p.type) for p in positions}


def main():
    print("🚀 Trade copier starting...")

    while True:
        # Get master positions
        master_positions = get_positions_for_account(MASTER_LOGIN, MASTER_PASSWORD, MASTER_SERVER)
        if not master_positions:
            print("⚠️ No master positions found or failed to connect.")
        master_snapshot = positions_to_dict(master_positions)

        # Get slave positions
        slave_positions = get_positions_for_account(SLAVE_LOGIN, SLAVE_PASSWORD, SLAVE_SERVER)
        if not slave_positions:
            print("⚠️ No slave positions found or failed to connect.")
        slave_snapshot = positions_to_dict(slave_positions)

        if master_snapshot != slave_snapshot:
            print("🔁 Desync detected — syncing now")

            if not mt5.initialize(login=SLAVE_LOGIN, password=SLAVE_PASSWORD, server=SLAVE_SERVER):
                print(f"❌ Failed to init slave terminal for syncing: {mt5.last_error()}")
            else:
                clear_slave_open_positions()
                for p in master_positions:
                    copy_position_to_slave(p)
                mt5.shutdown()
        else:
            print("✅ Slave is already in sync with master")

        time.sleep(COPY_INTERVAL)


if __name__ == "__main__":
    main()
