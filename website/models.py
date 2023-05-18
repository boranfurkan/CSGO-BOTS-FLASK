from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    configs = db.relationship('Config')
    bot_status = db.relationship('BotStatus')


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suggested_rate = db.Column(db.Integer)
    shadow_user_token = db.Column(db.String(150))
    shadow_merchant_token = db.Column(db.String(150))
    waxpeer_token = db.Column(db.String(150))
    csgo_market_token = db.Column(db.String(150))
    csgo_empire_token = db.Column(db.String(150))
    shadowpay_discount = db.Column(db.Integer)
    waxpeer_discount = db.Column(db.Integer)
    market_discount = db.Column(db.Integer)
    buff_rate = db.Column(db.Integer)
    waxpeer_cookie = db.Column(db.String(5000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    image = db.Column(db.String(250))
    buff_listing = db.Column(db.Integer)
    buff_listing_7 = db.Column(db.Integer)
    buff_listing_30 = db.Column(db.Integer)
    buff_listing_60 = db.Column(db.Integer)
    buff_buy_order = db.Column(db.Integer)
    suggested_price = db.Column(db.Integer)
    shadow_price = db.Column(db.Integer)
    waxpeer_price = db.Column(db.Integer)
    market_price = db.Column(db.Integer)
    is_special_priced = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class BotStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shadow_bot = db.Column(db.Boolean, default=False)
    waxpeer_bot = db.Column(db.Boolean, default=False)
    csgo_market_bot = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
