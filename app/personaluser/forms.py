# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User,Usercar

class AddCarForm(FlaskForm):
    carname = StringField(u'车牌号',validators=[Regexp(u'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$',message=u'请输入正确的车牌号，如：京A88888')])
    submit = SubmitField(u'确认')

    def validate_carname(self,field):
        if Usercar.query.filter_by(name=field.data).first():
            raise ValidationError(u'车辆信息已使用！')

class PaymentForm(FlaskForm):
    password = PasswordField(u'请输入密码',validators=[Required()])
    submit = SubmitField(u'确认支付')

class SearchForm(FlaskForm):
    stdate = StringField(u'筛选词')
    accurate = BooleanField(u'精确查找')
    submit = SubmitField(u'筛选')


