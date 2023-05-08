import time

from flask_socketio import SocketIO, emit
from flask_login import current_user
from .models import Config, Item
from website.utils.shadowpay import Shadow
from threading import Thread

socketio = SocketIO()


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit("message", "sa")


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on("message")
def handle_new_message(message):
    print(f"New message: {message}")
    emit("message", "sa")


@socketio.on("shadowpay")
def handle_new_message(message):
    stop_thread = False
    all_configs = Config.query.filter_by(user_id=current_user.id).first()
    shadowpay = Shadow(user_token=all_configs.shadow_user_token, merchant_token=all_configs.shadow_merchant_token,
                       discount=all_configs.shadowpay_discount)

    if not stop_thread:
        emit("shadowpay", "Waiting user to start application! ")

    def shadow_run():
        while not stop_thread:
            try:
                shadowpay.create_links()
                time.sleep(1)
                logs = shadowpay.update_items()
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
