# -*- coding: UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash,abort
from flask_login import login_user, logout_user, login_required, current_user
from . import person
from .. import db
from ..models import User,Permission,Usercar,Balancechangerecord,Monthcard,Solution
from ..decorators import admin_required, permission_required
import datetime
from .forms import AddCarForm,PaymentForm, SearchForm

@person.route('/home')
@login_required
@permission_required(Permission.USERUSE)
def person_home():
    return render_template('personaluser/home.html')


@person.route('/carmanagemnet', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USERUSE)
def person_carmanagement():
    form = AddCarForm()
    car_info = Usercar.query.filter_by(userid=current_user.id)
    car_info = list(car_info)
    cardquery = Solution.query.filter_by(id=1).first().monthcard
    if form.validate_on_submit():
        car = Usercar(name=form.carname.data,
                      userid=current_user.id)
        try:
            db.session.add(car)
            db.session.commit()
            flash(u'成功登入车辆信息！')
        except:
            flash(u'登入车辆信息过程出错！请联系管理员！')
        return redirect(url_for('personaluser.person_carmanagement'))
    elif form.carname.data is not None:
        flash(u'登入车辆信息过程出错！请重新核实信息！')
    return render_template('personaluser/carmanagement.html',car_info=car_info,today=datetime.date.today(),form=form,cardquery=cardquery)


@person.route('/infoquery', methods=['GET','POST'])
@login_required
@permission_required(Permission.USERUSE)
def person_infoquery():
    form = SearchForm()
    if form.validate_on_submit():
        if form.accurate.data is False:
            balance_info = Balancechangerecord.query.filter(Balancechangerecord.userid==current_user.id).filter(Balancechangerecord.reason.like(u'%'+form.stdate.data+u'%')).all()
            balance_info += Balancechangerecord.query.filter(Balancechangerecord.userid==current_user.id).filter(Balancechangerecord.time.like(u'%'+form.stdate.data+u'%')).all()
        else:
            balance_info = Balancechangerecord.query.filter_by(userid=current_user.id,reason=form.stdate.data).all()
            balance_info += Balancechangerecord.query.filter_by(userid=current_user.id,time=form.stdate.data).all()
        return render_template('personaluser/infoquery.html',cost_info=balance_info,form=form,se=True)
    balance_info = Balancechangerecord.query.filter_by(userid=current_user.id)
    balance_info = list(balance_info)
    balance_info.reverse()
    return render_template('personaluser/infoquery.html',cost_info=balance_info,form=form,se=False)


@person.route('/cardelete/<token>')
@login_required
@permission_required(Permission.USERUSE)
def person_cardel(token):
    car = Usercar.query.filter_by(id=token).first()
    if car is not None and car.userid is current_user.id:
        db.session.delete(car)
        db.session.commit()
    elif car is None:
        return redirect(url_for('personaluser.person_carmanagement'))
    else:
        abort(403)
    return redirect(url_for('personaluser.person_carmanagement'))


@person.route('/monthcardpay/<token>')
@login_required
@permission_required(Permission.USERUSE)
def person_monthcardpay(token):
    cardquery = Solution.query.filter_by(id=1).first().monthcard
    if not cardquery:
        abort(404)
    car = Usercar.query.filter_by(id=token).first()
    monthcard_info = Monthcard.query.all()
    if car is None or car.userid is not current_user.id:
        abort(404)
    return render_template('personaluser/monthcardpay.html',monthcard_info=monthcard_info,car=car,token1=int(token),today=datetime.date.today())


@person.route('/payment/<token1>/<token>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USERUSE)
def person_payment(token1,token):
    cardquery = Solution.query.filter_by(id=1).first().monthcard
    if not cardquery:
        abort(404)
    car = Usercar.query.filter_by(id=token1).first()
    monthcard_info = Monthcard.query.filter_by(id=token).first()
    if car is None or monthcard_info is None or car.userid is not current_user.id:
        abort(404)
    form = PaymentForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
           if current_user.balance > monthcard_info.cost:
               current_user.balance -= monthcard_info.cost
               balancerecord = Balancechangerecord(userid=current_user.id,
                                                   reason=u'月卡充值（' + monthcard_info.name + u'）',
                                                   amount=-monthcard_info.cost,
                                                   before_amount=current_user.balance + monthcard_info.cost,
                                                   after_amount=current_user.balance,
                                                   collectorid=current_user.id,
                                                   time=datetime.datetime.now()
                                                   )
               if car.fresh_monthcard(monthcard_info.month):
                   db.session.add(current_user)
                   db.session.add(balancerecord)
                   db.session.commit()
                   return  redirect(url_for('personaluser.person_carmanagement'))
               else:
                   flash(u'错误！交易失败！请联系管理员')
           else:
               flash(u'余额不足！交易失败！')
        else:
            flash(u'密码错误！交易失败！')
    return render_template('personaluser/payment.html',car=car,monthcard_info=monthcard_info,form=form,today=datetime.date.today())


