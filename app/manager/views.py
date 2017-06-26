# -*- coding: UTF-8 -*-
from flask import make_response
from flask import render_template, redirect, request, url_for, flash
from flask import send_file
from flask_login import login_user, logout_user, login_required, current_user
from . import manager
from .. import db
from ..models import User,Permission,Solution,Monthcard,Balancechangerecord,Usercar,Parkingrecord
from ..decorators import admin_required, permission_required
from .forms import SolutionForm,CardForm
import datetime

@manager.route('/home',methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_home():
    form=SolutionForm()
    nowsolution = Solution.query.filter_by(id=1).first()
    if form.validate_on_submit():
        nowsolution.mincost = int(float(form.mincost.data)*100)
        nowsolution.hourcost = int(float(form.hourcost.data)*100)
        nowsolution.daycost = int(float(form.daycost.data)*100)
        nowsolution.leastcost = int(float(form.leastcost.data)*100)
        nowsolution.freemins = form.freemins.data
        nowsolution.leastcostmins = form.leastcostmins.data
        nowsolution.monthcard = form.monthcard.data

        db.session.add(nowsolution)
        db.session.commit()
        flash(u'成功变更')
        return redirect(url_for('manager.manager_home'))
    return render_template('manager/home.html',form=form,nowsolution=nowsolution)


@manager.route('/monthcard',methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_monthcard():
    monthcard_info = Monthcard.query.all()
    form = CardForm()
    if form.validate_on_submit():
        card = Monthcard(name=form.name.data,
                         month=form.month.data,
                         cost=int(float(form.cost.data)*100))
        db.session.add(card)
        db.session.commit()
        return redirect(url_for('manager.manager_monthcard'))
    elif form.name.data is not None or form.month.data is not None or form.cost.data is not None:
        flash(u'添加信息有误,请核对!')
    return render_template('manager/monthcard.html',monthcard_info=monthcard_info,form=form)


@manager.route('/info')
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_info():
    return render_template('manager/info.html')


@manager.route('/monthcarddel/<token>')
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_monthcarddel(token):
    card = Monthcard.query.filter_by(id=token).first()
    if card is not None:
        db.session.delete(card)
        db.session.commit()
    return redirect(url_for('manager.manager_monthcard'))

import tablib
@manager.route('/download/1')
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_excel1():
    list = Balancechangerecord.query.all()
    headers = (u"用户名", u"用户邮箱", u"名称",u"时间",u'金额',u'交易前金额',u'交易后金额',u'操作者')
    info = [ ]
    data = tablib.Dataset(*info, headers=headers)
    for record in list:
        data.append([User.query.filter_by(id=record.userid).first().username, User.query.filter_by(id=record.userid).first().username, record.reason, record.time, record.amount/100, record.before_amount/100, record.after_amount/100, User.query.filter_by(id=record.collectorid).first().username])
        open('app/templates/manager/data1.xlsx', 'wb').write(data.xlsx)
    response = make_response(send_file('templates/manager/data1.xlsx'))
    response.headers["Content-Disposition"] = "attachment; filename=交易记录.xlsx;"
    return response

@manager.route('/download/2')
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_excel2():
    list = User.query.all()
    headers = (u"用户名", u"用户邮箱", u"角色",u"余额",u'邮箱确认')
    info = [ ]
    data = tablib.Dataset(*info, headers=headers)
    for record in list:
        data.append([record.username, record.email, record.role.name, record.balance/100,record.confirmed])
        open('app/templates/manager/data2.xlsx', 'wb').write(data.xlsx)
    response = make_response(send_file('templates/manager/data2.xlsx'))
    response.headers["Content-Disposition"] = "attachment; filename=用户记录.xlsx;"
    return response

@manager.route('/download/3')
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_excel3():
    list = Parkingrecord.query.all()
    headers = (u"车号", u"入库时间", u"出库时间")
    info = [ ]
    data = tablib.Dataset(*info, headers=headers)
    for record in list:
        data.append([record.name, record.in_time, record.out_time])
        open('app/templates/manager/data3.xlsx', 'wb').write(data.xlsx)
    response = make_response(send_file('templates/manager/data3.xlsx'))
    response.headers["Content-Disposition"] = "attachment; filename=停车记录.xlsx;"
    return response


@manager.route('/download/4')
@login_required
@permission_required(Permission.ADVANCEMANAGEMENT)
def manager_excel4():
    list = Usercar.query.all()
    headers = (u"车号", u"用户名", u"用户邮箱",u"月卡有效期")
    info = [ ]
    data = tablib.Dataset(*info, headers=headers)
    for record in list:
        data.append([record.name, User.query.filter_by(id=record.userid).first().username,User.query.filter_by(id=record.userid).first().email, record.monthcard_date])
        open('app/templates/manager/data4.xlsx', 'wb').write(data.xlsx)
    response = make_response(send_file('templates/manager/data4.xlsx'))
    response.headers["Content-Disposition"] = "attachment; filename=车辆信息.xlsx;"
    return response

