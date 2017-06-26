# -*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,IntegerField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo,NumberRange
from wtforms import ValidationError
from ..models import User


class SolutionForm(FlaskForm):
    mincost = StringField(u'每满1分钟的费用（单位：元）',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    hourcost = StringField(u'每满1小时的费用（单位：元）',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    daycost = StringField(u'每满1天的费用（单位：元）',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    leastcost = StringField(u'最低费用（单位：元）',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    freemins = IntegerField(u'免费停车分钟数（单位：分钟）',validators=[NumberRange(0,100000000)])
    leastcostmins = IntegerField(u'最低费用停车分钟数（单位：分钟）',validators=[NumberRange(0,100000000)])
    monthcard = BooleanField(u'月卡充值开启')
    submit = SubmitField(u'确认变更')


class CardForm(FlaskForm):
    name = StringField(u'名称',validators=[Required()])
    month = IntegerField(u'月数',validators=[NumberRange(0,1000)])
    cost = StringField(u'费用（单位：元）',validators=[Regexp(u'^[0-9]{0,}\.{0,1}[0-9]{0,2}$',message=u'不符合金额要求')])
    submit = SubmitField(u'确认提交')
