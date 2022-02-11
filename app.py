from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import date, datetime, timedelta
from calendar import monthrange
import calendar
import pyrebase



app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
Bootstrap(app)


firebaseConfig={'apiKey': "AIzaSyB1qb-HB2nBrefQaQm_lmD7uFDsrTYPctk",
   'authDomain': "data-d3cca.firebaseapp.com",
    'databaseURL': "https://data-d3cca.firebaseio.com",
    'projectId': "data-d3cca",
    'storageBucket': "data-d3cca.appspot.com",
    'messagingSenderId': "1016417085751",
    'appId': "1:1016417085751:web:7fd29bd369e12f9661d2b2" }	

firebase=pyrebase.initialize_app(firebaseConfig)

db=firebase.database()


#Login and logout-------------

current_user_isloggedin = False
current_user_isAdmin = False
current_user_email = None
current_user_userid = None

def login_user(user, usrid, admin):
	global current_user_isloggedin
	global current_user_email
	global current_user_userid
	global current_user_isAdmin

	current_user_isloggedin = True
	current_user_email = user
	current_user_userid = usrid
	current_user_isAdmin = admin

def logout_user():
	global current_user_isloggedin
	global current_user_email
	global current_user_userid
	global current_user_isAdmin

	current_user_isloggedin = False
	current_user_email = None
	current_user_userid = None
	current_user_isAdmin = False
	

#-----------------------------------
#-------------Validacijos-----------




def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')

def findDay(date): 
    year, month, day = (int(i) for i in date.split('-'))     
    dayNumber = calendar.weekday(year, month, day) 
    days =["Monday", "Tuesday", "Wednesday", "Thursday", 
                         "Friday", "Saturday", "Sunday"] 
    return (days[dayNumber]) 





#routes

@app.route('/')
def index():
	return render_template('index.html')



@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/login', methods = ['POST'])
def loginPOST():

	enteredusr = request.form.get('username')
	enteredpsw = request.form.get('password')
	id = 0


	#Praeina per visus userius ir randa ar bent vieno username atitinka su ivestu, jei taip jo id issaugo
	all_users2 = db.child("Employees").get()
	all_users1 = all_users2.val()

	for user in all_users1[1:]:
		if user.get("email")==enteredusr:
			id = user.get("id")

	#Is DB istraukia info pagal userio id kuri rado anksciau
	if id>0:
		dbactive1 = db.child("Employees").child(id).child("active").get()
		dbactive=dbactive1.val()

		if dbactive == True:
			dbusr1 = db.child("Employees").child(id).child("email").get()
			dbusr=dbusr1.val()
			dbpsw1 = db.child("Employees").child(id).child("password").get()
			dbpsw=dbpsw1.val()
			dbadmin1 = db.child("Employees").child(id).child("isadmin").get()
			dbadmin=dbadmin1.val()

			#Istraukta usr/psw lygina ir jei viskas ok prilogina
			if check_password_hash(dbpsw, enteredpsw):
				login_user(dbusr, id, dbadmin)
				return redirect(url_for('dashboard'))
			else:
				flash('Invalid password', 'danger')
		else:
			flash('Your account is not activated', 'danger')
	else:
			flash('Invalid username', 'danger')



	return redirect(url_for('login'))







@app.route('/dashboard')
def dashboard():
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin

	if loggedin:
		
		return render_template('dashboard.html', name=current_user_email)
		
	else:
		return redirect(url_for('login'))

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))












@app.route('/createemployee')
def signup():
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin

	if loggedin:
		if isadmin:
			return render_template('signup.html')
		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))


@app.route('/createemployee', methods=['GET', 'POST'])
def signupPOST():

	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		if isadmin:
			admin1 = request.form.get('admin')
			active1 = request.form.get('active')
			types = request.form.get('types')
			fname = request.form.get('fname')
			lname = request.form.get('lname')
			email = request.form.get('email')
			password = request.form.get('password')

			SpecialSym =['$', '@', '#', '%', '!'] 
			SpecialSym2 =['@'] 
			val = True
			reason = None
			
			

			if not any(char in SpecialSym for char in password): 
				reason = 'Password should have at least one of the symbols $@#!'
				val = False
			if not any(char.islower() for char in password): 
				reason = 'Password should have at least one lowercase letter'
				val = False	
			if not any(char.isupper() for char in password): 
				reason = 'Password should have at least one uppercase letter'
				val = False		
			if not any(char.isdigit() for char in password): 
				reason = 'Password should have at least one numeral'
				val = False
			if len(password) > 20: 
				reason = 'Password length should be not be greater than 8'
				val = False
			if len(password) < 6: 
				reason = 'Password length should be at least 6'
				val = False
			if not any(char in SpecialSym2 for char in email): 
				reason = ' "@" symbol is required in the email'
				val = False
			if len(email) < 1: 
				reason = 'Email field cannot be empty'
				val = False
			if len(lname) < 1: 
				reason = 'Last name field cannot be empty'
				val = False
			if len(fname) < 1: 
				reason = 'First name field cannot be empty'
				val = False

			a=1
			all_users1 = db.child("Employees").get()
			for user in all_users1.each():
				username = db.child("Employees").child(a).child("email").get()
				if username.val()==email:
					reason = 'This email is already in use'
					val = False
				a=a+1



			if (val==True):

				admin = False
				active = False
				
				if admin1 == 'on':
					admin = True

				if active1 == 'on':
					active = True



				# Gaunam last id ir new id
				all_employees1 = db.child("Employees").get()
				all_employees = all_employees1.val()
				id = all_employees[-1].get('id') + 1

				hashed_password = generate_password_hash(password, method='sha256')
				data={'fname':fname, 'lname':lname, 'id':id, 'email':email, 'password':hashed_password, 'type':types, 'isadmin':admin, 'active':active}
				db.child("Employees").child(id).set(data) # Papushina duomenis su nustatytu id

				flash('New user has been created','success')
				return render_template('signup.html')

			else:
				flash(reason, 'danger')
				return render_template('signup.html')

		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))














@app.route('/updateemployee')
def updateemployee():

	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		if isadmin:
			rows1 = db.child("Employees").get()
			rows = rows1.val()
			return render_template('updateemployee.html', title='Overview', rows=rows, admin=True)
		else:
			data1 = db.child("Employees").child(current_user_userid).get()
			data = data1.val()
			rows = []
			rows.append(None)
			rows.append(data)
			return render_template('updateemployee.html', title='Overview', rows=rows, admin=False)
	else:
		return redirect(url_for('login'))


@app.route('/updateemployeeredirect/<id>')
def updateemployeeredirect(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		if isadmin:
			data1 = db.child("Employees").child(id).get()
			data = data1.val()
			return render_template('updateemployeeid.html', id=id, data=data)
		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))




@app.route('/updateemployeePOST/<id>', methods = ['GET', 'POST'])
def updateemployeePOST(id):

	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		if isadmin:

			fname=request.form.get('fname')
			lname=request.form.get('lname')
			password=request.form.get('password')
			types=request.form.get('types')
			admin1=request.form.get('admin')

			admin = False		
			if admin1 == 'on':
				admin = True

			db.child("Employees").child(id).update({'fname':fname, 'lname':lname, 'isadmin':admin, 'type':types})


			if password!="":

				SpecialSym =['$', '@', '#', '%', '!'] 
				val = True
				reason = None

				if not any(char in SpecialSym for char in password): 
					reason = 'Password should have at least one of the symbols $@#!'
					val = False
				if not any(char.islower() for char in password): 
					reason = 'Password should have at least one lowercase letter'
					val = False	
				if not any(char.isupper() for char in password): 
					reason = 'Password should have at least one uppercase letter'
					val = False		
				if not any(char.isdigit() for char in password): 
					reason = 'Password should have at least one numeral'
					val = False
				if len(password) > 20: 
					reason = 'Password length should be not be greater than 8'
					val = False
				if len(password) < 6: 
					reason = 'Password length should be at least 6'
					val = False

				if (val==True):
					hashed_password = generate_password_hash(password, method='sha256')
					db.child("Employees").child(id).update({'password':hashed_password})
				else:
					flash(reason, 'danger')
					data1 = db.child("Employees").child(id).get()
					data = data1.val()
					return render_template('updateemployeeid.html', id=id, data=data)

			flash('Data has been updated','success')

			return redirect(url_for('updateemployee'))

		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))



@app.route('/deactivateemployeePOST/<id>', methods = ['GET', 'POST'])
def deactivateemployeePOST(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		if isadmin:

			db.child("Employees").child(id).update({'active':False})
			return redirect(url_for('updateemployee'))

		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))


@app.route('/activateemployeePOST/<id>', methods = ['GET', 'POST'])
def activateemployeePOST(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		if isadmin:

			db.child("Employees").child(id).update({'active':True})
			return redirect(url_for('updateemployee'))

		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))












@app.route('/insertschedule')
def insertschedule():
	loggedin = current_user_isloggedin

	if loggedin:
		return render_template('insertschedule.html')
	else:
		return redirect(url_for('login'))
	


@app.route('/insertschedule', methods = ['POST'])
def insertschedulePOST():
	loggedin = current_user_isloggedin

	if loggedin:
		year = int(request.form.get('year'))
		month = int(request.form.get('month'))
		time = request.form.get('time')

		type1 = db.child("Employees").child(current_user_userid).child("type").get()
		type2 = type1.val()

		fname1 = db.child("Employees").child(current_user_userid).child("fname").get()
		fname2 = fname1.val()

		lname1 = db.child("Employees").child(current_user_userid).child("lname").get()
		lname2 = lname1.val()

		fullname = fname2 + " " + lname2

		# Gaunam last id
		
		all_schedules1 = db.child("Schedules").get()
		all_schedules = all_schedules1.val()
		new_id = all_schedules[-1].get('id') + 1


		# Patikrinimas ar niekas nepasiemes to shifto ir ar tu nesi pasirinkes jau tam menesiui
		val1 = True
		val2 = True
		val3 = True
		reason1 = None
		reason2 = None
		reason3 = None

		for schedule in all_schedules[1:]:
			if schedule != None:
				existing_uid = schedule.get('uid')
				existing_type = schedule.get('type')
				existing_year = schedule.get('year')
				existing_month = schedule.get('month')
				existing_shift = schedule.get('shift')

				if current_user_userid==existing_uid and year==existing_year and month==existing_month:
					val1 = False
					reason1 = "You already have a shift selected for this month"

				if year==existing_year and month==existing_month and time==existing_shift and type2==existing_type:
					val2 = False
					reason2 = "This shift is already selected by another specialist"


		currentMonth = datetime.now().month
		currentYear = datetime.now().year

		if int(year)<int(currentYear) or (int(year) == int(currentYear) and int(month) <= int(currentMonth)):
			val3 = False
			reason3 = "You cannot set a shift to the past"



		if val1 == True and val2 == True and val3 == True:
			data={'id':new_id, 'uid':current_user_userid, 'year':year, 'month':month, 'shift':time, 'type':type2, 'name':fullname}
			db.child("Schedules").child(new_id).set(data)


			flash('New schedule has been inserted','success')
			return render_template('insertschedule.html')

		else:
			if val1 == False:
				flash(reason1, 'danger')
			if val2 == False:
				flash(reason2, 'danger')
			if val3 == False:
				flash(reason3, 'danger')
			return render_template('insertschedule.html')
			

	else:
		return redirect(url_for('login'))



@app.route('/updateschedule')
def updateschedule():

	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin
	
	if loggedin:
		rows1 = db.child("Schedules").get()
		rows2 = rows1.val()

		futureMonth = []

		currentYear = int(datetime.now().year)
		currentMonth = int(datetime.now().month)
		

		if isadmin:
			rows = []
			rows.append(None)
			futureMonth.append(True)
			for row in rows2[1:]:
				if row != None:
					rows.append(row)
					dbyear = int(row.get('year'))
					dbmonth = int(row.get('month'))

					if dbyear > currentYear or (dbyear == currentYear and dbmonth > currentMonth):
						futureMonth.append(True)
					else:
						futureMonth.append(False)
			return render_template('updateschedule.html', title='Overview', rows=rows, isadmin=isadmin, futureMonth=futureMonth)
		else:	
			rows = []
			rows.append(None)
			futureMonth.append(True)
			for row in rows2[1:]:
				if row != None:
					existing_uid = row.get('uid')
					if existing_uid == current_user_userid:
						rows.append(row)
						dbyear = int(row.get('year'))
						dbmonth = int(row.get('month'))
						if dbyear > currentYear or (dbyear == currentYear and dbmonth > currentMonth):
							futureMonth.append(True)
						else:
							futureMonth.append(False)


			return render_template('updateschedule.html', title='Overview', rows=rows, isadmin=isadmin, futureMonth=futureMonth)
	else:
		return redirect(url_for('login'))

@app.route('/updatescheduleredirect/<id>')
def updatescheduleredirect(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin
	allowed = False

	if loggedin:
		uid1 = db.child("Schedules").child(id).child("uid").get()
		uid = uid1.val()
		if uid == current_user_userid:
			allowed = True
		if isadmin:
			allowed = True

		if allowed:
			data1 = db.child("Schedules").child(id).get()
			data = data1.val()
			return render_template('updatescheduleid.html', id=id, data=data)
		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))


@app.route('/updateschedulePOST/<id>', methods = ['GET', 'POST'])
def updateschedulePOST(id):

	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin
	allowed = False

	if loggedin:
		uid1 = db.child("Schedules").child(id).child("uid").get()
		uid = uid1.val()
		if uid == current_user_userid:
			allowed = True
		if isadmin:
			allowed = True

		if allowed:
			year1 = db.child("Schedules").child(id).child("year").get()
			year = year1.val()
			month1 = db.child("Schedules").child(id).child("month").get()
			month = month1.val()
			time = request.form.get('time')

			all_schedules1 = db.child("Schedules").get()
			all_schedules = all_schedules1.val()

			type1 = db.child("Schedules").child(id).child("type").get()
			type2 = type1.val()


			val2 = True
			reason2 = None

			for schedule in all_schedules[1:]:
				if schedule != None:
					existing_type = schedule.get('type')
					existing_year = schedule.get('year')
					existing_month = schedule.get('month')
					existing_shift = schedule.get('shift')

					if year==existing_year and month==existing_month and time==existing_shift and type2==existing_type:
						val2 = False
						reason2 = "This shift is already selected by another specialist"

			if val2 == True:
				db.child("Schedules").child(id).update({'shift':time})

				times1 = db.child("Visits").get()
				times = times1.val()

				for visit in times[1:]:
					if visit != None:
						date= str(year) + "-" + str(month) + "-"

						if visit.get("emp_id")==uid and date in visit.get("date"):
							db.child("Visits").child(visit.get('id')).remove()

				flash('Schedule was updated succesfully','success')
				return redirect(url_for('updateschedule'))
			if val2 == False:
				flash(reason2, 'danger')
				data1 = db.child("Schedules").child(id).get()
				data = data1.val()
				return render_template('updatescheduleid.html', id=id, data=data)
		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))


@app.route('/deleteschedulePOST/<id>', methods = ['GET', 'POST'])
def deleteschedulePOST(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin
	allowed = False

	if loggedin:
		schedule1 = db.child("Schedules").child(id).get()
		schedule = schedule1.val()
		uid = schedule.get('uid')
		year = schedule.get('year')
		month = schedule.get('month')


		if uid == current_user_userid:
			allowed = True
		if isadmin:
			allowed = True

		if allowed:
			db.child("Schedules").child(id).remove()

			times1 = db.child("Visits").get()
			times = times1.val()

			for visit in times[1:]:
				if visit != None:
					date= str(year) + "-" + str(month) + "-"

					if visit.get("emp_id")==uid and date in visit.get("date"):
						db.child("Visits").child(visit.get('id')).remove()

			flash('Your shift was removed succesfully', 'success')
			return redirect(url_for('updateschedule'))
		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))














@app.route('/createpatient')
def createpatient():
	loggedin = current_user_isloggedin
	if loggedin:
		
		return render_template('createbooklet.html', data=None)
	else:
		return redirect(url_for('login'))
	



@app.route('/createpatient', methods = ['POST'])
def createpatientPOST():
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:

		fname = request.form.get('fname')
		lname = request.form.get('lname')
		pn = request.form.get('pn')
		gender = request.form.get('gender')
		email = request.form.get('email')
		phone = request.form.get('phone')

		# Gaunam last id ir new id
		patients2 = db.child("Patients").get()
		patients = patients2.val()
		new_id = patients[-1].get('id') + 1
		val = True
		reason = None
		SpecialSym2 =['@']

		
		for patient in patients[1:]:
			existing_pn = patient.get('pn')
			existing_email = patient.get('email')
			if email == existing_email:
				reason = "This email is already taken"
				val = False
			if pn == existing_pn:
				reason = "Person with this personal number is already registered"
				val = False

		if len(str(phone)) != 11: 
			reason = 'Phone number is incorrect'
			val = False
		if not any(char in SpecialSym2 for char in email): 
			reason = ' "@" symbol is required in the email'
			val = False
		if len(email) < 3: 
			reason = 'Incorrect email'
			val = False
		if pn != "":
			skaitmuo = str(pn)[0]
			skaicius = int(skaitmuo)
			if (skaicius % 2) == 0 and gender == "Male" or (skaicius % 2) != 0 and gender == "Female":
				reason = 'Gender does not match the personal number'
				val = False
		if len(str(pn)) != 11: 
			reason = 'Incorrect personal number'
			val = False
		if len(lname) < 1: 
			reason = 'Last name field cannot be empty'
			val = False
		if len(fname) < 1: 
			reason = 'First name field cannot be empty'
			val = False
		
		if val:
			data={'id':new_id, 'fname':fname, 'lname':lname, 'pn':pn, 'gender':gender, 'email':email, 'phone':phone,'password':"null", 'resetpsw':True, 'active':False }
			db.child("Patients").child(new_id).set(data)
			flash('New patient was created','success')
			return redirect(url_for('bookletlist'))
		else:
			data={'id':new_id, 'fname':fname, 'lname':lname, 'pn':pn, 'gender':gender, 'email':email, 'phone':phone, 'password':"null", 'active':False }		
			flash(reason,'danger')
			return render_template('createbooklet.html', data=data)
	else:
		return redirect(url_for('login'))

@app.route('/bookletlist')
def bookletlist():
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		rows1 = db.child("Patients").get()
		rows = rows1.val()
		return render_template('bookletlist.html', title='Overview', rows=rows, isadmin=isadmin)
	else:
		return redirect(url_for('login'))

@app.route('/activatepatientPOST/<id>', methods = ['GET', 'POST'])
def activatepatientPOST(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		db.child("Patients").child(id).update({'active':True})
		return redirect(url_for('bookletlist'))
	else:
		return redirect(url_for('login'))

@app.route('/deactivatepatientPOST/<id>', methods = ['GET', 'POST'])
def deactivatepatientPOST(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		db.child("Patients").child(id).update({'active':False})
		return redirect(url_for('bookletlist'))
	else:
		return redirect(url_for('login'))




@app.route('/resetpasswordPOST/<id>', methods = ['GET', 'POST'])
def resetpasswordPOST(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin


	if loggedin:
		db.child("Patients").child(id).update({'resetpsw':True})
		return redirect(url_for('bookletlist'))
	else:
		return redirect(url_for('login'))








@app.route('/booklet/<id>')
def bookletredirect(id):
	loggedin = current_user_isloggedin
	if loggedin:

		data1 = db.child("Patients").child(id).get()
		data = data1.val()


		rec1 = db.child("Records").get()
		rec2 = rec1.val()

		comdata=[]

		records = []
		for record in rec2[1:]:
			existing_pat_id = record.get('pat_id')
			if int(existing_pat_id) == int(id):
				records.append(record)

		return render_template('bookletid.html', id=id, data=data, records=records, comdata=comdata)
	else:
		return redirect(url_for('login'))


@app.route('/booklet/<id>', methods = ['POST'])
def bookletcommentPOST(id):
	loggedin = current_user_isloggedin
	if loggedin:
	
		symptoms = request.form.get('symptoms')
		diagnosis = request.form.get('diagnosis')
		medicine = request.form.get('medicine')
		recommendations = request.form.get('recommendations')
		other = request.form.get('other')

		if symptoms!="" and diagnosis!="" and medicine!="" and recommendations!="":

			if other == "":
				other = "-"

			today = date.today()
			now = datetime.now()
			current_time = now.strftime("%H:%M")
			day = str(today)
			time = str(current_time)
			total = day + " " + time

			records2 = db.child("Records").get()
			records = records2.val()
			new_id = records[-1].get('id') + 1

			type2=db.child("Employees").child(current_user_userid).child("type").get()
			fname=db.child("Employees").child(current_user_userid).child("fname").get()
			lname=db.child("Employees").child(current_user_userid).child("lname").get()

			type1=type2.val()
			emp_name=str(fname.val()) + " " + str(lname.val())




			insert={'id':new_id, 'time':total, 'emp_id':current_user_userid, 'emp_type':type1, 'emp_name':emp_name, 'pat_id':id, 'symptoms':symptoms, 'diagnosis':diagnosis, 'medicine':medicine, 'recommendations':recommendations, 'other':other}
			db.child("Records").child(new_id).set(insert)


			data1 = db.child("Patients").child(id).get()
			data = data1.val()

			rec1 = db.child("Records").get()
			rec2 = rec1.val()

			comdata=[]

			records = []
			for record in rec2[1:]:
				existing_pat_id = record.get('pat_id')
				if int(existing_pat_id) == int(id):
					records.append(record)

			flash('New record was posted succesfully','success')
			return render_template('bookletid.html', id=id, data=data, records=records, comdata=comdata)

		else:
			data1 = db.child("Patients").child(id).get()
			data = data1.val()


			rec1 = db.child("Records").get()
			rec2 = rec1.val()

			records = []
			for record in rec2[1:]:
				existing_pat_id = record.get('pat_id')
				if int(existing_pat_id) == int(id):
					records.append(record)

			comdata={'symptoms':symptoms, 'diagnosis':diagnosis, 'medicine':medicine, 'recommendations':recommendations, 'other':other,}		
			flash('Please fill in the mising data to post the record','danger')
			return render_template('bookletid.html', id=id, data=data, records=records, comdata=comdata)

		
	else:
		return redirect(url_for('login'))


@app.route('/updatepatient/<id>')
def updatepatientredirect(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin

	if loggedin:
		data1 = db.child("Patients").child(id).get()
		data = data1.val()
		return render_template('updatebookletid.html', id=id, data=data)
	else:
		return redirect(url_for('login'))


@app.route('/updatepatientPOST/<id>', methods = ['GET', 'POST'])
def updatepatientPOST(id):

	loggedin = current_user_isloggedin

	if loggedin:

		fname = request.form.get('fname')
		lname = request.form.get('lname')
		pn = request.form.get('pn')
		gender = request.form.get('gender')
		email = request.form.get('email')
		phone = request.form.get('phone')
		patients2 = db.child("Patients").get()
		patients = patients2.val()
		val = True
		reason = None
		SpecialSym2 =['@']

		for patient in patients[1:]:
			existing_pn = patient.get('pn')
			existing_email = patient.get('email')
			existing_id = patient.get('id')
			if email == existing_email and int(id) != int(existing_id):
				reason = "This email is already taken"
				val = False
			if pn == existing_pn and int(id) != int(existing_id):
				reason = "Person with this personal number is already registered"
				val = False

		if len(str(phone)) != 11: 
			reason = 'Phone number is incorrect'
			val = False
		if not any(char in SpecialSym2 for char in email): 
			reason = ' "@" symbol is required in the email'
			val = False
		if len(email) < 3: 
			reason = 'Incorrect email'
			val = False
		if pn != "":
			skaitmuo = str(pn)[0]
			skaicius = int(skaitmuo)
			if (skaicius % 2) == 0 and gender == "Male" or (skaicius % 2) != 0 and gender == "Female":
				reason = 'Gender does not match the personal number'
				val = False
		if len(str(pn)) != 11: 
			reason = 'Incorrect personal number'
			val = False
		if len(lname) < 1: 
			reason = 'Last name field cannot be empty'
			val = False
		if len(fname) < 1: 
			reason = 'First name field cannot be empty'
			val = False
		
		if val:
			db.child("Patients").child(id).update({'fname':fname, 'lname':lname, 'pn':pn, 'gender':gender, 'email':email, 'phone':phone})
			flash('Personal data updated succesfully','success')
			return redirect(url_for('bookletlist'))
		else:
			data={'fname':fname, 'lname':lname, 'pn':pn, 'gender':gender, 'email':email, 'phone':phone, 'password':"null", 'active':False }		
			flash(reason,'danger')
			return render_template('updatebookletid.html', id=id, data=data)
	else:
		return redirect(url_for('login'))










@app.route('/registervisit')
def selectpatient():
	loggedin = current_user_isloggedin
	if loggedin:
		rows1 = db.child("Patients").get()
		rows = rows1.val()
		return render_template('selectpatient.html', title='Overview', rows=rows)
	else:
		return redirect(url_for('login'))

@app.route('/registervisit/<pid>')
def selectemployee(pid):
	loggedin = current_user_isloggedin
	if loggedin:
		rows1 = db.child("Employees").get()
		rows = rows1.val()
		return render_template('selectemployee.html', title='Overview', rows=rows, pid=pid)
	else:
		return redirect(url_for('login'))


@app.route('/registervisit/<pid>/<eid>')
def selectvisit(pid,eid):
	loggedin = current_user_isloggedin
	if loggedin:
		schedules1 = db.child("Schedules").get()
		schedules = schedules1.val()

		existingVisits1 = db.child("Visits").get()
		existingVisits = existingVisits1.val()
		

		rows = []
		exists = False

		selectedEmpSchedules = []
		
		for schedule in schedules[1:]:
			if schedule != None:
				if int(schedule.get('uid')) == int(eid):


					currentYear = datetime.now().year
					currentMonth = datetime.now().month
					dbyear = schedule.get('year')
					dbmonth = schedule.get('month')

					#PATIKRINAM AR MENUO YRA BUVES/ESAMAS/ATEINANTIS
					if int(dbyear)>int(currentYear) or (int(dbyear) == int(currentYear) and int(dbmonth) > int(currentMonth)):
						monthStatus = "busimas"
					elif int(dbyear) == int(currentYear) and int(dbmonth) == int(currentMonth):
						monthStatus = "einamas"
					else:
						monthStatus = "praeities"

					if monthStatus != "praeities":
						#GAUNAM EINAMO SHIFTO DARBO LAIKA
						shift = schedule.get('shift')
						splittedshift = shift.split(" ")
						fromsplitted = splittedshift[0].split(":")
						tosplitted = splittedshift[2].split(":")

						since = fromsplitted[0]
						to = tosplitted[0]

						

						#JEI MENUO ESAMAS, PRADEDAM NUO SEKANCIOS DIENOS, JEI BUSIMAS, NUO 1 MENESIO DIENOS
						if monthStatus == "busimas":
							daysFrom = 1
						elif monthStatus == "einamas":
							now = datetime.now()
							daysFrom = int(now.day) + 1

						#GAUNAM TO MENESIO DIENU KIEKI IR PALEIDZIAM FORA
						amountOfDays = monthrange(int(dbyear), int(dbmonth))

						for day in range(daysFrom, int(amountOfDays[1])+1):
							week_num = date(int(dbyear),int(dbmonth),int(day)).weekday()
							#PATIKRINAM AR NE SAVAITGALIS
							if int(week_num) != 5 and int(week_num) != 6:
								#FORAS EINANTIS PER VALANDAS
								for hour in range(int(since), int(to)+1):
									#FORAS PATIKRINANTIS AR PAS DAKTARA AR PACIENTA JAU NERA VIZITO TUO METU
									for visit in existingVisits[1:]:
										if visit != None:
											fullDate = str(dbyear) + "-" + str(dbmonth) + "-" + str(day)
											fullTime = str(hour) + ":00"
											if visit.get('date') == fullDate and fullTime == visit.get('time') and (int(eid) == int(visit.get('emp_id')) or int(pid) == int(visit.get('pat_id'))):
												exists = True

									if exists == False:
										insert = {'date':fullDate, 'time':fullTime}
										rows.append(insert)

									exists = False



		return render_template('selecttime.html', rows=rows, pid=pid, eid=eid)
	else:
		return redirect(url_for('login'))

@app.route('/registervisit/<pid>/<eid>/<date>/<time>')
def createvisit(pid,eid,date,time):
	loggedin = current_user_isloggedin
	if loggedin:

		pfname1 = db.child("Patients").child(pid).child("fname").get()
		pfname = pfname1.val()
		plname1 = db.child("Patients").child(pid).child("lname").get()
		plname = plname1.val()

		patient = pfname + " " + plname


		efname1 = db.child("Employees").child(eid).child("fname").get()
		efname = efname1.val()
		elname1 = db.child("Employees").child(eid).child("lname").get()
		elname = elname1.val()

		employee = efname + " " + elname

		return render_template('createvisit.html', data=None, pid=pid, eid=eid, date = date, time = time, patient=patient, employee=employee)
	else:
		return redirect(url_for('login'))



@app.route('/registervisit/<pid>/<eid>/<date>/<time>/<patient>/<employee>', methods=['POST'])
def createvisitPOST(pid,eid,date,time,patient,employee):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin
	if loggedin:
		remotely = False
		remotely1 = request.form.get('remotely')
		if remotely1 == 'on':
			remotely = True

		emp_type1 = db.child("Employees").child(eid).child("type").get()
		emp_type = emp_type1.val()

		#PATIKRINU DAR KARTA AR NERA REGISTRUOTO TOKIO VIZITO
		existingVisits1 = db.child("Visits").get()
		existingVisits = existingVisits1.val()
		exists = False
		newid = len(existingVisits)


		for visit in existingVisits[1:]:
			if visit != None:
				if visit.get('date') == date and time == visit.get('time') and (int(eid) == int(visit.get('emp_id')) or int(pid) == int(visit.get('pat_id'))):
					exists = True

		if exists == False:
			db.child("Visits").child(newid).set({'date': date, "emp_id": int(eid), "emp_name": employee, "id": newid, "pat_id": int(pid), "pat_name": patient, "remote": remotely, "status": "upcoming", "time": time, "type":emp_type})
			flash('Schedule was updated succesfully','success')
		else:
			flash('Unfortunately, the visit was taken by another patient, during your registration process','danger')

		return redirect(url_for('allvisits'))			
	else:
		return redirect(url_for('login'))


@app.route('/allvisits')
def allvisits():
	loggedin = current_user_isloggedin
	if loggedin:

		rows = []
		rows.append(None)
		visits1 = db.child("Visits").get()
		visits = visits1.val()

		for visit in visits[1:]:
			rows.append(visit)


		return render_template('visits.html', title='Overview', rows=rows)
	else:
		return redirect(url_for('login'))



@app.route('/patientvisits/<id>')
def patientvisits(id):
	loggedin = current_user_isloggedin
	
	if loggedin:
		rows = []
		rows.append(None)
		visits1 = db.child("Visits").get()
		visits = visits1.val()

		for visit in visits[1:]:
			if visit != None:
				if visit.get("pat_id") == int(id):
					rows.append(visit)
		return render_template('visits.html', title='Overview', rows=rows)
	else:
		return redirect(url_for('login'))



@app.route('/mytodayvisits')
def mytodayvisits():
	loggedin = current_user_isloggedin
	if loggedin:

		rows = []
		rows.append(None)
		visits1 = db.child("Visits").get()
		visits = visits1.val()

		today = date.today()
		todayDate2 = today.strftime("%Y-%m-%d")
		todayDate3 = str(todayDate2).split("-")


		for visit in visits[1:]:
			if visit != None:
				dbDate1 = visit.get("date")
				dbDate2 = dbDate1.split("-")

				date1 = date(int(todayDate3[0]), int(todayDate3[1]), int(todayDate3[2]))
				date2 = date(int(dbDate2[0]), int(dbDate2[1]), int(dbDate2[2]))

				if date1 == date2 and visit.get("emp_id") == int(current_user_userid):
					rows.append(visit)
				
		return render_template('visits.html', title='Overview', rows=rows)

	else:
		return redirect(url_for('login'))


@app.route('/employeevisits/<id>')
def employeevisits(id):
	loggedin = current_user_isloggedin
	isadmin = current_user_isAdmin

	if loggedin:
		if isadmin or int(id)==int(current_user_userid):

			rows = []
			rows.append(None)
			visits1 = db.child("Visits").get()
			visits = visits1.val()

			for visit in visits[1:]:
				if visit != None:
					if visit.get("emp_id") == int(id):
						rows.append(visit)
			return render_template('visits.html', title='Overview', rows=rows)
		else:
			flash('You dont have permission to access this page', 'danger')
			return redirect(url_for('dashboard'))

	else:
		return redirect(url_for('login'))


@app.route('/happenedvisit/<id>')
def happenedvisit(id):
	loggedin = current_user_isloggedin
	if loggedin:

		today = date.today()
		todayDate2 = today.strftime("%Y-%m-%d")
		todayDate3 = str(todayDate2).split("-")

		dbDate1 = db.child("Visits").child(id).child("date").get()
		dbDate2 = dbDate1.val()
		dbDate3 = dbDate2.split("-")

		date1 = date(int(todayDate3[0]), int(todayDate3[1]), int(todayDate3[2]))

		date2 = date(int(dbDate3[0]), int(dbDate3[1]), int(dbDate3[2]))

		if date1 >= date2:
			db.child("Visits").child(id).update({'status':"happened"})
			flash('Status was updated succesfully','success')
		else:
			flash('You cannot set future visit as happened','danger')

		return redirect(url_for('allvisits'))
	else:
		return redirect(url_for('login'))



@app.route('/missedvisit/<id>')
def missedvisit(id):
	loggedin = current_user_isloggedin

	if loggedin:

		today = date.today()
		todayDate2 = today.strftime("%Y-%m-%d")
		todayDate3 = str(todayDate2).split("-")

		dbDate1 = db.child("Visits").child(id).child("date").get()
		dbDate2 = dbDate1.val()
		dbDate3 = dbDate2.split("-")

		date1 = date(int(todayDate3[0]), int(todayDate3[1]), int(todayDate3[2]))

		date2 = date(int(dbDate3[0]), int(dbDate3[1]), int(dbDate3[2]))

		if date1 >= date2:
			db.child("Visits").child(id).update({'status':"missed"})
			flash('Status was updated succesfully','success')
		else:
			flash('You cannot set future visit as missed','danger')

		return redirect(url_for('allvisits'))
	else:
		return redirect(url_for('login'))


@app.route('/deletevisit/<id>')
def deletevisit(id):
	loggedin = current_user_isloggedin

	if loggedin:

		status1 = db.child("Visits").child(id).child("status").get()
		status = status1.val()

		if str(status) == "upcoming": 
			db.child("Visits").child(id).remove()
			flash('Visit was deleted succesfully','success')
		else:
			flash('You cannot cancel this visit','success')
		return redirect(url_for('allvisits'))
	else:
		return redirect(url_for('login'))







if __name__ == '__main__':
    app.run(debug=True)