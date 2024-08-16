from flask import render_template, url_for, flash, redirect, request
from equigence import app, db, bcrypt
from equigence.forms import Register, Login, New, Filter
from equigence.models import User, Equity, Image
from flask_login import login_user, logout_user, current_user, login_required
from flask import send_file
from equigence.plotting import plotchart
import requests


@app.route('/')
@app.route('/home')
def home():
    """Home page route."""
    return render_template('landing.html')

@app.route('/listings', methods=['GET', 'POST'])
def listings():
    """listings page route."""
    form = Filter()
    page = request.args.get('page', 1, type=int)
    query = Accomodation.query
    if form.validate_on_submit():

        if form.state.data != '':
            query = query.filter_by(state=form.state.data)
        if form.city.data != '':
            query = query.filter_by(city=form.city.data)
        if form.type.data != '':
            query = query.filter_by(house_type=form.type.data)
        rents = query.order_by(Accomodation.created_at.desc()).paginate(page=page, per_page=6)
        return render_template('listing.html', rents=rents, title='Listings', form=form)
    rents = Accomodation.query.order_by(Accomodation.created_at.desc()).paginate(page=page, per_page=6)
    return render_template('listing.html', rents=rents, title='Listings', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page route."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = Register()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        newUser = User()
        user = {"firstname": form.firstname.data,
                    'lastname': form.lastname.data,
                    'email': form.email.data,
                    'password': hashed_password,
                    'id': newUser.id,
                    'equities': {}}
        db.db.Users.insert_one(user)
        flash(f"Account created successfully! Please log in.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page route."""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = Login()
    if form.validate_on_submit():
        existing_user = db.db.Users.find_one({'email': form.email.data})
        if existing_user and bcrypt.check_password_hash(existing_user.get('password'),
                                                        form.password.data):
            user = User(firstname=existing_user['firstname'],
                        lastname=existing_user['lastname'],
                        email=existing_user['email'], 
                        password=existing_user['password'],
                        id=existing_user['id'],)
            login_user(user, form.remember.data)
            # print(current_user.__dict__) # This is to check the current user object
            next_page = request.args.get('next')
            flash(f"Log in successful!", 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash(f"Log in failed! Please recheck email and password.", 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """new search route"""
    form = New()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            symbol = form.symbol.data
            formMetric = form.metric.data
            apiFunction = None
            # urlSharePrice = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ohi&apikey=WOHIPQEJ4Z6LPM6F'
            # share = list(requests.get(urlSharePrice).json().get('Time Series (Daily)').values)[0]
            match formMetric:
                case 'N/M':
                    apiFunction = 'INCOME_STATEMENT'
                    url = f'https://www.alphavantage.co/query?function={apiFunction}&symbol={symbol}&apikey=WOHIPQEJ4Z6LPM6F'
                    data = requests.get(url).json().get('quarterlyReports')
                    netincomeList = []
                    revenue = []
                    netProfitMargin = []
                    quartersList = [f'Q{i+1}' for i in range(0, int(form.singleSearchQtr.data))]
                    for i in range(0, int(form.singleSearchQtr.data)):
                        netincomeList.append(data[i].get('netIncome'))
                        revenue.append(data[i].get('totalRevenue'))
                    for i in range(0, int(form.singleSearchQtr.data)):
                        netProfitMargin.append(int(netincomeList[i]) / int(revenue[i]))
                    plotedImage = plotchart(netProfitMargin, quartersList, 'bar',
                               'Net Profit Margin', 
                               'Quarters', 
                               'Profit Margin Analysis')
                    activeUser = db.db.Users.find_one({'id': current_user.id})
                    activeUser['equities'][symbol] = {'ProfitMarginPlot': plotedImage}
                    
                        
                case 'P/E':
                    api
            
            url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey=WOHIPQEJ4Z6LPM6F'
            r = requests.get(url)
            data = r.json().get('quarterlyReports')
            

            try:
                for image in form.image.data:
                    img = Image(data=image.read(), accomodation_id=accomodation.id)
                    db.session.add(img)
                    db.session.commit()
                flash(f"Rent added successfully!", 'success')
                return redirect(url_for('listings'))
            except Exception:
                flash(f"Rent added successfully!", 'success')
                return redirect(url_for('listings'))
    else:
        flash(f"Please log in to add a new rent.", 'danger')
        return redirect(url_for('login'))
    return render_template('new.html', title='New Search', form=form)

@app.route('/contact')
def contact():
    """Contact page route."""
    return render_template('contact.html', title='Contact Us')

@app.route('/logout')
def logout():
    """Logout route."""
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    """dashboard page route."""
    return render_template('dashboard.html', title='Dashboard')

@app.route('/accomodation/<accomodation_id>')
def accomodation(accomodation_id):
    """accomodation page route."""
    rent = Accomodation.query.get_or_404(accomodation_id)
    pictures = Image.query.filter_by(accomodation_id=accomodation_id).all()
    return render_template('accomodation.html', title='Accomodation', rent=rent, pictures=pictures)

@app.route('/image/<image_id>')
def serve_image(image_id):
    image = Image.query.get(image_id)
    return send_file(BytesIO(image.data), mimetype='image/jpeg')
