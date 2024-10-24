from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'quiz_app'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template ('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM teacher WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            flash('Account already exists with this username!', 'danger')
            return redirect(url_for('register'))
        
        cursor.execute('INSERT INTO teacher (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cursor.close()

        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    
    return render_template ('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM teacher WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('teacher'))
        else:
            flash('Incorrect username or password!', 'danger')
            return redirect(url_for('login'))
        
    return render_template ('login.html')

@app.route('/teacher')
def teacher():
    if 'username' in session:
        return render_template('teacher.html', username=session['username'])
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))
    
@app.route('/student_reg', methods=['GET', 'POST'])
def student_reg():
    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM student WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists with this username!', 'danger')
            return redirect(url_for('student_reg'))
        
        cursor.execute('INSERT INTO student (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cursor.close()

        flash('You have successfully registered!', 'success')
        return redirect(url_for('student_log'))

    return render_template('student_reg.html')

@app.route('/student_log', methods=['GET', 'POST'])
def student_log():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM student WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()

        if account:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('student'))
        else:
            flash('Incorrect username or password!', 'danger')
            return redirect(url_for('student_log'))
        
    return render_template('student_log.html')

@app.route('/student')
def student():
    if 'username' in session:
        return render_template('student.html', username=session['username'])
    else:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('student_log'))

if __name__=='__main__':
    app.run(debug=True)