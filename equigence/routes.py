from flask import render_template, url_for, flash, redirect, request
from equigence import app, db, bcrypt
from equigence.forms import Register, Login, New, Filter
from equigence.models import User, Equity, Image
from flask_login import login_user, logout_user, current_user, login_required
from flask import send_file
from equigence.plotting import plotchart
import requests
from io import BytesIO



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
            imageData = []
            symbol = form.symbol.data.upper()
            formMetric = form.metric.data
            apiFunction = None
            # urlSharePrice = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ohi&apikey=WOHIPQEJ4Z6LPM6F'
            # share = list(requests.get(urlSharePrice).json().get('Time Series (Daily)').values)[0]
            match formMetric:
                case 'NPM':
                    apiFunction = 'INCOME_STATEMENT'
                    url = f'https://www.alphavantage.co/query?function={apiFunction}&symbol={symbol}&apikey=WOHIPQEJ4Z6LPM6F'
                    data = requests.get(url).json().get('quarterlyReports')
                    if data:
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
                                f'Last {int(form.singleSearchQtr.data)} Quarters', 
                                'Profit Margin Analysis')
                        imageData += [symbol, formMetric, current_user.id, netProfitMargin]
                        activeUser = db.db.Users.find_one({'id': current_user.id})
                        if 'equities' not in activeUser:
                            activeUser['equities'] = {}
                        if symbol not in activeUser['equities']:
                            activeUser['equities'][symbol] = {}
                        if formMetric not in activeUser['equities'][symbol]:
                            activeUser['equities'][symbol][formMetric] = {}
                        activeUser['equities'][symbol][formMetric]['ProfitMarginPlot'] =  plotedImage
                        activeUser['equities'][symbol][formMetric]['ProfitMarginList'] = netProfitMargin
                        db.db.Users.update_one({'id': current_user.id}, {'$set': {'equities': activeUser['equities']}})
                        return render_template('displayplot.html', title='Analysis Report', data=imageData)
                    else:
                        flash(f"Data not found for {symbol}", 'danger')
                        return redirect(url_for('new'))
                case 'PTE':
                    apiFunction = 'OVERVIEW'
                    overviewUrl = f'https://www.alphavantage.co/query?function={apiFunction}&symbol={symbol}&apikey=WOHIPQEJ4Z6LPM6F'
                    netincomeUrl = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey=WOHIPQEJ4Z6LPM6F'
                    overviewData = requests.get(overviewUrl).json()
                    incomeData = requests.get(netincomeUrl).json().get('quarterlyReports')
                    outstandingShares = int(overviewData.get('SharesOutstanding'))
                    if overviewData and incomeData:
                        netincomeList = []
                        quartersList = [f'Q{i+1}' for i in range(0, int(form.singleSearchQtr.data))]
                        marketSharePrice = int(overviewData.get('MarketCapitalization')) / outstandingShares
                        for i in range(0, int(form.singleSearchQtr.data)):
                            netincomeList.append(incomeData[i].get('netIncome'))
                        earningsPerShare = [int(i) / int(outstandingShares) for i in netincomeList]
                        priceToEarnings = [marketSharePrice / i for i in earningsPerShare]
                        plotedImage = plotchart(priceToEarnings, quartersList, 'bar',
                                'Price to Earnings', 
                                f'Last {int(form.singleSearchQtr.data)} Quarters', 
                                'Price to Earnings Analysis')
                        imageData += [symbol, formMetric, current_user.id, priceToEarnings]
                        activeUser = db.db.Users.find_one({'id': current_user.id})
                        if 'equities' not in activeUser:
                            activeUser['equities'] = {}
                        if symbol not in activeUser['equities']:
                            activeUser['equities'][symbol] = {}
                        if formMetric not in activeUser['equities'][symbol]:
                            activeUser['equities'][symbol][formMetric] = {}
                        activeUser['equities'][symbol][formMetric]['PriceToEarningsPlot'] =  plotedImage
                        activeUser['equities'][symbol][formMetric]['PriceToEarningsList'] = priceToEarnings
                        db.db.Users.update_one({'id': current_user.id}, {'$set': {'equities': activeUser['equities']}})
                        return render_template('displayplot.html', title='Analysis Report', data=imageData)
                    else:
                        flash(f"Data not found for {symbol}", 'danger')
                        return redirect(url_for('new'))
            
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

@app.route('/image/<symbol>/<metric>/<user_id>')
def serve_image(symbol, metric, user_id):
    user_doc = db.db.Users.find_one({'id': user_id})
    
    if user_doc and 'equities' in user_doc and symbol in user_doc['equities']:
        if metric == 'NPM':
            image_data = user_doc['equities'][symbol][metric].get('ProfitMarginPlot')
        elif metric == 'PTE':
            image_data = user_doc['equities'][symbol][metric].get('PriceToEarningsPlot')

        if image_data:
            image_data = BytesIO(image_data)
            
            return send_file(image_data, mimetype='image/png')
    
    flash('Image not found', 'danger')
    return redirect(url_for('new'))
