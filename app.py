from flask import Flask, render_template, redirect, request, url_for, session, g, abort
from forms import LoginForm, register, orderForm, program_arrange
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table
import config
from threading import Lock
import sys

app = Flask(__name__)
lock = Lock()

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
ENGINE_URI = f"mysql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}"

SECRET_KEY = "c8yrAu4m57"

db = SQLAlchemy(app)
engine = create_engine(ENGINE_URI)
metadata = MetaData()

class User(db.Model):
    __tablename__ = "user"
    uid = db.Column(db.String(8), primary_key=True, nullable=False)
    password = db.Column(db.String(64), nullable = False)
    name = db.Column(db.String(20), nullable = False)
    program = db.Column(db.String(4), nullable = True)
    auth = db.Column(db.String(15), nullable = False)

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    song_name = db.Column(db.String(50), nullable=False)
    song_artist = db.Column(db.String(50), nullable=False)
    program = db.Column(db.String(8), db.ForeignKey("user.uid"), nullable=True)
    dj = db.relationship("User")

class Program(db.Model):
    __tablename__ = "program"
    name = db.Column(db.String(20), primary_key=True, nullable=False)
    week = db.Column(db.String(2), nullable=False)
    day = db.Column(db.String(2), nullable=False)
    period = db.Column(db.String(2), nullable=True)
    

with app.app_context():
    db.create_all()

@app.before_request
def auth():
    id = session.get('uid')
    auth = session.get('auth')
    path = request.path
    for current_path in config.required_login:
        if path in config.required_login or path.startswith(current_path):
        # print(id)
            if not id:
                session.pop("uid", None)
                session.pop("auth", None)
                abort(401)
            else:
                # 获取user
                # user = User.query.get(id)
                # 把user放到全局变量中
                g.user = id
                g.auth = id
            
def getSongs():
            retList = []
            for ret in Order.query.all():
                if not ret.program:
                    retList.append(ret.__dict__)
                    pass
    
            return retList

def getPrograms():
            retList = []
            for ret in Program.query.all():
                retList.append(ret.__dict__)
                pass
    
            return retList

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/dashboard')
def dashboard():
    user = User.query.filter_by(name=g.user).first()
    if user.program:
        prog_period = Program.query.filter_by(name=user.program).first()
        program_id = user.program
        period = prog_period.week+prog_period.day+prog_period.period
    else:
        program_id = "无需做节目"
        period = "无排班"
    return render_template("dashboard.html", user = g.user, program = program_id, period = period, auth = user.auth)

@app.route('/song_choice', methods=['GET', 'POST'])
def song_choice():
    if request.method == "GET":
        lock.acquire()
        song_list=getSongs()
        return render_template("song_choice.html", order_song=song_list)
    else:
        id = session.get('uid')
        users = User.query.filter_by(name=id).first()
        song1 = int(request.form.get('song1'))
        song2 = int(request.form.get('song2'))
        song1_chosen = Order.query.get(song1)
        song2_chosen = Order.query.get(song2)
        lock.acquire()
        try:
            if song1_chosen.program or song2_chosen.program:
                return "选歌1或选歌2已经被选择"
            song1_chosen.program = users.uid
            song2_chosen.program = users.uid
            db.session.commit()
            return "选歌成功"
        finally:
            lock.release()

@app.route('/order', methods=['GET', 'POST'])
def order():
    form = orderForm()
    if request.method == "GET":
        return render_template("order.html", form=form)
    else:
        name = form.song_name.data
        artist = form.song_artist.data
        current_song = Order.query.filter_by(song_name=name).first()
        lock.acquire()
        try:
            if current_song == None: # 当前数据库不存在该数据，可以注册
                song = Order(song_name = name, song_artist=artist)
                # 将定义的对象加到session
                db.session.add(song)
                # 将session同步到数据库
                db.session.commit()
                return "点歌成功"
            else:
                return "该歌曲以存在，请勿重复点歌"
        finally:
            lock.release()

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
    form = LoginForm()
    if request.method == "GET":
        return render_template('login.html', form=form)
    else:
        username = form.username.data
        password = form.password.data 
        # print(username)
        users = User.query.filter_by(name=username).first()
        if users and users.password == password:
            session['uid'] = username
            session['auth'] = users.auth
            return redirect('/dashboard')
        else:
            session.pop("uid", None)
            return "账号或密码错误"

@app.route('/register', methods=['GET', 'POST'])
def register_form():
    form = register()
    if request.method == "GET":
        program_list=getPrograms()
        return render_template('register.html', form=form, auth=config.auth, program_list=program_list)
    else:
        uid = form.uid.data
        username = form.username.data
        password = form.password.data
        program = request.form.get('program')
        print(program)
        auth = request.form.get('auth')
        current_id = User.query.filter_by(uid=uid).first()
        current_name = User.query.filter_by(name=username).first()
        if current_id == None and current_name == None: # 当前数据库不存在该数据，可以注册
            if program != "":
                user = User(uid = uid, name=username, password=password, program=program, auth=auth)
            else:
                user = User(uid = uid, name=username, password=password, auth=auth)
            # 将定义的对象加到session
            db.session.add(user)
            # 将session同步到数据库
            db.session.commit()
            return "用户创建成功"
        else:
            return "用户已存在"

@app.route("/arrange", methods=['GET', 'POST'])
def program_arranging():
    # print(sys.getrecursionlimit())
    form = program_arrange()
    if request.method == "GET":
        return render_template("program_arrange.html", form=form)
    else:
        # 设置表格
        table = Table('Program', metadata, autoload_with=engine)
        # 创建删除语句
        delete_statement = table.delete()
        # 执行删除操作
        with engine.begin() as connection:
            connection.execute(delete_statement)
        od1a = Program(name=form.od1a.data, week="单周", day="周一", period="中午") 
        od1p = Program(name=form.od1p.data, week="单周", day="周一", period="下午") 
        od2a = Program(name=form.od2a.data, week="单周", day="周二", period="中午") 
        od2p = Program(name=form.od2p.data, week="单周", day="周二", period="下午") 
        od3a = Program(name=form.od3a.data, week="单周", day="周三", period="中午") 
        od3p = Program(name=form.od3p.data, week="单周", day="周三", period="下午") 
        od4a = Program(name=form.od4a.data, week="单周", day="周四", period="中午") 
        od4p = Program(name=form.od4p.data, week="单周", day="周四", period="下午") 
        od5a = Program(name=form.od5a.data, week="单周", day="周五", period="中午") 
        db.session.add(od1a)
        db.session.add(od1p)
        db.session.add(od2a)
        db.session.add(od2p)
        db.session.add(od3a)
        db.session.add(od3p)
        db.session.add(od4a)
        db.session.add(od4p)
        db.session.add(od5a)
        db.session.commit()
        return "排班同步成功"

@app.route('/admin_songs/<songId>', methods=['POST'])
def reject_songs(songId):
    if request.method == 'POST':
        song = Order.query.get(songId)
        db.session.delete(song)
        db.session.commit()
        return redirect("/admin_songs")


@app.route('/admin_songs', methods=['GET'])
def admin_songs():
    if request.method == 'GET':
        songs = Order.query.filter_by(program=None).all()
        return render_template('song_admin.html', songs=songs)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
