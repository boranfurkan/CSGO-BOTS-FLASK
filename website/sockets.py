import time
from flask_socketio import SocketIO, emit
from flask_login import current_user
from .models import Config, Item
from website.utils.shadowpay import Shadow
from website.utils.waxpeer import Waxpeer
from threading import Thread

socketio = SocketIO()


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit("message", "sa")


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on("shadowpay")
def handle_new_message(message):
    stop_thread = False
    all_user_configs = Config.query.filter_by(user_id=current_user.id).first()
    shadowpay = Shadow(user_token=all_user_configs.shadow_user_token,
                       merchant_token=all_user_configs.shadow_merchant_token,
                       discount=all_user_configs.shadowpay_discount)

    if not stop_thread:
        socketio.emit("shadowpay", "Waiting user to start application! ")

    def shadow_run():
        while not stop_thread:
            try:
                shadowpay.create_links()
                time.sleep(0.3)
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
        print("Shadowpay start!")
        stop_thread = False
        all_user_items = {}
        items = Item.query.filter_by(user_id=current_user.id).all()
        for item in items:
            all_user_items[item.name] = item.suggested_price

        shadowpay.get_inventory(user_items=all_user_items)

        shadowpay_thread.start()

    elif message == "stop":
        if shadowpay_thread.is_alive():
            stop_thread = True
            emit("shadowpay", "Bot is successfully stopped!")
        else:
            emit("shadowpay", "Bot is not working!")

    elif message == "restart":
        if shadowpay_thread.is_alive():
            stop_thread = True
            shadowpay_thread.start()
            shadowpay_thread.join()
            emit("shadowpay", "Bot is successfully restarted!")
        else:
            emit("shadowpay", "Bot is not working!")


@socketio.on("waxpeer")
def handle_new_message(message):
    stop_thread = False
    all_user_configs = Config.query.filter_by(user_id=current_user.id).first()
    waxpeer = Waxpeer(token=all_user_configs.waxpeer_token, cookie=all_user_configs.waxpeer_cookie,
                      discount=all_user_configs.waxpeer_discount)

    if not stop_thread:
        socketio.emit("waxpeer", "Waiting user to start application! ")

    def waxpeer_run():
        while not stop_thread:
            try:
                waxpeer.request_market_data()
                waxpeer.set_logs([])
                logs = waxpeer.update_items()
                waxpeer.set_items_to_update([])
                waxpeer.set_market_data({})
                for log in logs:
                    socketio.emit("waxpeer", log)
                time.sleep(5)
            except BaseException as error:
                socketio.emit("waxpeer", error)

    waxpeer_thread = Thread(target=waxpeer_run)

    if message == "start":
        print("Shadowpay start!")
        stop_thread = False
        all_user_items = {}
        items = Item.query.filter_by(user_id=current_user.id).all()
        for item in items:
            all_user_items[item.name] = item.suggested_price

        waxpeer.get_inventory(user_items=all_user_items)

        waxpeer_thread.start()

    elif message == "stop":
        if waxpeer_thread.is_alive():
            stop_thread = True
            emit("waxpeer", "Bot is successfully stopped!")
        else:
            emit("waxpeer", "Bot is not working!")

    elif message == "restart":
        if waxpeer_thread.is_alive():
            stop_thread = True
            waxpeer_thread.start()
            emit("waxpeer", "Bot is successfully restarted!")
        else:
            emit("waxpeer", "Bot is not working!")
