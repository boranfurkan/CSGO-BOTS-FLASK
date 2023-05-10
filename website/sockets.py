import time
from threading import Thread

from flask_login import current_user
from flask_socketio import SocketIO, emit

from website.utils.shadowpay import Shadow
from website.utils.waxpeer import Waxpeer
from website.utils.csgo_market import CsgoMarket

from .models import Config, Item

socketio = SocketIO()
is_shadowpay_working = False
is_waxpeer_working = False
is_csgo_market_working = False


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit("message", "sa")


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on("shadowpay")
def handle_new_message(message):
    global is_shadowpay_working
    all_user_configs = Config.query.filter_by(user_id=current_user.id).first()
    shadowpay = Shadow(user_token=all_user_configs.shadow_user_token,
                       merchant_token=all_user_configs.shadow_merchant_token,
                       discount=all_user_configs.shadowpay_discount)

    def shadow_run():
        while is_shadowpay_working:
            try:
                shadowpay.create_links()
                time.sleep(0.05)
                shadowpay.set_logs([])
                logs = shadowpay.update_items()
                shadowpay.set_items_to_update([])
                shadowpay.set_links_array([])
                shadowpay.set_market_data({})
                for log in logs:
                    socketio.emit("shadowpay", log)
            except BaseException as error:
                socketio.emit("shadowpay", error)

    shadowpay_thread = Thread(target=shadow_run)

    if message == "start":
        is_shadowpay_working = True
        all_user_items = {}
        items = Item.query.filter_by(user_id=current_user.id).all()
        for item in items:
            all_user_items[item.name] = item.suggested_price

        shadowpay.get_inventory(user_items=all_user_items)

        shadowpay_thread.start()
        socketio.emit("shadowpay", "Bot is successfully started!")

    elif message == "stop":
        if is_shadowpay_working:
            is_shadowpay_working = False
            socketio.emit("shadowpay", "Bot is successfully stopped!")
        else:
            socketio.emit("shadowpay", "Bot is not working!")


@socketio.on("waxpeer")
def handle_new_message(message):
    global is_waxpeer_working
    all_user_configs = Config.query.filter_by(user_id=current_user.id).first()
    waxpeer = Waxpeer(token=all_user_configs.waxpeer_token, cookie=all_user_configs.waxpeer_cookie,
                      discount=all_user_configs.waxpeer_discount)

    def waxpeer_run():
        while is_waxpeer_working:
            try:
                waxpeer.request_market_data()
                waxpeer.set_logs([])
                logs = waxpeer.update_items()
                waxpeer.set_items_to_update([])
                waxpeer.set_market_data({})
                for log in logs:
                    socketio.emit("waxpeer", log)

                is_online = waxpeer.make_user_online()
                socketio.emit("waxpeer", is_online)

                time.sleep(10)
            except BaseException as error:
                socketio.emit("waxpeer", error)

    waxpeer_thread = Thread(target=waxpeer_run)

    if message == "start":
        is_waxpeer_working = True
        all_user_items = {}
        items = Item.query.filter_by(user_id=current_user.id).all()
        for item in items:
            all_user_items[item.name] = item.suggested_price

        waxpeer.get_inventory(user_items=all_user_items)

        waxpeer_thread.start()

    elif message == "stop":
        if is_waxpeer_working:
            is_waxpeer_working = False
            emit("waxpeer", "Bot is successfully stopped!")
        else:
            emit("waxpeer", "Bot is not working!")


@socketio.on("csgo_market")
def handle_new_message(message):
    global is_csgo_market_working
    all_user_configs = Config.query.filter_by(user_id=current_user.id).first()
    csgo_market = CsgoMarket(secret_key=all_user_configs.csgo_market_token, discount=all_user_configs.market_discount)

    def csgo_market_run():
        while is_csgo_market_working:
            try:
                csgo_market.create_links()
                csgo_market.request_market_data()
                csgo_market.set_logs([])
                logs = csgo_market.update_items()
                csgo_market.set_items_to_update({})
                csgo_market.set_links_array([])
                csgo_market.set_market_data({})
                for log in logs:
                    socketio.emit("csgo_market", log)

                is_online = csgo_market.make_user_online()
                socketio.emit("csgo_market", is_online)
                time.sleep(3)
            except BaseException as error:
                socketio.emit("csgo_market", error)

    csgo_market_thread = Thread(target=csgo_market_run)

    if message == "start":
        is_csgo_market_working = True
        all_user_items = {}
        items = Item.query.filter_by(user_id=current_user.id).all()
        for item in items:
            all_user_items[item.name] = item.suggested_price

        csgo_market.get_inventory(user_items=all_user_items)

        csgo_market_thread.start()
        socketio.emit("csgo_market", "Bot is successfully started!")

    elif message == "stop":
        if is_csgo_market_working:
            is_csgo_market_working = False
            socketio.emit("csgo_market", "Bot is successfully stopped!")
        else:
            socketio.emit("csgo_market", "Bot is not working!")
