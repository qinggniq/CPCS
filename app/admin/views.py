# -*- coding: UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import admin
from .. import db
from ..models import User,Permission,Balancechangerecord,Nowparking,Parkingrecord,Solution,Usercar
from ..decorators import admin_required, permission_required
from .forms import AdduserForm,SearchForm

@admin.route('/home', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def admin_home():
    userlist = User.query.all()
    form = AdduserForm()
    form1 = SearchForm()
    if form1.validate_on_submit():
        if not form1.accurate.data:
            userlist1 = User.query.filter(User.username.like(u'%'+form1.username_email.data+u'%')).all()
            userlist2 = User.query.filter(User.email.like(u'%'+form1.username_email.data+u'%')).all()
        else:
            userlist1 = User.query.filter_by(username=form1.username_email.data).all()
            userlist2 = User.query.filter_by(email=form1.username_email.data).all()
        userlistall = userlist1 + userlist2
        return render_template('admin/home.html',userlist=userlistall,form=form,form1=form1,ch=True)
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first() is None:
            if User.query.filter_by(username=form.username.data).first() is None:
                user=User(email=form.email.data,
                          username=form.username.data,
                          password=form.password.data)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('admin.admin_home'))
            else:
                flash(u'添加用户错误，用户名已被注册！')
        else:
            flash(u'添加用户错误，邮箱已被注册！')
    elif form.username.data is not None or form.email.data is not None or form.password.data is not None:
        flash(u'添加用户错误，请核对。')
    return render_template('admin/home.html',userlist=userlist,form=form,form1=form1,ch=False)


@admin.route('/confirm/<token>')
@login_required
@permission_required(Permission.ADMINISTER)
def admin_confirm(token):
    user = User.query.filter_by(id=token).first()
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin.admin_home'))

@admin.route('/change/<token>/<token1>')
@login_required
@permission_required(Permission.ADMINISTER)
def admin_change(token,token1):
    user = User.query.filter_by(id=token).first()
    user.role_id = token1
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('admin.admin_home'))


@admin.route('/del/<token>')
@login_required
@permission_required(Permission.ADMINISTER)
def admin_del(token):
    user = User.query.filter_by(id=token).first()
    if user is None:
        return redirect(url_for('admin.admin_home'))
    usercar = Usercar.query.filter_by(userid=user.id).all()
    userbalance = Balancechangerecord.query.filter_by(userid=user.id).all()
    for car in usercar:
        db.session.delete(car)
    for balance in userbalance:
        db.session.delete(balance)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.admin_home'))

