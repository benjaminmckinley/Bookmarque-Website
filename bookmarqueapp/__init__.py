from flask import Flask
from flask import render_template # for file extends
from flask import redirect
from flask import request
from flask import url_for
from flask_mysqldb import MySQL #Mysql
from flask_login import LoginManager, current_user, login_user #Logins
from sassutils.wsgi import SassMiddleware # for sass/scss compilation
import smtplib, ssl, email
from email import encoders  # email import for sending emails
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import config as cfg # for loading in db configurations
from .models import User


app = Flask(__name__)
app.config['MYSQL_HOST'] = cfg.mysql["host"]
app.config['MYSQL_USER'] = cfg.mysql["user"]
app.config['MYSQL_PASSWORD'] = cfg.mysql["password"]
app.config['MYSQL_DB'] = cfg.mysql["db"]

#Login initialization
#Example secret key, probably should be changed.
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Email Initialization
try:
    gmail_server_user = cfg.email['user']
    gmail_server_password = cfg.email['password']
    #SMTP initialization and setups
    port = 465
    # Create a secure SSL context
    context = ssl.create_default_context()
    #Server connection
    server = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
    server.login(gmail_server_user, gmail_server_password)
except Exception as ex:
    print("Email couldn't start: " + str(ex))




mysql = MySQL(app)
# configure directory locations for Sass/SCSS
app.wsgi_app = SassMiddleware(app.wsgi_app, {
    'bookmarqueapp': ('static/sass', 'static/css', '/static/css')
})

@app.route('/mysqltest')
def test():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM book;''')
    rv = cursor.fetchall()
    print(rv)
    #cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
    mysql.connection.commit()
    return render_template('index.html')

@app.route('/')
def homepage():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM book, book_has_book_categories WHERE book.ISBN = book_has_book_categories.ISBN AND categoryID = '1' LIMIT 4;''')
    featured = cursor.fetchall()
    cursor.execute('''SELECT * FROM book, book_has_book_categories WHERE book.ISBN = book_has_book_categories.ISBN AND categoryID = '18' LIMIT 4;''')
    newly_released = cursor.fetchall()
    mysql.connection.commit()
    return render_template('index.html', featured=featured, newly_released=newly_released)

@app.route('/search/')
def search():
    return render_template('search_view.html')

@app.route('/view/<ISBN>')
def book_details(ISBN):
    print(str(ISBN))
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM book WHERE book.ISBN = ''' + str(ISBN)+ ''';''')
    fetch = cursor.fetchall()
    cursor.execute('''SELECT book_categories.categoryName FROM book_has_book_categories, book_categories WHERE book_has_book_categories.ISBN = ''' + str(ISBN)+ ''' AND book_has_book_categories.categoryID = book_categories.categoryID;''')
    tag_fetch = cursor.fetchall()
    mysql.connection.commit()
    return render_template('book_details_example.html', data=fetch[0],tags=list(tag_fetch))

@app.route('/admin')
def admin():
    return render_template('admin_view.html')

@app.route('/manage-books')
def manageBooks():
    return render_template('manage_books.html')


@app.route('/checkout1')
def checkout1():
    return render_template('checkout1.html')

@app.route('/checkout2')
def checkout2():
    return render_template('checkout2.html')

@app.route('/checkout3')
def checkout3():
    return render_template('checkout3.html')

@app.route('/checkout4')
def checkout4():
    return render_template('checkout4.html')

@app.route('/checkout5')
def checkout5():
    return render_template('checkout5.html')

@app.route('/checkout6')
def checkout6():
    return render_template('checkout6.html')

@app.route('/manage-books/book-entry')
def bookEntry():
    return render_template('book_entry.html')

@app.route('/cart')
def shopping_cart():
    return render_template('shopping_cart.html')

@app.route('/cart/history')
def order_history():
    return render_template('order_history.html')

@app.route('/profile', methods = ['POST', 'GET'])
def profile():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM users WHERE userID = '101';''')
    information = cursor.fetchall()
    cursor.execute('''SELECT addressStreet, addressCity, addressState, addressZip FROM users JOIN address ON users.addressID = address.addressID WHERE userID = "101";''')
    address = cursor.fetchall()
    cursor.execute('''SELECT userEmail FROM users WHERE userID = "101";''')
    email = cursor.fetchone()
    email = email[0]
    cursor.execute('''SELECT MIN(users_has_card.cardID), cardNumber, cardExpDate, cardType, cardSVC FROM users_has_card JOIN card ON card.cardID = users_has_card.cardID WHERE userEmail = %s;''', [email])
    card = cursor.fetchall()
    initCard = card[0]
    initial = information[0]
    initAdd = address[0]
    if request.method == 'POST':

        fName = request.form.get('fName')
        if (fName is None or fName == ""):
            fName = initial[2]

        lName = request.form.get('lName')
        if (lName is None or lName == ""):
            lName = initial[3]

        address = request.form.get('address')
        if (address is None or address == ""):
            address = initAdd[0]

        phone = request.form.get('phone')
        if (phone is None or phone == ""):
            phone = initial[7]

        city = request.form.get('city')
        if (city is None or city == ""):
            city = initAdd[1]

        state = request.form.get('state')
        if (state is None or state == ""):
            state = initAdd[2]

        zipCode = request.form.get('zip')
        if (zipCode is None or zipCode == ""):
            zipCode = initAdd[3]

        # handles update_password form
        password = request.form.get('password')
        if (password is None or password == ""):
            password = initial[6]
        passConfirm = request.form.get('passConfirm') # used to check if password is same in both fields
        submit = request.form.get('Save')
        if (submit is None):
            submit = "Cancel"
        if (submit == "Save" and password == passConfirm):
            cursor.execute('''UPDATE users SET userPassword = %s WHERE userID = "101";''', [password])
            #Send out email to user
            #Email Generation
            message = MIMEMultipart()
            message["From"] = gmail_server_user
            #For testing emails, I am sending emails to our email account, this should be changed to a variable which contains our user's email.
            test_email = "projdeploy@gmail.com"
            message["To"] = test_email
            message["Subject"] = "Your password has been changed"
            msgAlternative = MIMEMultipart('alternative')
            #Inline html, which could be replaced with larger template files if needed
            msgText = MIMEText("<h2>Your password has been changed. </h2> <p><br> Your password has been changed, as you asked. </p> <br> <p> If you didn’t ask to change your password, we’re here to help keep your account secure. Visit our support page for more info. </p>", 'html', 'utf-8')
            msgAlternative.attach(msgText)
            message.attach(msgAlternative)
            print("Send out an email here")
            text = message.as_string()
            print(text)
            server.sendmail(gmail_server_user, test_email, text)


        # handles update_card form and create_card form
        cardList = request.form.get('cardList')
        if (cardList is None or cardList == ""):
            cardList = initCard[3]

        cardNumber = request.form.get('cardNumber')
        if (cardNumber is None or cardNumber == ""):
            cardNumber = initCard[1]

        cID = initCard[0]
        monthList = request.form.get('monthList')
        if (monthList is None or monthList == ""):
            cursor.execute('''SELECT MONTH(cardExpDate) FROM card WHERE cardID = %s;''', [cID])
            monthList = cursor.fetchone()
            monthList = monthList[0]
            
        yearList = request.form.get('yearList')
        if (yearList is None or yearList == ""):
            cursor.execute('''SELECT YEAR(cardExpDate) FROM card WHERE cardID = %s;''', [cID])
            yearList = cursor.fetchone()
            yearList = yearList[0]

        dateConcat = str(yearList) + str(monthList) + "01" #converts year and month into datetime format
            
        SVC = request.form.get('SVC')
        if (SVC is None or SVC == ""):
            SVC = initCard[4]

        # confirm is for update card
        confirm = request.form.get("saveCard")
        print(confirm)
        if (confirm is None):
            confirm = "Cancel"
        if (confirm == "Save"):
            cursor.execute('''UPDATE card JOIN users_has_card ON card.cardID = users_has_card.cardID JOIN users ON users.userEmail = users_has_card.userEmail JOIN (SELECT MIN(cardID) AS min FROM users_has_card ) AS min ON min.min = users_has_card.cardID SET cardType = %s, cardNumber = %s, cardSVC = %s, cardExpDate = %s WHERE users_has_card.userEmail = %s;''', (cardList, cardNumber, [SVC], dateConcat, email))

        # ensures cards have unique ids
        cursor.execute('''SELECT MAX(cardID) FROM card;''');
        val = cursor.fetchone()
        cardValue = val[0]
        cardValue += 1

        cursor.execute('''SELECT COUNT(*) FROM users_has_card WHERE userEmail = %s;''', [email])
        maxCard = cursor.fetchone()
        maxCard = maxCard[0]

        #test is for create card
        test = request.form.get("createCard")
        if (test is None):
            test = "Exit"
        if (test == "Confirm" and maxCard <= 2):
            cursor.execute('''INSERT INTO card (cardID, cardNumber, cardType, cardSVC, cardExpDate) VALUES (%s, %s, %s, %s, %s);''', ([cardValue], cardNumber, cardList, SVC, dateConcat))
            cursor.execute('''INSERT INTO users_has_card (userEmail, cardID) VALUES (%s, %s);''', (email, [cardValue]))

        status = request.form.get('status')
        password = request.form.get('password')
        if (status is None and password is None): #not on update_password and status is unchecked
            status = "Deactive"
        else:
            status = initial[8]

        #ensures addresses have unique ids
        cursor.execute('''SELECT MAX(addressID) FROM address;''');
        value = cursor.fetchone()
        addressValue = value[0]
        addressValue += 1

        if (status == "Active"): # subscription for promos is checked
            cursor.execute('''UPDATE users SET userFName = %s, userLName = %s, userPhone = %s, userSubStatus = %s WHERE userID = "101";''', (fName, lName, phone, status))
        else: # subcription for promos is not checked
            cursor.execute('''UPDATE users SET userFName = %s, userLName = %s, userPhone = %s, userSubStatus = "Deactive" WHERE userID = "101";''', (fName, lName, phone))

        cursor.execute('''SELECT addressID FROM users WHERE userID = "101";''')
        checkValue = cursor.fetchone()
        check = checkValue[0]
        #print(check is None)
        if (password is None and check is None): # not on update_password form and there is no existing address associated
            print(addressValue)
            cursor.execute('''INSERT INTO address (addressID, addressStreet, addressCity, addressState, addressZip) VALUES (%s, %s, %s, %s, %s);''', ([addressValue], address, city, state, zipCode))
            cursor.execute('''UPDATE users SET addressID = %s WHERE userID = "101";''', [addressValue])
        else:
            cursor.execute('''UPDATE address JOIN users ON users.addressID = address.addressID SET addressStreet = %s, addressCity = %s, addressState = %s, addressZip = %s WHERE users.userID = "101";''', (address, city, state, zipCode))
        mysql.connection.commit()

    cursor.execute('''SELECT * FROM users WHERE userID = '101';''')
    information = cursor.fetchall()
    cursor.execute('''SELECT addressStreet, addressCity, addressState, addressZip FROM users JOIN address ON users.addressID = address.addressID WHERE userID = "101";''')
    address = cursor.fetchall()
    cursor.execute('''SELECT userEmail FROM users WHERE userID = "101";''')
    email = cursor.fetchone()
    email = email[0]
    cursor.execute('''SELECT MIN(users_has_card.cardID), cardNumber, cardExpDate, cardType, cardSVC FROM users_has_card JOIN card ON card.cardID = users_has_card.cardID WHERE userEmail = %s;''', [email])
    card = cursor.fetchall()
    mysql.connection.commit()
    return render_template('profile.html', details=information[0], add=address[0], card=card[0])
    #return render_template('profile.html')

@app.route('/profile/update-password')
def password_panel():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM users WHERE userID = '101';''')
    information = cursor.fetchall()
    cursor.execute('''SELECT addressStreet, addressCity, addressState, addressZip FROM users JOIN address ON users.addressID = address.addressID WHERE userID = "101";''')
    address = cursor.fetchall()
    cursor.execute('''SELECT userEmail FROM users WHERE userID = "101";''')
    email = cursor.fetchone()
    email = email[0]
    cursor.execute('''SELECT MIN(users_has_card.cardID), cardNumber, cardExpDate, cardType, cardSVC FROM users_has_card JOIN card ON card.cardID = users_has_card.cardID WHERE userEmail = %s;''', [email])
    card = cursor.fetchall()
    mysql.connection.commit()
    return render_template('update_password.html', details=information[0], add=address[0], card=card[0])

@app.route('/profile/update-card')
def card_panel():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM users WHERE userID = '101';''')
    information = cursor.fetchall()
    cursor.execute('''SELECT addressStreet, addressCity, addressState, addressZip FROM users JOIN address ON users.addressID = address.addressID WHERE userID = "101";''')
    address = cursor.fetchall()
    cursor.execute('''SELECT userEmail FROM users WHERE userID = "101";''')
    email = cursor.fetchone()
    email = email[0]
    cursor.execute('''SELECT MIN(users_has_card.cardID), cardNumber, cardExpDate, cardType, cardSVC FROM users_has_card JOIN card ON card.cardID = users_has_card.cardID WHERE userEmail = %s;''', [email])
    card = cursor.fetchall()
    mysql.connection.commit()
    return render_template('update_card.html', details=information[0], add=address[0], card=card[0])

@app.route('/profile/create-card')
def card_panel_2():
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM users WHERE userID = '101';''')
    information = cursor.fetchall()
    cursor.execute('''SELECT addressStreet, addressCity, addressState, addressZip FROM users JOIN address ON users.addressID = address.addressID WHERE userID = "101";''')
    address = cursor.fetchall()
    cursor.execute('''SELECT userEmail FROM users WHERE userID = "101";''')
    email = cursor.fetchone()
    email = email[0]
    cursor.execute('''SELECT MIN(users_has_card.cardID), cardNumber, cardExpDate, cardType, cardSVC FROM users_has_card JOIN card ON card.cardID = users_has_card.cardID WHERE userEmail = %s;''', [email])
    card = cursor.fetchall()
    mysql.connection.commit()
    return render_template('create_card.html', details=information[0], add=address[0], card=card[0])

@app.route('/profile/edit')
def edit_profile():
    return render_template('edit_profile.html')

# registration and login #
@app.route('/register', methods=['POST'])
def register_user():
    if request.method == 'POST':

        # get information from form
        # pull hidden input value for url which called '/register'
        next_url = request.form.get('next')

        # user information
        first_name = request.form.get('fName')
        last_name = request.form.get('lName')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check to see if email is taken

        #Add user to the database

        # Redirect to login

        # payment information
        # cardType, cardNumber, expMonth, expYear
        # address, city, state, zip

        # add user to the database
        # cursor = mysql.connection.cursor()
        # query = ''
        # cursor.execute(query)
        # cursor.commit()

        # send verification email

        # send.email()

        # if url exists redirect user to the page they were on
        if next_url:
            return redirect(next_url)

    return redirect('/') # if all else fails go to the homepage

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # PULL IN Email and password from login form here and insert into sql statement below.
        
        user_email = None
        cursor = mysql.connection.cursor()
        cursor.execute('''SELECT userID FROM users WHERE email = %s;''', (user_email))
        information = cursor.fetchall()
        print(information)
        mysql.connection.commit()
        user = load_user(user_id = information[0][0])
        # Use the user returned from load_user above to compare password from the form
        #if successful -> login
        #  if not user or !PASSWORD_COMPARISON:
        login_user(user)
        print('login')
    else:
        print('do not login')

    return redirect('/')

#This function shoud be called when a user is first logging in.
@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute('''SELECT * FROM users WHERE userID = %s;''', (user_id))
    information = cursor.fetchall()
    print(information)
    mysql.connection.commit()
    user = User(information[0][0], information[0][1], information[0][6], information[0][2], information[0][3])
    # SQL to return an instance of information pertaining to a user from DB
    return user;
