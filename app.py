from flask import Flask, render_template, request, flash, redirect, session, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from hashlib import md5
from  sqlalchemy.sql.expression import func
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqlamodel import ModelView
from flask_admin import Admin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['UPLOAD_FOLDER'] = 'static/img/upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
db = SQLAlchemy(app)
ckeditor = CKEditor(app)


class Articles(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    image_name = db.Column(db.String(100))
    category = db.Column(db.String(100))

    def __repr__(self):
        return 'Articles %r' % self.id 


class Routes(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    point_a = db.Column(db.String(100))
    point_b = db.Column(db.String(100))
    image_name = db.Column(db.String(100))

    def __repr__(self):
        return 'Routes %r' % self.id 

class Events(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    city = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    image_name = db.Column(db.String(100))
    pr = db.relationship('Favorites', backref='events', uselist=False)

    def __repr__(self):
        return 'Events %r' % self.id 

class Region(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.Text)
    image_name = db.Column(db.String(100))

    def __repr__(self):
        return 'Region %r' % self.id 


class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=True)
    root = db.Column(db.Integer, default=0)
    pr = db.relationship('Favorites', backref='users', uselist=False)
   
    def __repr__(self):
        return 'User %r' % self.id 


class Favorites(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_event = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return 'Favorites %r' % self.id 


class AdminIndex(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if 'name' in session:
            user = Users.query.filter_by(email=session['name']).first()
            if user.root!=1:
                abort(403)
            else:
                return self.render('admin/dashboard_index.html')
        else:
            abort(401)


admin = Admin(app, name='Vandroўnik',index_view=AdminIndex())

admin.add_view(ModelView(Articles, db.session))
admin.add_view(ModelView(Routes, db.session))
admin.add_view(ModelView(Events, db.session))
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(Users, db.session))


@app.route('/', methods=['GET', 'POST'])
def index():
    events_random = Events.query.order_by(func.random()).limit(3).all()
    return render_template("index.html",events_random=events_random)


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('name', None)
    if request.method == 'POST':
        email = request.form.get('email')
        password = md5(request.form.get('password').encode()).hexdigest()
        user = Users.query.filter_by(email=email,password=password).first()
        if user:
            session['name'] = Users.query.filter_by(email=email).first().email
            return redirect(url_for("index"))
        else:
            flash("Неправильная почта или пароль!", category="bad")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            user = Users(name=name,email=email,password=md5(password.encode()).hexdigest())
            db.session.add(user)
            db.session.commit()
            flash("Регистрация прошла успешно!", category="ok")
            return redirect(url_for("reg"))
        except:
            flash("Произошла ошибка! Проверьте введенные данные!", category="bad")
            db.session.rollback()
            return redirect(url_for("reg"))
    return render_template("reg.html")


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    articles = Articles.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        image = request.files['image']
        filename = secure_filename(image.filename)
        pic_name = str(uuid.uuid4()) + "_" + filename
        image.save("static/img/upload/" + pic_name)
        text = request.form.get('ckeditor')
        articles = Articles(title=title,category=category,image_name=pic_name,text=text)
        db.session.add(articles)
        db.session.commit()
        flash("Запись добавлена!", category="ok")
        return redirect(url_for("articles"))

    if request.method == 'GET':
        category = request.args.get('category')
        if category:
            category= category.capitalize()
            category = "%{}%".format(category)
            articles = Articles.query.filter(Articles.category.like(category)).all()
            return render_template("articles.html",articles=articles)
        else:
             return render_template("articles.html",articles=articles)

    return render_template("articles.html",articles=articles)


@app.route('/articles/<int:id>', methods=['GET', 'POST'])
def article(id):
    article = Articles.query.get(id)
    articles_random = Articles.query.filter(Articles.id!=article.id).order_by(func.random()).limit(3).all()

    if request.method == 'POST':
        article.title = request.form.get('title')
        article.category = request.form.get('category')
        article.text = request.form.get('ckeditor')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/upload/" + pic_name)
            article.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("article", id=article.id))

    return render_template("article.html",article=article,articles_random=articles_random)


@app.route('/delete-article/<int:id>')
def delete_article(id):
    obj = Articles.query.filter_by(id=id).first()
    db.session.delete(obj)
    db.session.commit()
    flash("Запись удалена!", category="bad")
    return redirect('/articles')


@app.route('/routes', methods=['GET', 'POST'])
def routes():
    routes = Routes.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        point_a = request.form.get('point_a')
        point_b = request.form.get('point_b')
        text = request.form.get('ckeditor')
        image = request.files['image']
        filename = secure_filename(image.filename)
        pic_name = str(uuid.uuid4()) + "_" + filename
        image.save("static/img/upload/" + pic_name)
        routes = Routes(title=title,text=text,point_a=point_a,point_b=point_b,image_name=pic_name)
        db.session.add(routes)
        db.session.commit()
        flash("Запись добавлена!", category="ok")
        return redirect(url_for("routes"))

    if request.method == 'GET':
        point_a = request.args.get('point_a')
        point_b = request.args.get('point_b')
        if point_a or point_b:
            point_a = point_a.capitalize()
            point_b = point_b.capitalize()
            point_a = "%{}%".format(point_a)
            point_b = "%{}%".format(point_b)
            routes = Routes.query.filter(Routes.point_a.like(point_a) | Routes.point_b.like(point_b)).all()
            
            return render_template("routes.html",routes=routes)
        else:
             return render_template("routes.html",routes=routes)

    return render_template("routes.html",routes=routes)


@app.route('/routes/<int:id>', methods=['GET', 'POST'])
def route(id):
    route = Routes.query.get(id)
    if request.method == 'POST':
        route.title = request.form.get('title')
        route.text = request.form.get('ckeditor')
        route.point_a = request.form.get('point_a')
        route.point_b = request.form.get('point_b')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/upload/" + pic_name)
            route.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("route", id=route.id))
    return render_template("route.html",route=route)


@app.route('/delete-route/<int:id>')
def delete_route(id):
    obj = Routes.query.filter_by(id=id).first()
    db.session.delete(obj)
    db.session.commit()
    flash("Запись удалена!", category="bad")
    return redirect('/routes')


@app.route('/events', methods=['GET', 'POST'])
def events():
    events = Events.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        city = request.form.get('city')
        date = datetime.strptime(request.form['date'],'%Y-%m-%d')
        image = request.files['image']
        filename = secure_filename(image.filename)
        pic_name = str(uuid.uuid4()) + "_" + filename
        image.save("static/img/upload/" + pic_name)
        text = request.form.get('ckeditor')
        event = Events(title=title, city=city, date=date,text=text, image_name=pic_name)
        db.session.add(event)
        db.session.commit()
        flash("Запись добавлена!", category="ok")
        return redirect(url_for("events"))

    if request.method == 'GET':
        date = request.args.get('date')
        city = request.args.get('city')
        if date or city:
            date = date.capitalize()
            city = city.capitalize()
            date = "%{}%".format(date)
            city = "%{}%".format(city)
            events = Events.query.filter(Events.date.like(date) | Events.city.like(city)).all()
            return render_template("events.html",events=events)
        else:
             return render_template("events.html",events=events)
    return render_template("events.html",events=events)


@app.route('/events/<int:id>', methods=['GET', 'POST'])
def event(id):
    
    total_user = object
    fav = object
    id_list = []
    if 'name' in session:
        total_user = Users.query.filter_by(email=session['name']).first()
        fav = Favorites.query.filter_by(id_user=total_user.id).all()
        for ev in fav:
            id_list.append(ev.id_event)

    event = Events.query.get(id)
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.city = request.form.get('city')
        event.date = datetime.strptime(request.form['date'],'%Y-%m-%d')
        image = request.files['image']
        event.text = request.form.get('ckeditor')
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/upload/" + pic_name)
            event.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("event", id=event.id))
    return render_template("event.html",event=event,id_list=id_list)


@app.route('/delete-event/<int:id>')
def delete_event(id):
    obj = Events.query.filter_by(id=id).first()
    db.session.delete(obj)
    db.session.commit()
    flash("Запись удалена!", category="bad")
    return redirect('/events')


@app.route('/add-event-fav/<int:id>')
def add_event_fav(id):
    total_user = Users.query.filter_by(email=session['name']).first()
    total_event = Events.query.filter_by(id=id).first()
    fav = Favorites(id_user=total_user.id, id_event=total_event.id)
    db.session.add(fav)
    db.session.commit()
    flash("Добавлено в избранное!", category="ok")
    return redirect(url_for("event", id=total_event.id))


@app.route('/delete-event-fav/<int:id>')
def delete_event_fav(id):
    total_user = Users.query.filter_by(email=session['name']).first()
    total_event = Events.query.filter_by(id=id).first()
    fav = Favorites.query.filter_by(id_user=total_user.id,id_event=total_event.id).first()
    db.session.delete(fav)
    db.session.commit()
    flash("Удалено из избранного!", category="bad")
    return redirect(url_for("event", id=total_event.id))


@app.route('/map', methods=['GET', 'POST'])
def map():
    return render_template("map.html")


@app.route('/map/<int:id_region>', methods=['GET', 'POST'])
def region(id_region):
    region = Region.query.get(id_region)
    if request.method == 'POST':
        region.title = request.form.get('title')
        region.text = request.form.get('ckeditor')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/map/" + pic_name)
            region.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("region", id_region=region.id))
    return render_template("region.html",region=region)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'name' in session:
        abort(401)

    total_user = Users.query.filter_by(email=session['name']).first()
    fav = Favorites.query.filter_by(id_user=total_user.id).all()
    id_list = []
    events_list = []

    for event in fav:
        id_list.append(event.id_event)

    for el in id_list:
        events_list.append(Events.query.filter_by(id=el).first())
    
    return render_template("profile.html",events=events_list)


@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect('/')


@app.context_processor
def inject_user():
    def get_user_name():
        if 'name' in session:
            return Users.query.filter_by(email=session['name']).first()
    return dict(active_user=get_user_name())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidded(e):
    return render_template('403.html'), 403


@app.errorhandler(401)
def forbidded(e):
    return render_template('401.html'), 401


if __name__ == '__main__':
    app.run(debug=True)