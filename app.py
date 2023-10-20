from flask import Flask, render_template, redirect, request, url_for, session, g
from forms import LoginForm
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)

app.config["SECRET_KEY"] = "c8yrAu4m57"
# MySQL所在主机
HOSTNAME = "127.0.0.1"
# MySQL监听端口，安装时设定为3306
PORT = 3306
# 用户名
USER = "root"
# 用户密码
PASSWORD = "root"
# 所使用的数据库
DATABASE = "gyradio_test"

DB_URI = f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

SECRET_KEY = "c8yrAu4m57"

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True,  nullable=False)
    password = db.Column(db.String(64), nullable = False)
    name = db.Column(db.String(20), nullable = False)

with app.app_context():
    db.create_all()

@app.before_request
def auth():
    if request.path in config.required_login:
        id = session.get('uid')
        if not id:
            return redirect("/form")
            session.pop('uid', None)
        else:
            # 获取user
            user = User.query.get(id)
            # 把user放到全局变量中
            g.user = id

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", user = g.user)

# @app.route('/add')
# def add():
#     # 定义对象
#     user = User(name="timewaster", password="123456")
#     # 将定义的对象加到session
#     db.session.add(user)
#     # 讲session同步到数据库
#     db.session.commit()
#     return "用户创建成功"

@app.route('/form', methods=['GET', 'POST'])
def page_form():
    if request.method == "GET":
        """ form 表单练习 """
        form = LoginForm()
        return render_template('page_form.html', form=form)
    else:
        form = LoginForm()
        username = form.username.data
        password = form.password.data 
        # print(username)
        users = User.query.filter_by(name=username).first()
        if users and users.password == password:
            return redirect('/dashboard/'+username)
        else:
            session.pop("uid", None)
            return "账号或密码错误"

if __name__ == '__main__':
    app.run(debug=True)