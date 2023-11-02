from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class LoginForm(FlaskForm):
    """ 登录表单的实现 """
    username = StringField(label='用户名', default='admin')
    password = PasswordField(label='密码')
    submit = SubmitField('登录')

class register(FlaskForm):
    """ 登录表单的实现 """
    uid = StringField(label="学号")
    username = StringField(label='姓名', default='xxx')
    password = PasswordField(label='密码')
    submit = SubmitField('注册')

class orderForm(FlaskForm):
    """ 登录表单的实现 """
    song_name = StringField(label="歌名")
    song_artist = StringField(label='歌手')
    submit = SubmitField('提交')
