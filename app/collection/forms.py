# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo,NumberRange
from wtforms import ValidationError
from ..models import User

class PayForm(FlaskForm):
    email = StringField(u'充值账户', validators=[Required(), Length(1, 64),
                                             Email()])
    money = StringField(u'充值金额（单位：元）',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    password = PasswordField(u'您的密码')
    submit = SubmitField(u'确认充值')

    def validate_email(self,field):
        user = User.query.filter_by(email=field.data).first()
        if user is None:
            raise ValidationError(u'邮箱不存在')
        elif not user.confirmed:
            raise ValidationError(u'邮箱未验证')


class InForm(FlaskForm):
    name = StringField(u'车牌号',validators=[Regexp(u'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$',message=u'请输入正确的车牌号，如：京A88888')])
    submit = SubmitField(u'确认入库')


class OutForm(FlaskForm):
    name = StringField(u'车牌号',validators=[Regexp(u'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领A-Z]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂学警港澳]{1}$',message=u'请输入正确的车牌号，如：京A88888')])
    submit = SubmitField(u'确认出库')


class OutpayForm(FlaskForm):
    money = StringField(u'实收金额',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    submit = SubmitField(u'确认')


class OtherForm(FlaskForm):
    email = StringField(u'交易账户', validators=[Required(), Length(1, 64),
                                             Email()])
    money = StringField(u'充值金额（可正可负）（单位：元）',validators=[Regexp(u'^\-{0,1}[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    reason = StringField(u'交易项目',validators=[Required()])
    password = PasswordField(u'您的密码')
    submit = SubmitField(u'确认交易')
