from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, Response
from website.utils.buy_utils import get_all_auction_data, update_auction_data
from flask_login import login_required, current_user
from website.utils.sell_utils import get_user_items
from .models import Config, Item, BotStatus
from website.logger.logger import logger
from website.db.db import db
import asyncio
import json
import time

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        if not current_user.configs:
            return redirect(url_for('views.configs'))

        elif not current_user.bot_status:
            new_bot_status = BotStatus(user_id=current_user.id)
            db.session.add(new_bot_status)
            db.session.commit()
            user_bot_status = BotStatus.query.filter_by(user_id=current_user.id).first()
            return render_template("home.html", user=current_user, user_bot_status=user_bot_status)

        else:
            user_bot_status = BotStatus.query.filter_by(user_id=current_user.id).first()
            return render_template("home.html", user=current_user, user_bot_status=user_bot_status)


@views.route('/configs', methods=['GET', 'POST'])
@login_required
def configs():
    if request.method == 'POST':
        suggested_rate = float(request.form.get('suggested_rate')).__round__(2)
        shadow_user_token = str(request.form.get('shadow_user_token')).strip()
        shadow_merchant_token = str(request.form.get('shadow_merchant_token')).strip()
        waxpeer_token = str(request.form.get('waxpeer_token')).strip()
        csgo_market_token = str(request.form.get('csgo_market_token')).strip()
        csgo_empire_token = str(request.form.get('csgo_empire_token')).strip()
        buff_rate = float(request.form.get('buff_rate')).__round__(2)
        shadowpay_discount = float(request.form.get('shadowpay_discount')).__round__(2)
        waxpeer_discount = float(request.form.get('waxpeer_discount')).__round__(2)
        market_discount = float(request.form.get('market_discount')).__round__(2)
        waxpeer_cookie = str(request.form.get('waxpeer_cookie')).strip()

        if not (bool(suggested_rate) and bool(shadow_user_token) and bool(shadow_merchant_token) and bool(waxpeer_token)
                and bool(csgo_market_token) and bool(shadowpay_discount) and bool(waxpeer_discount)
                and bool(waxpeer_cookie)) and bool(csgo_empire_token) and bool(buff_rate):
            return jsonify({"status": "error", "details": "You should fill the form fully!"})
        else:
            if not current_user.configs:
                new_config = Config(suggested_rate=suggested_rate, shadow_user_token=shadow_user_token,
                                    shadow_merchant_token=shadow_merchant_token, waxpeer_token=waxpeer_token,
                                    csgo_market_token=csgo_market_token, csgo_empire_token=csgo_empire_token,
                                    buff_rate=buff_rate, shadowpay_discount=shadowpay_discount,
                                    waxpeer_discount=waxpeer_discount, market_discount=market_discount,
                                    waxpeer_cookie=waxpeer_cookie, user_id=current_user.id)
                db.session.add(new_config)
                db.session.commit()
                return jsonify({"status": "success", "details": "Successfully updated the configs!"})
            else:
                current_rate = Config.query.filter_by(user_id=current_user.id).first().suggested_rate
                if current_rate != suggested_rate:
                    all_user_items = Item.query.filter_by(user_id=current_user.id).all()
                    for item in all_user_items:
                        if item.is_special_priced != 1 or item.is_special_priced != True:
                            item.suggested_price = float(item.buff_listing_7 * suggested_rate).__round__(2)
                    flash('Successfully updated the item prices according to new suggested rate!', category='success')
                Config.query.filter_by(
                    user_id=current_user.id).update(
                    dict(suggested_rate=suggested_rate, shadow_user_token=shadow_user_token,
                         shadow_merchant_token=shadow_merchant_token,
                         waxpeer_token=waxpeer_token,
                         csgo_market_token=csgo_market_token,
                         csgo_empire_token=csgo_empire_token,
                         buff_rate=buff_rate,
                         shadowpay_discount=shadowpay_discount,
                         waxpeer_discount=waxpeer_discount, market_discount=market_discount,
                         waxpeer_cookie=waxpeer_cookie, user_id=current_user.id))
                db.session.commit()
                return jsonify({"status": "success", "details": "Successfully updated the configs!"})

    elif request.method == "GET":
        if not current_user.configs:
            flash('You should set up your configs first!', category='error')
            return render_template("configs.html", user=current_user)
    return render_template("configs.html", user=current_user)


@views.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    if request.method == 'GET':
        if not current_user.configs:
            return redirect(url_for('views.configs'))
        else:
            shadow_token = current_user.configs[0].shadow_user_token
            waxpeer_token = current_user.configs[0].waxpeer_token
            csgo_market_token = current_user.configs[0].csgo_market_token
            result = asyncio.run(get_user_items(shadow_token=shadow_token, waxpeer_token=waxpeer_token,
                                                csgo_market_token=csgo_market_token))
            if result["status"] == "success":
                for item, values in result["items"].items():
                    shadowpay_price = values["shadowpay_price"]
                    waxpeer_price = values["waxpeer_price"]
                    csgo_market_price = values["csgo_market_price"]
                    buff_listing = values["listing"]
                    buff_buy_order = values["buy_order"]
                    buff_listing_7 = values["listing7"]
                    buff_listing30 = values["listing30"]
                    buff_listing60 = values["listing60"]
                    if "image" in values.keys() and values["image"] is not None:
                        image = values["image"]
                    else:
                        image = "-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXH5ApeO4YmlhxYQk" \
                                "nCRvCo04DEVlxkKgpot621FAR17P7NdTRH-t26q4SZlvD7PYTQgXtu5cB1g_zMyoD0mlOx5UM5ZWClcYCU" \
                                "dgU3Z1rQ_FK-xezngZO46MzOziQ1vSMmtCmIyxfkgx5SLrs4SgJFJKs/360fx360f"
                    if Item.query.filter_by(name=item, user_id=current_user.id).first():
                        Item.query.filter_by(name=item, user_id=current_user.id). \
                            update(dict(name=item, image=image,
                                        buff_listing=buff_listing,
                                        buff_listing_7=buff_listing_7,
                                        buff_listing_30=buff_listing30,
                                        buff_listing_60=buff_listing60,
                                        buff_buy_order=buff_buy_order,
                                        shadow_price=shadowpay_price,
                                        waxpeer_price=waxpeer_price,
                                        market_price=csgo_market_price))
                        db.session.commit()
                    else:
                        new_item = Item(name=item, image=image,
                                        buff_listing=buff_listing,
                                        buff_listing_7=buff_listing_7,
                                        buff_listing_30=buff_listing30,
                                        buff_listing_60=buff_listing60,
                                        buff_buy_order=buff_buy_order,
                                        suggested_price=float(buff_listing_7 *
                                                              current_user.configs[0].suggested_rate).__round__(2),
                                        shadow_price=shadowpay_price,
                                        waxpeer_price=waxpeer_price,
                                        market_price=csgo_market_price,
                                        user_id=current_user.id)
                        db.session.add(new_item)
                        db.session.commit()
                user_items = Item.query.filter_by(user_id=current_user.id).all()
                flash('Successfully Loaded All Items!', category='success')
                return render_template("items.html", user=current_user, user_items=user_items)
            else:
                flash('Could not fetch user inventory. Please try again in 2 minutes.', category='error')
                return redirect(url_for('views.home'))


@views.route('/auction', methods=['GET'])
@login_required
def empire_auction():
    if request.method == 'GET':
        if not current_user.configs:
            return redirect(url_for('views.configs'))
        else:
            csgo_empire_token = current_user.configs[0].csgo_empire_token
            shadow_token = current_user.configs[0].shadow_user_token
            csgo_market_token = current_user.configs[0].csgo_market_token
            buff_rate = current_user.configs[0].buff_rate
            result = asyncio.run(get_all_auction_data(csgo_empire_token=csgo_empire_token, shadow_token=shadow_token,
                                                      market_token=csgo_market_token, buff_rate=buff_rate))
            if result[0]["status"] == "success":
                flash('Successfully Loaded All Items!', category='success')
                return render_template("auction.html", current_auctions=result[0], empire_market_data=result[1],
                                       steam_inventories=result[2], shadowpay_market_data=result[3],
                                       csgo_market_data=result[4], buff=result[5],
                                       buff_rate=buff_rate, user=current_user)
            else:
                flash('Could not fetch user inventory. Please try again in 2 minutes.', category='error')
                return redirect(url_for('views.home'))


@views.route('/get-new-auctions')
@login_required
def get_new_auctions():
    csgo_empire_token = current_user.configs[0].csgo_empire_token

    def get_items():
        while True:
            new_auctions = update_auction_data(csgo_empire_token)

            if new_auctions[1] == "success":
                yield f"data: {json.dumps(new_auctions[0])}\n\n"
            else:
                yield f"data: Error {json.dumps(new_auctions[0])}\n\n"
                time.sleep(60)

            time.sleep(3)

    return Response(get_items(), mimetype='text/event-stream')


@views.route('/update-item', methods=['PATCH'])
@login_required
def update_item():
    if request.method == "PATCH":
        try:
            item = json.loads(request.data)
            item_id = item["itemId"]
            new_suggested_price = item["newSuggestedPrice"]
            item = Item.query.get_or_404(item_id)
            item.suggested_price = new_suggested_price
            item.is_special_priced = True
            db.session.commit()
            logger.info("success")
            return jsonify({"status": "success"})

        except BaseException as error:
            logger.error(error)
            return jsonify({"status": "error", "details": error})


@views.route('/update-bot-status', methods=['POST'])
@login_required
def update_bot_status():
    if request.method == "POST":
        try:
            bot = json.loads(request.data)
            bot_name = bot["name"]
            new_status = bot["status"]
            operation_type = bot["type"]

            if bot_name == "shadowpay":
                user_shadow_bot = BotStatus.query.filter_by(user_id=current_user.id)
                user_shadow_bot.update(dict(shadow_bot=new_status))
                db.session.commit()
            elif bot_name == "waxpeer":
                user_waxpeer_bot = BotStatus.query.filter_by(user_id=current_user.id)
                user_waxpeer_bot.update(dict(waxpeer_bot=new_status))
                db.session.commit()
            elif bot_name == "csgo_market":
                user_csgo_market_bot = BotStatus.query.filter_by(user_id=current_user.id)
                user_csgo_market_bot.update(dict(csgo_market_bot=new_status))
                db.session.commit()

            if operation_type == "start":
                flash('Bot successfully started!', category='success')
            elif operation_type == "restart":
                flash('Bot successfully restarted!', category='success')
            else:
                flash('Bot successfully stopped!', category='success')

            return jsonify({"status": "success"})

        except BaseException as error:
            logger.error(error)
            return jsonify({"status": "error", "details": error})
