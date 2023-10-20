from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class LoginForm(FlaskForm):
    """ 登录表单的实现 """
    username = StringField(label='用户名', default='admin')
    password = PasswordField(label='密码')
    submit = SubmitField('登录')
