import os
import secrets
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask_restful import Api
from markupsafe import escape
from dbms import DB, User, SensorData
from forms import RegistrationForm, LoginForm, AccountForm, PostForm, ResetForm1, ResetForm2, SellForm, BuyorSellForm
from flask_login import login_user, LoginManager, logout_user, current_user, login_required
from grapher import create_plot, create_heatmap

db = DB('site.db')

app = Flask(__name__)

app.config['SECRET_KEY'] = 'adminek'

api = Api(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(username):
    user = User(username)
    return user


api.add_resource(SensorData, '/update/<string:username>')


@app.route('/home')
@login_required
def home():
    bar = create_plot()
    heatmap = create_heatmap()
    return render_template('home.html', sensors=db.get_sensor(), title='Home', plot=bar, heatmap=heatmap,
                           alerts=db.get_sensor())


@app.route('/')
@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/news')
@login_required
def news_page():
    heatmap = create_heatmap()

    return render_template('news.html', heatmap=heatmap, alerts=db.get_sensor())


@app.route('/buyandsell', methods=['GET', 'POST'])
@login_required
def buyandsell_page():
    heatmap = create_heatmap()

    form = BuyorSellForm()
    if form.validate_on_submit():
        print('here')
        print(form.buyorsell.data)
        if form.buyorsell.data == 'buying':
            return redirect(url_for('buy_page'))
        elif form.buyorsell.data == 'selling':
            return redirect(url_for('sell_page'))
        else:
            flash('Choose one of the Options!', category='danger')
            return redirect(url_for('buyandsell_page'))

    return render_template('buyandsell.html', title='Buy & Sell', heatmap=heatmap, form=form, alerts=db.get_sensor())


@app.route('/buy')
@login_required
def buy_page():
    heatmap = create_heatmap()

    return render_template('buy.html', title='Buy', heatmap=heatmap, buy_listings=db.get_listings_all(),
                           alerts=db.get_sensor())


@app.route('/buy/<product_id>')
@login_required
def buy_individual_page(product_id):
    heatmap = create_heatmap()

    if db.check_product_id(product_id):
        return render_template('buy_individual.html', heatmap=heatmap, listing=db.get_listing(product_id),
                               alerts=db.get_sensor())

    else:
        flash('Sorry! The Product does not exist', category='danger')
        return redirect(url_for('buy_page'))


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell_page():
    heatmap = create_heatmap()
    form = SellForm()
    if form.validate_on_submit():
        if form.image.data:
            random_hex = secrets.token_hex(8)
            _, p_ext = os.path.splitext(form.image.data.filename)
            p_fn = random_hex + p_ext
            image_path = os.path.join(app.root_path, 'static/bs_images', p_fn)
            form.image.data.save(image_path)

            dt = datetime.now()

            if db.add_listing(db.get_id(current_user.username), dt.strftime("%H:%M:%S"), dt.strftime("%m/%d/%y"),
                              form.name.data, float(form.price.data), form.units.data, form.info.data, p_fn,
                              form.location.data, 'TRUE' if form.verified.data else 'FALSE', 'TRUE' if form.negotiable.data else 'FALSE'):
                flash(f'Your Listing has been Successfully Posted!', category='success')
                return redirect(url_for('home'))
            else:
                flash('Sorry, Please Try Again Later', category='danger')
                return redirect(url_for('sell_page'))
    return render_template('sell.html', title='Sell', form=form, heatmap=heatmap, alerts=db.get_sensor())


@app.route('/thankyou')
def thankyou_page():
    heatmap = create_heatmap()

    return render_template('thankyou.html', heatmap=heatmap, alerts=db.get_sensor())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.add_user(form.username.data, form.email.data, form.password.data):
            flash(f'Account Created for {form.username.data}, You will now be able to login!', category='success')
            return redirect(url_for('login'))
        else:
            flash('Sorry, Account already exists!', category='danger')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form, alerts=db.get_dummy_data())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        if db.check_login(form.username.data, form.password.data):
            user = User(form.username.data)
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in!', 'success')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form, alerts=db.get_dummy_data())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('about_page'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    heatmap = create_heatmap()

    img = url_for('static', filename='profile_pics/' + current_user.image)
    form = AccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            random_hex = secrets.token_hex(8)
            _, p_ext = os.path.splitext(form.picture.data.filename)
            p_fn = random_hex + p_ext
            picture_path = os.path.join(app.root_path, 'static/profile_pics', p_fn)
            form.picture.data.save(picture_path)
            db.update_picture(p_fn, current_user.username)
            current_user.image = p_fn
            flash('Picture Successfully Updated', 'success')
            return redirect(url_for('account'))
    return render_template('account.html', title='Account', form=form, image_file=img, heatmap=heatmap,
                           alerts=db.get_sensor())


# @app.route('/reset-password-username')
# def reset_password_username():
#     form = ResetForm1()
#     if form.validate_on_submit():
#         user = User(form.username.data)
#         token = user.reset_pass()
#         send_email(token)
#         flash('An email has been sent with instructions to reset your password.', 'info')
#         return redirect(url_for('login'))
#
#     return render_template('reset_password_username.html')
#
#
# @app.route('/reset-password/<token>')
# def reset_password(token):
#     user_id =
#     form = ResetForm2()


# if __name__ == '__main__':
#     app.run(debug=True)
