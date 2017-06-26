from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    USERUSE = 0x01
    BASICMANAGEMENT = 0x02
    ADVANCEMANAGEMENT = 0x04
    ADMINISTER = 0x80


'''

after db.create_all() run Role.insert_roles() and Solution.set()

'''

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.USERUSE, True),
            'Collector': (Permission.BASICMANAGEMENT, False),
            'Manager': (Permission.BASICMANAGEMENT |
                          Permission.ADVANCEMANAGEMENT, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    balance = db.Column(db.Integer,default=0)
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

import datetime
class Usercar(db.Model):
    __tablename__ = 'usercars'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True,index=True)
    userid = db.Column(db.Integer)
    monthcard_date = db.Column(db.Date,default=datetime.date.today()-datetime.timedelta(days=1))

    def check_monthcard(self):
        today = datetime.date.today()
        if today <= self.monthcard_date:
            return True
        else :
            return False

    def fresh_monthcard(self,num_month=1):
        day = datetime.date.today() - datetime.timedelta(days=1)
        if self.monthcard_date > day:
            day = self.monthcard_date
        try:
            self.monthcard_date = day + datetime.timedelta(days=30*num_month)
            db.session.add(self)
            db.session.commit()
        except:
            return False
        return True

    def __repr__(self):
        return '<User %r>' % self.name


class Nowparking(db.Model):
    __tablename__ = 'nowparkings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    in_time = db.Column(db.DateTime,default=datetime.datetime.now())

    def parking_finish(self):
        Info = {
            'CarName':self.name,
            'InTime':self.in_time,
            'OutTime':datetime.datetime.now()
        }
        return Info

    def __repr__(self):
        return '<User %r>' % self.name

class Parkingrecord(db.Model):
    __tablename__ = 'parkingrecords'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    in_time = db.Column(db.DateTime)
    out_time = db.Column(db.DateTime,default=datetime.datetime.now())

    def __repr__(self):
        return '<User %r>' % self.name

class Balancechangerecord(db.Model):
    __tablename__ = 'balancechangerecords'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, index=True)
    reason = db.Column(db.String(64))
    time = db.Column(db.DateTime,default=datetime.datetime.now())
    amount = db.Column(db.Integer)
    before_amount = db.Column(db.Integer)
    after_amount = db.Column(db.Integer)
    collectorid = db.Column(db.Integer)

    def __repr__(self):
        return '<User %r>' % self.name


class Solution(db.Model):
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key=True)
    mincost = db.Column(db.Integer,default=0)
    hourcost = db.Column(db.Integer,default=0)
    daycost = db.Column(db.Integer,default=0)
    leastcost = db.Column(db.Integer,default=0)
    freemins = db.Column(db.Integer,default=0)
    leastcostmins = db.Column(db.Integer,default=0)
    monthcard = db.Column(db.Boolean,default=False)

    @staticmethod
    def set():
        sol = Solution()
        db.session.add(sol)
        db.session.commit()


    def __repr__(self):
        return '<ID %d>' % self.id


class Monthcard(db.Model):
    __tablename__ = 'monthcards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    month = db.Column(db.Integer,default=0)
    cost = db.Column(db.Integer,default=0)

    def __repr__(self):
        return '<ID %d>' % self.id
