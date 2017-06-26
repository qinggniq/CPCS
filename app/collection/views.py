# -*- coding: UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import collection
from .. import db
from ..models import User,Permission,Balancechangerecord,Nowparking,Parkingrecord,Solution,Usercar
from ..decorators import admin_required, permission_required
from .forms import PayForm,InForm,OutForm,OutpayForm, OtherForm

@collection.route('/home', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.BASICMANAGEMENT)
def collection_home():
    form = PayForm()
    paylist = Balancechangerecord.query.filter_by(collectorid=current_user.id,reason=u'账户充值').all()
    paylist.reverse()
    if form.validate_on_submit():
        if not current_user.verify_password(form.password.data):
            flash(u'密码错误，充值失败')
        else:
            user = User.query.filter_by(email=form.email.data).first()
            if not user.can(Permission.USERUSE):
                flash(u'被充值账户非用户，充值失败')
            else:
                record = Balancechangerecord(userid=user.id,
                    amount=int(float(form.money.data)*100),
                    time=datetime.datetime.now(),
                    before_amount = user.balance,
                    after_amount = user.balance+int(float(form.money.data)*100),
                    collectorid = current_user.id,
                    reason = u'账户充值'
                    )
                user.balance=user.balance+int(float(form.money.data)*100)
                db.session.add(record)
                db.session.add(user)
                db.session.commit()
                str=u'向' + user.email + u'充值'+ unicode(float(form.money.data)) + u'元成功'
                flash(str)
                return redirect(url_for('collection.collection_home'))
    elif form.email.data is not None or form.money.data is not None or form.password.data is not None:
        flash(u'充值失败！')
    return render_template('collection/home.html',form=form,paylist=paylist[0:20],User=User)


@collection.route('/inmanagement',methods=['GET', 'POST'])
@login_required
@permission_required(Permission.BASICMANAGEMENT)
def collection_inmanagement():
    form = InForm()
    inlist = Nowparking.query.all()
    inlist.reverse()
    if form.validate_on_submit():
        exist = Nowparking.query.filter_by(name=form.name.data).first()
        if not exist is None:
            str = exist.name + u'已在库中！请核对！'
            flash(str)
        else:
            now = Nowparking(name=form.name.data,
                             in_time=datetime.datetime.now())
            db.session.add(now)
            db.session.commit()
            str = now.name + u'成功入库！'
            flash(str)
            return redirect(url_for('collection.collection_inmanagement'))
    elif form.name.data is not None:
        flash(u'车辆信息有误，请核对！')
    return render_template('collection/inmanagement.html',form=form,inlist=inlist)


@collection.route('/outmanagement',methods=['GET', 'POST'])
@login_required
@permission_required(Permission.BASICMANAGEMENT)
def collection_outmanagement():
    form = OutForm()
    inlist = Nowparking.query.all()
    inlist.reverse()
    if form.validate_on_submit():
        exist = Nowparking.query.filter_by(name=form.name.data).first()
        if exist is None:
            str = form.name.data + u'未在库中！请核对！'
            flash(str)
        else:
            return redirect(url_for('collection.collection_outmanagement2',token=exist.id))
    elif form.name.data is not None:
        flash(u'车辆信息有误，请核对！')
    return render_template('collection/outmanagement.html',form=form,inlist=inlist)

import datetime
@collection.route('/outmanagement2/<token>',methods=['GET', 'POST'])
@login_required
@permission_required(Permission.BASICMANAGEMENT)
def collection_outmanagement2(token):
    query = Nowparking.query.filter_by(id=token).first()
    form = OutpayForm()
    if query is None:
        return redirect(url_for('collection.collection_outmanagement'))
    end = query.parking_finish()
    delta = end['OutTime']-end['InTime']
    payway = Solution.query.filter_by(id=1).first()
    car = Usercar.query.filter_by(name=end['CarName']).first()
    message = dict()
    user = None
    if car is not None and car.check_monthcard():
        message['info'] = u'月卡有效期内'
        message['payment'] = 0
        message['realpay'] = 0

    elif delta < datetime.timedelta(minutes=payway.freemins):
        message['info'] = u'免费停车时间内'
        message['payment'] = 0
        message['realpay'] = 0
    else :
        delta = delta-datetime.timedelta(minutes=payway.freemins)
        if delta <= datetime.timedelta(minutes=payway.leastcostmins):
            message['info'] = u'最低消费'
            message['payment'] = payway.leastcost

        else :
            message['info'] = u'正常缴费'
            delta -= datetime.timedelta(minutes=payway.leastcostmins)
            minscost = (delta.seconds // datetime.timedelta(minutes=1).seconds) * payway.mincost
            hourscost = (delta.seconds // datetime.timedelta(hours=1).seconds) * payway.hourcost
            dayscost = (delta.days // datetime.timedelta(days=1).days) * payway.daycost
            message['payment'] = payway.leastcost + minscost + hourscost + dayscost


        if car is None:
            message['realpay'] = message['payment']
            message['info'] += u'（无关联账户车辆）'

        else:
            user = User.query.filter_by(id=car.userid).first()
            if user.balance >= message['payment']:
                message['realpay'] = 0
                message['info'] += u'（已从账户自动扣款）'

            else :
                message['realpay'] = message['payment'] - user.balance
                message['info'] += u'（账户余额不足）'


    if form.validate_on_submit():
        if user is not None:
            user.balance -= message['payment'] - message['realpay']
            backmoney = int(float(form.money.data)*100) - message['realpay']
            if backmoney < 0:
                flash(u'支付金额不足，交易失败')
                return redirect(url_for('collection.collection_outmanagement2',token=token))
            else :
                parkingrecord = Parkingrecord(name=end['CarName'],in_time=end['InTime'],out_time=end['OutTime'])
                str = query.name + u'成功出库！'
                balancerecord = Balancechangerecord(userid=user.id,
                                                reason=query.name+u'停车费用',
                                                amount=-(message['payment'] - message['realpay']),
                                                before_amount=user.balance+(message['payment'] - message['realpay']),
                                                after_amount=user.balance,
                                                collectorid=current_user.id,
                                                time=datetime.datetime.now())
                db.session.delete(query)
                db.session.add(balancerecord)
                db.session.add(parkingrecord)
                db.session.commit()
                flash(str)
                return render_template('collection/outchange.html',token=backmoney)
        else:
            parkingrecord = Parkingrecord(name=end['CarName'],in_time=end['InTime'],out_time=end['OutTime'])
            backmoney = int(float(form.money.data)*100) - message['realpay']
            if backmoney < 0:
                flash(u'支付金额不足，交易失败')
                return redirect(url_for('collection.collection_outmanagement2',token=token))
            db.session.delete(query)
            db.session.add(parkingrecord)
            db.session.commit()
            return render_template('collection/outchange.html',token=backmoney)
    return render_template('collection/outmanagement2.html',form=form,message=message)

@collection.route('/others',methods=['GET', 'POST'])
@login_required
@permission_required(Permission.BASICMANAGEMENT)
def collection_others():
    form = OtherForm()
    paylist = Balancechangerecord.query.filter(Balancechangerecord.collectorid==current_user.id).filter(Balancechangerecord.reason.like(u'%其他交易%')).all()
    paylist.reverse()
    if form.validate_on_submit():
        if not current_user.verify_password(form.password.data):
            flash(u'密码错误，交易失败')
        else:
            user = User.query.filter_by(email=form.email.data).first()
            if not user.can(Permission.USERUSE):
                flash(u'交易账户非用户，交易失败')
            else:
                record = Balancechangerecord(userid=user.id,
                    amount=int(float(form.money.data)*100),
                    time=datetime.datetime.now(),
                    before_amount = user.balance,
                    after_amount = user.balance+int(float(form.money.data)*100),
                    collectorid = current_user.id,
                    reason = u'其他交易'+form.reason.data
                    )
                user.balance=user.balance+int(float(form.money.data)*100)
                db.session.add(record)
                db.session.add(user)
                db.session.commit()
                if float(form.money.data) > 0:
                    str=u'向' + user.email + u'充值'+ unicode(float(form.money.data)) + u'元成功'
                else :
                    str=u'向' + user.email + u'扣款'+ unicode(-float(form.money.data)) + u'元成功'
                flash(str)
                return redirect(url_for('collection.collection_others'))
    elif form.email.data is not None or form.money.data is not None or form.password.data is not None:
        flash(u'交易失败！')
    return render_template('collection/others.html',form=form,paylist=paylist[0:20],User=User)


@collection.route('/outchange/<token>')
@login_required
@permission_required(Permission.BASICMANAGEMENT)
def collection_outchange(token):
    return render_template('collection/outchange.html',token=int(token))



