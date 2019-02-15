from flask import Flask, render_template, flash, request, url_for, redirect, session, send_file, send_from_directory, jsonify
import sys
from . import content_management
from . import dbconnect
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from passlib.hash import sha256_crypt
from pymysql import escape_string as thwart
import gc
from functools import wraps
import smtplib
from flask_mail import Mail,Message
import os
import pygal
########################To learn clear about wrapper function in python#####################################
###go to link : https://www.saltycrane.com/blog/2008/01/how-to-use-args-and-kwargs-in-python/  ###


TOPIC_DICT = content_management.Content()

app = Flask(__name__, instance_path = '/var/www/FlaskApp/FlaskApp/protected')

app.config.update(
    DEBUG=True,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=' beginnercoder007@gmail.com',
    MAIL_PASSWORD='asdfgflkjhj12345678900'
    )

mail=Mail(app)

app.config['SECRET_KEY'] = '123456'

@app.route('/')
@app.route('/<path:urlpath>/')
def homepage(urlpath='/'):

	return render_template("main.html")

@app.route('/converters/')
@app.route('/converters/<string:thread>/<int:page>')
def converterexample(thread='test',page=1):
    try:
        gc.collect()
        return render_template("converterexample.html",thread=thread, page=page)
    except Exception as e:
        return(str(e))
        

@app.route('/jinjaman/')
def jinjaman():
    try:
        gc.collect()
        data = [15,'15','Python is good','Python, Java, php, SQL, C++','<p><strong>Hey there!</strong></p>']
        return render_template("jinja-templating.html", data = data)
    except Exception as e:
        return(str(e))

@app.route('/include_example/')
def include_example():
	try:
		replies = {'Jack':'Cool post',
					'Jane':'+1',
					'Erika':'Most definitely',
					'Bob':'wow',
					'Carl':'amazing!'}
		return render_template("include_tutorial.html", replies = replies)
	except Exception as e:
		return(str(e))

@app.route('/dashboard/')
def dashboard():

	return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)

def login_required(f):
	@wraps(f)
	def wrap(*args,**kwargs):
        #*args is infinite number of arguments which act like a variable not a list like structure and can't access with index#
        #**kwargs is infinite number of arguments which act like a list like structure and the values can be accessed using index#
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash("You need to login first")
			return redirect(url_for('login_page'))
	return wrap

@app.route("/logout/")
@login_required
def logout():
	session.clear()
	flash("You have been logged out!")
	gc.collect()
	return redirect(url_for('homepage'))

@app.route('/login/', methods = ['GET','POST'])
def login_page():

	error = ''
	try:

		c, conn = dbconnect.connection()
		if request.method == "POST":

			data = c.execute("SELECT * FROM users WHERE username = (%s)", thwart(request.form['username']))
			data = c.fetchone()[2]

			if sha256_crypt.verify(request.form['password'],data):
				session['logged_in'] = True
				session['username'] = request.form['username']
				flash("You are now logged in")
				return redirect(url_for("dashboard"))
		
			else:
				error = "Invalid credentials, try again"

		gc.collect()

		return render_template("login.html",error = error)

	except Exception as e:

		#flash(e)
		error = "Invalid credentials, try again."
		return render_template("login.html",error = error)

@app.route('/send-mail/')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
            sender="beginnercoder007@gmail.com",
            recipients=["maranacoder007@gmail.com"])
        msg.body = "Yo!\nHave you heard the good word of Python????"
        mail.send(msg)
        return 'Mail sent'
    except Exception as e:
        return str(e)

##########Example for forgot password############
#msg = Message("Forgot Password - PythonProgramming.net",
#   sender = "pythonprogrammingnet@gmail.com",
#   recipients = [email_addr])
#msg.body='Hello '+username+',\nYou or someone else has requested that a new password be generated for your account.'
#msg.html = render_template('/mails/reset-password.html',username = username, link = link)
#mail.send(msg)
##########reset-password.html###########
#<p>Hello {{username}},</p>
#<p>You or someone else has requested that a new password be generated for you account.  If you made this request,  then please click this link:  <a href={{link}}><strong>reset password</strong></a>.</p>

@app.route('/return-file/')
def return_file():
    return send_file('/var/www/FlaskApp/FlaskApp/static/dept.csv',attachment_filename = 'dept.csv')

def special_requirement(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        try:
            if 'admin' == session['username']:
                return f(*args,**kwargs)
            else:
                return redirect(url_for('dashboard')), flash("You must be an admin to continue")
        except Exception as e:
            return redirect(url_for('dashboard')), flash(str(e))
    return wrap

@app.route('/secret/<path:filename>')
@special_requirement
def protected(filename='abcd.png'):
    try:
        return send_from_directory(os.path.join(app.instance_path,''),filename)
    except Exception as e:
        return redirect(url_for('homepage'))

@app.route('/interactive/')
def interactive():
    try:
        return render_template("interactive.html")
    except Exception as e:
        return(str(e))

@app.route('/background_process')
def background_process():
    try:
        lang = request.args.get('proglang')
        if str(lang).lower() == 'python':
            return jsonify(result = 'You are wise!')
        else:
            return jsonify(result = 'Try again')
    except Exception as e:
        return(str(e))

@app.route('/pygalexample/')
def pygalexample():
    try:
        graph = pygal.Line()
        graph.title = '% Change Coolness of programming languages over time.'
        graph.x_labels = ['2011','2012','2013','2014','2015','2016']
        graph.add('Python', [15,31,89,200,356,900])
        graph.add('Java', [15,45,76,80,91,95])
        graph.add('C++', [5,51,54,102,150,201])
        graph.add('All other combined!', [5,15,21,55,92,105])
        graph_data = graph.render_data_uri()
        return render_template("graphing.html",graph_data = graph_data)
    except Exception as e:
        return(str(e))

@app.route('/paypalexample/')
def paypal():
    return render_template("paypal.html")

@app.route('/paypaldownload/')
def paypaldown():
    return send_file('/var/www/FlaskApp/FlaskApp/static/videos/paypal.mp4',attachment_filename = 'paypal.mp4')

@app.route('/ssldownload/')
def ssldown():
    return send_file('/var/www/FlaskApp/FlaskApp/static/videos/SSL_for_HTTPS.mp4',attachment_filename = 'SSL_for_HTTPS.mp4')



@app.errorhandler(404)
def page_not_found(e):

	return render_template("404.html")

##@app.route('/slashboard/')
#def slashboard():
#	try:
#		return render_template("dashboard.html",TOPIC_DICT = topics)
#	except Exception as e:
#		return render_template("500.html",error=e)

class RegistrationForm(Form):

	username = TextField('Username',[validators.Length(min = 4, max = 20)])
	email = TextField('Email Address',[validators.Length(min = 6, max = 50)])
	password = PasswordField('Password',[validators.Required(),validators.EqualTo('confirm',message = "Passwords must match.")])
	confirm = PasswordField('Repeat Password')
	accept_tos = BooleanField('I accept to the <a href="/tos">Terms of Service</a> and the <a href="/privacy/">Privacy Notice</a>', [validators.Required()])

@app.route('/register/', methods = ['GET','POST'])
def register_page():

	try:
		form = RegistrationForm(request.form)

		if request.method == "POST" and form.validate():
			username = form.username.data
			email = form.email.data
			password = sha256_crypt.encrypt((str(form.password.data)))
			c, conn = dbconnect.connection()
			x = c.execute("SELECT * FROM users WHERE username = (%s)",(thwart(username)))

			if int(x) > 0:
				flash("That username is already taken, please choose another")
				return render_template('register.html',form = form)

			else:
				c.execute("INSERT INTO users(username, password,email,tracking) VALUES(%s,%s,%s,%s)",(thwart(username),thwart(password),thwart(email),thwart("/introduction-to-python-programming")))
				conn.commit()
				flash("Thanks for registering!")
				c.close()
				conn.close()
				gc.collect()
				session['logged_in'] = True
				session['username'] = username
				return redirect(url_for('dashboard'))

		return render_template("register.html", form = form)
	except Exception as e:
		return(str(e))


if __name__ == "__main__":
	app.run()
