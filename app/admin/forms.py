# -*- coding: UTF-8 -*-
import  re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class AdduserForm(FlaskForm):
    email = StringField(u'电子邮箱地址', validators=[Required(), Length(1, 64),Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64)])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'提交')

class SearchForm(FlaskForm):
    username_email = StringField(u'关键词',validators=[Required()])
    accurate = BooleanField(u'精确搜索')
    submit = SubmitField(u'搜索')

