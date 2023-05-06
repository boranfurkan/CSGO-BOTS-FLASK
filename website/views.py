from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .api_utils import get_user_items
from .models import Config, Item
from .logger import logger
from . import db
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
        else:
            return render_template("home.html", user=current_user)


@views.route('/configs', methods=['GET', 'POST'])
@login_required
def configs():
    if request.method == 'POST':
        suggested_rate = float(request.form.get('suggested_rate')).__round__(2)
        shadow_user_token = str(request.form.get('shadow_user_token')).strip()
        shadow_merchant_token = str(request.form.get('shadow_merchant_token')).strip()
        waxpeer_token = str(request.form.get('waxpeer_token')).strip()
        csgo_market_token = str(request.form.get('csgo_market_token')).strip()
        shadowpay_discount = float(request.form.get('shadowpay_discount')).__round__(2)
        waxpeer_discount = float(request.form.get('waxpeer_discount')).__round__(2)
        market_discount = float(request.form.get('market_discount')).__round__(2)
        waxpeer_cookie = str(request.form.get('waxpeer_cookie')).strip()

        if not (bool(suggested_rate) and bool(shadow_user_token) and bool(shadow_merchant_token) and bool(waxpeer_token)
                and bool(csgo_market_token) and bool(shadowpay_discount) and bool(waxpeer_discount) and bool(
                    waxpeer_cookie)):
            flash('You should fill the form fully!!', category='error')
        else:
            if not current_user.configs:
                new_config = Config(suggested_rate=suggested_rate, shadow_user_token=shadow_user_token,
                                    shadow_merchant_token=shadow_merchant_token, waxpeer_token=waxpeer_token,
                                    csgo_market_token=csgo_market_token, shadowpay_discount=shadowpay_discount,
                                    waxpeer_discount=waxpeer_discount, market_discount=market_discount,
                                    waxpeer_cookie=waxpeer_cookie, user_id=current_user.id)
                db.session.add(new_config)
                db.session.commit()
                flash('Successfully updated the configs!', category='success')
            else:
                Config.query.filter_by(
                    user_id=current_user.id).update(
                    dict(suggested_rate=suggested_rate, shadow_user_token=shadow_user_token,
                         shadow_merchant_token=shadow_merchant_token,
                         waxpeer_token=waxpeer_token,
                         csgo_market_token=csgo_market_token,
                         shadowpay_discount=shadowpay_discount,
                         waxpeer_discount=waxpeer_discount, market_discount=market_discount,
                         waxpeer_cookie=waxpeer_cookie, user_id=current_user.id))
                db.session.commit()
                flash('Successfully updated the configs!', category='success')
    elif request.method == "GET":
        if not current_user.configs:
            flash('You should set up your configs first!', category='error')
    return render_template("configs.html", user=current_user)


@views.route('/items', methods=['GET', 'POST'])
@login_required
def items():
    if request.method == 'GET':
        if not current_user.configs[0].shadow_user_token:
            flash('You should provide your shadowpay user token', category='error')
            time.sleep(1)
            return redirect(url_for('views.configs'))
        elif not current_user.configs[0].waxpeer_token:
            flash('You should provide your waxpeer user token', category='error')
            time.sleep(1)
            return redirect(url_for('views.configs'))
        elif not current_user.configs[0].csgo_market_token:
            flash('You should provide your csgo market token', category='error')
            time.sleep(1)
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
                    if "image" in values.keys():
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
                return render_template("items.html", user=current_user, user_items=user_items)
            else:
                flash('Could not fetch user inventory. Please try again in 2 minutes.', category='error')
                return redirect(url_for('views.home'))


@views.route('/update-item', methods=['PATCH'])
@login_required
def update_item():
    try:
        item = json.loads(request.data)
        item_id = item["itemId"]
        new_suggested_price = item["newSuggestedPrice"]
        item = Item.query.get_or_404(item_id)
        item.suggested_price = new_suggested_price
        db.session.commit()
        logger.info("success")
        flash('Successfully updated the item!', category='success')
        return jsonify({"status": "success"})

    except BaseException as error:
        logger.error(error)
        return jsonify({"status": "error", "details": error})