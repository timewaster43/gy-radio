from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class LoginForm(FlaskForm):
    """ 登录表单的实现 """
    username = StringField(label='用户名', default='admin')
    password = PasswordField(label='密码')
    submit = SubmitField('登录')

class register(FlaskForm):
    """ 注册表单的实现 """
    uid = StringField(label="学号")
    username = StringField(label='姓名', default='xxx')
    password = PasswordField(label='密码')
    program = StringField(label='节目ID')
    auth = StringField(label="职位")
    submit = SubmitField('注册')

class orderForm(FlaskForm):
    """ 点歌表单的实现 """
    song_name = StringField(label="歌名")
    song_artist = StringField(label='歌手')
    submit = SubmitField('提交')

class program_arrange(FlaskForm):
    """排班"""
    # 单周排班
    od1a = StringField(label="单周周一中午")
    od1p = StringField(label="单周周一下午")
    od2a = StringField(label="单周周二中午")
    od2p = StringField(label="单周周二下午")
    od3a = StringField(label="单周周三中午")
    od3p = StringField(label="单周周三下午")
    od4a = StringField(label="单周周四中午")
    od4p = StringField(label="单周周四下午")
    od5a = StringField(label="单周周五中午")
    submit = SubmitField("确认")
