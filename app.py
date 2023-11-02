from flask import Flask, render_template, redirect, request, url_for, session, g
from forms import LoginForm, register, orderForm
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
    uid = db.Column(db.String(8), primary_key=True, nullable=False)
    password = db.Column(db.String(64), nullable = False)
    name = db.Column(db.String(20), nullable = False)

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    song_name = db.Column(db.String(50), nullable=False)
    song_artist = db.Column(db.String(50), nullable=False)
    dj_id = db.Column(db.String(8), db.ForeignKey("user.uid"), nullable=True)
    dj = db.relationship("User")
    

with app.app_context():
    db.create_all()

@app.before_request
def auth():
    if request.path in config.required_login:
        id = session.get('uid')
        print(id)
        if not id:
            session.clear()
            return redirect("/login")
        else:
            # 获取user
            # user = User.query.get(id)
            # 把user放到全局变量中
            g.user = id
            

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", user = g.user)

@app.route('/song_choice', methods=['GET', 'POST'])
def song_choice():
    if request.method == "GET":
        def getFundModel():
            retList = []
            for ret in Order.query.all():
                if not ret.dj_id:
                    retList.append(ret.__dict__)
                    pass
    
            return retList
        song_list=getFundModel()
        return render_template("song_choice.html", order_song=song_list)
    else:
        id = session.get('uid')
        users = User.query.filter_by(name=id).first()
        song1 = int(request.form.get('song1'))
        song2 = int(request.form.get('song2'))
        song1_chosen = Order.query.get(song1)
        song2_chosen = Order.query.get(song2)
        song1_chosen.dj_id = users.uid
        song2_chosen.dj_id = users.uid
        print(song2_chosen.dj_id)
        db.session.commit()
        return "选歌成功"


@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == "GET":
        form = orderForm()
        return render_template("order.html", form=form)
    else:
        form = orderForm()
        name = form.song_name.data
        artist = form.song_artist.data
        current_song = Order.query.filter_by(song_name=name).first()
        if current_song == None: # 当前数据库不存在该数据，可以注册
            song = Order(song_name = name, song_artist=artist)
            # 将定义的对象加到session
            db.session.add(song)
            # 将session同步到数据库
            db.session.commit()
            return "点歌成功"
        else:
            return "该歌曲以存在，请勿重复点歌"

# @app.route('/add')
# def add():
#     # 定义对象
#     user = User(name="timewaster", password="123456")
#     # 将定义的对象加到session
#     db.session.add(user)
#     # 将session同步到数据库
#     db.session.commit()
#     return "用户创建成功"

@app.route('/login', methods=['GET', 'POST'])
def login_form():
    if request.method == "GET":
        form = LoginForm()
        return render_template('login.html', form=form)
    else:
        form = LoginForm()
        username = form.username.data
        password = form.password.data 
        # print(username)
        users = User.query.filter_by(name=username).first()
        if users and users.password == password:
            session['uid'] = username
            return redirect('/dashboard')
        else:
            session.pop("uid", None)
            return "账号或密码错误"

@app.route('/register', methods=['GET', 'POST'])
def register_form():
    if request.method == "GET":
        form = register()
        return render_template('register.html', form=form)
    else:
        form = register()
        uid = form.uid.data
        username = form.username.data
        password = form.password.data
        current_id = User.query.filter_by(uid=uid).first()
        if current_id == None: # 当前数据库不存在该数据，可以注册
            user = User(uid = uid, name=username, password=password)
            # 将定义的对象加到session
            db.session.add(user)
            # 将session同步到数据库
            db.session.commit()
            return "用户创建成功"
        else:
            return "用户已存在"

if __name__ == '__main__':
    app.run(debug=True)
