from flask import render_template, url_for, flash, redirect, request
from equigence import app, db, bcrypt
from equigence.forms import Register, Login, New
from equigence.models import User
from flask_login import login_user, logout_user, current_user, login_required
from flask import send_file
from equigence.plotting import plotchart, plotComparisonChart
import requests
from io import BytesIO



@app.route('/')
@app.route('/home')
def home():
    """Home page route."""
    return render_template('landing.html', title='Equigence')

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
            next_page = request.args.get('next')
            flash(f"Log in successful!", 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash(f"Log in failed! Please recheck email and password.", 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    """dashboard page route."""
    equities = db.db.Users.find_one({'id': current_user.id}).get('equities')
    return render_template('dashboard.html', data=equities, title='Dashboard')

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """new search route"""
    form = New()
    if current_user.is_authenticated:
        if form.validate_on_submit() and not form.compare.data:
            imageData = []
            symbol = form.symbol.data.upper()
            formMetric = form.metric.data
            apiFunction = None
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
                                f'Profit Margin Analysis for {symbol}')
                        imageData += [symbol, formMetric, current_user.id, netProfitMargin, 0]
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
                                f'Price to Earnings Analysis for {symbol}')
                        imageData += [symbol, formMetric, current_user.id, priceToEarnings, 0]
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
        elif form.validate_on_submit() and form.compare.data:
            #code for comparing multiple symbols
            if form.compare.data:
                symbols = form.compareStock.data.split(',')
            comparison_data = {}
            quartersList = [f'Q{i+1}' for i in range(0, int(form.compareSearchQtr.data))]
            for symbol in symbols:
                symbol = symbol.strip().upper()
                formMetric = form.compareMetric.data
                apiFunction = None
                data = None

                match formMetric:
                    case 'NPM':
                        apiFunction = 'INCOME_STATEMENT'
                        url = f'https://www.alphavantage.co/query?function={apiFunction}&symbol={symbol}&apikey=WOHIPQEJ4Z6LPM6F'
                        data = requests.get(url).json().get('quarterlyReports')
                        if data:
                            netincomeList = []
                            revenue = []
                            netProfitMargin = []
                            for i in range(0, int(form.compareSearchQtr.data)):
                                netincomeList.append(data[i].get('netIncome'))
                                revenue.append(data[i].get('totalRevenue'))
                            for i in range(0, int(form.compareSearchQtr.data)):
                                netProfitMargin.append(int(netincomeList[i]) / int(revenue[i]))
                            comparison_data[symbol] = netProfitMargin
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
                            marketSharePrice = int(overviewData.get('MarketCapitalization')) / outstandingShares
                            for i in range(0, int(form.compareSearchQtr.data)):
                                netincomeList.append(incomeData[i].get('netIncome'))
                            earningsPerShare = [int(i) / int(outstandingShares) for i in netincomeList]
                            priceToEarnings = [marketSharePrice / i for i in earningsPerShare]
                            comparison_data[symbol] = priceToEarnings
                        else:
                            flash(f"Data not found for {symbol}", 'danger')
                            return redirect(url_for('new'))

            # Plot the data
            plotedImage = plotComparisonChart(comparison_data, quartersList, 'bar',
                                                'Comparison of Equities', 
                                                f'Last {int(form.compareSearchQtr.data)} Quarters', 
                                                f'{form.compareMetric.data} Comparison Analysis For {form.compareStock.data.upper()}')
            imageData = [form.compareStock.data.upper(), form.compareMetric.data, current_user.id, comparison_data, 1]
            activeUser = db.db.Users.find_one({'id': current_user.id})
            comparedEquities = form.compareStock.data.upper()
            if 'equities' not in activeUser:
                activeUser['equities'] = {}
            if form.compareMetric.data not in activeUser['equities']:
                activeUser['equities'][comparedEquities] = {}
            if form.compareMetric.data not in activeUser['equities'][comparedEquities]:
                activeUser['equities'][comparedEquities][form.compareMetric.data] = {}
            activeUser['equities'][comparedEquities][form.compareMetric.data]['ComparisonPlot'] = plotedImage
            activeUser['equities'][comparedEquities][form.compareMetric.data]['ComparisonData'] = comparison_data
            db.db.Users.update_one({'id': current_user.id}, {'$set': {'equities': activeUser['equities']}})
            return render_template('displayplot.html', title='Comparison Report', data=imageData)    
                            
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

@app.route('/image/<symbol>/<metric>/<user_id>/<compare>')
def serve_image(symbol, metric, user_id, compare):
    user_doc = db.db.Users.find_one({'id': user_id})
    if compare == '0':
        if user_doc and 'equities' in user_doc and symbol in user_doc['equities']:
            if metric == 'NPM':
                image_data = user_doc['equities'][symbol][metric].get('ProfitMarginPlot')
            elif metric == 'PTE':
                image_data = user_doc['equities'][symbol][metric].get('PriceToEarningsPlot')

            if image_data:
                image_data = BytesIO(image_data)
                return send_file(image_data, mimetype='image/png')
    elif compare:
        if user_doc and 'equities' in user_doc and symbol in user_doc['equities']:
            image_data = user_doc['equities'][symbol][metric].get('ComparisonPlot')
            if image_data:
                image_data = BytesIO(image_data)
                return send_file(image_data, mimetype='image/png')
