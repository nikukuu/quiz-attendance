from flask import Flask, render_template, url_for, request, redirect, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import random, string

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'quiz_app'

mysql = MySQL(app)

def generate_class_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

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
            flash('Account already exists with this username.', 'danger')
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
            return redirect(url_for('teacher'))
        else:
            flash('Incorrect username or password.', 'danger')
            return redirect(url_for('login'))
        
    return render_template ('login.html')

    
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
            flash('Account already exists with this username.', 'danger')
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
            return redirect(url_for('student'))
        else:
            flash('Incorrect username or password.', 'danger')
            return redirect(url_for('student_log'))
        
    return render_template('student_log.html')

@app.route('/teacher')
def teacher():
    if 'username' in session:
        # Connect to the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch all classes from the database
        cursor.execute('SELECT class_name, class_code FROM t_classes')
        classes = cursor.fetchall()
        cursor.close()
        
        # Render the template with the username and classes
        return render_template('teacher.html', username=session['username'], classes=classes)
    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

@app.route('/student')
def student():
    if 'username' in session:
        return render_template('student.html', username=session['username'])
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('student_log'))
    
#-------------------------------AUTHENTICATION--END--CODE-------------------------------#


#-------------------------------ACCOUNT--INFORMATION-------------------------------------#

@app.route('/t_acc_info')
def t_acc_info():
    if 'username' in session:
        # Retrieve user details from the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM teacher WHERE username = %s', (session['username'],))
        account = cursor.fetchone()

        cursor.execute('SELECT class_name, class_code FROM t_classes')
        classes = cursor.fetchall()
        cursor.close()

        return render_template('t_acc_info.html', account=account, username=session['username'], classes=classes)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
#-------------------------------ACCOUNT--INFORMATION--END--CODE---------------------------#

@app.route('/t_classes', methods=['GET', 'POST'])
def t_classes():
    new_class_code = None  # Initialize code variable

    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            class_name = request.form['class_name']
            teacher_username = session['username']
            new_class_code = generate_class_code()  # Generate the code

            cursor.execute(
                'INSERT INTO t_classes (class_name, class_code, teacher_username) VALUES (%s, %s, %s)',
                (class_name, new_class_code, teacher_username)
            )
            mysql.connection.commit()

            flash('Class created successfully!', 'success')
            # Redirecting to the same page with the new class code
            return redirect(url_for('t_classes', code=new_class_code))

        # Fetch existing classes
        cursor.execute('SELECT * FROM t_classes')
        classes = cursor.fetchall()
        cursor.close()

        # Retrieve new_class_code from URL parameters if available
        new_class_code = request.args.get('code', None)

        return render_template('t_classes.html', username=session['username'], classes=classes, new_class_code=new_class_code)

    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))
    
@app.route('/t_quiz', defaults={'class_code': None})
@app.route('/t_quiz/<class_code>')
def t_quiz(class_code):
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch all classes
        cursor.execute('SELECT class_name, class_code FROM t_classes')
        classes = cursor.fetchall()

        # If a specific class_code is provided, fetch that class's details
        selected_class = None
        if class_code:
            cursor.execute('SELECT class_name, class_code FROM t_classes WHERE class_code = %s', (class_code,))
            selected_class = cursor.fetchone()
        
        cursor.close()
        
        # Render the template with classes and any selected class
        return render_template(
            't_quiz.html',
            username=session['username'],
            classes=classes,
            selected_class=selected_class
        )
    
    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))

@app.route('/delete_class/<class_code>', methods=['POST'])
def delete_class(class_code):
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Delete the class with the given class_code
        cursor.execute('DELETE FROM t_classes WHERE class_code = %s', (class_code,))
        mysql.connection.commit()
        cursor.close()

        flash('Class deleted successfully!', 'success')
        return redirect(url_for('t_classes'))
    else:
        flash('You need to log in first', 'danger')
        return redirect(url_for('login'))
    
@app.route('/class_quizzes/<class_code>', methods=['GET', 'POST'])
def class_quizzes(class_code):
    if 'username' in session:
        if request.method == 'POST':
            quiz_title = request.form['quiz_title']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('INSERT INTO quizzes (class_code, quiz_title) VALUES (%s, %s)', (class_code, quiz_title))
            mysql.connection.commit()
            cursor.close()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('class_quizzes', class_code=class_code))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Fetch class info and quizzes
        cursor.execute('SELECT * FROM t_classes WHERE class_code = %s', (class_code,))
        selected_class = cursor.fetchone()

        cursor.execute('SELECT * FROM quizzes WHERE class_code = %s', (class_code,))
        quizzes = cursor.fetchall()

        cursor.execute('SELECT class_name, class_code FROM t_classes')
        classes = cursor.fetchall()

        cursor.close()

        return render_template('class_quizzes.html',
                               selected_class=selected_class,
                               quizzes=quizzes,
                               username=session['username'],
                               classes=classes)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/manage_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def manage_quiz(quiz_id):
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            # Retrieve question and options from the form
            question_text = request.form['question_text']
            options = request.form.getlist('options[]')  # Get all options
            correct_answer_index = int(request.form['correct_answer']) - 1  # Convert to 0-based index
            correct_answer = options[correct_answer_index]  # Get the correct answer

            # Insert the question into the database
            cursor.execute(
                'INSERT INTO quiz_questions (quiz_id, question_text, correct_answer) VALUES (%s, %s, %s)',
                (quiz_id, question_text, correct_answer)
            )
            question_id = cursor.lastrowid  # Get the ID of the newly added question

            # Insert options into the database
            for option in options:
                cursor.execute(
                    'INSERT INTO quiz_options (question_id, option_text) VALUES (%s, %s)',
                    (question_id, option)
                )

            mysql.connection.commit()
            flash('Question added successfully!', 'success')
            return redirect(url_for('manage_quiz', quiz_id=quiz_id))

        # Fetch quiz details
        cursor.execute('SELECT * FROM quizzes WHERE quiz_id = %s', (quiz_id,))
        quiz = cursor.fetchone()
        class_code = quiz['class_code']

        # Fetch questions and their options
        cursor.execute('SELECT * FROM quiz_questions WHERE quiz_id = %s', (quiz_id,))
        questions = cursor.fetchall()

        # Fetch options for each question
        for question in questions:
            cursor.execute('SELECT * FROM quiz_options WHERE question_id = %s', (question['question_id'],))
            question['options'] = cursor.fetchall()

        cursor.execute('SELECT class_name, class_code FROM t_classes')
        classes = cursor.fetchall()
        cursor.close()

        return render_template('manage_quiz.html',
                               quiz=quiz,
                               questions=questions,
                               username=session['username'],
                               classes=classes, class_code=class_code)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/edit_question/<int:question_id>/<int:quiz_id>', methods=['GET', 'POST'])
def edit_question(question_id, quiz_id):
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            question_text = request.form['question_text']
            options = request.form.getlist('options[]')
            correct_answer_index = int(request.form['correct_answer']) - 1
            correct_answer = options[correct_answer_index]

            # Update question text and correct answer
            cursor.execute(
                'UPDATE quiz_questions SET question_text = %s, correct_answer = %s WHERE question_id = %s',
                (question_text, correct_answer, question_id)
            )

            # Update options
            cursor.execute('DELETE FROM quiz_options WHERE question_id = %s', (question_id,))
            for option in options:
                cursor.execute(
                    'INSERT INTO quiz_options (question_id, option_text) VALUES (%s, %s)',
                    (question_id, option)
                )

            mysql.connection.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('manage_quiz', quiz_id=quiz_id))

        # Fetch existing question and options
        cursor.execute('SELECT * FROM quiz_questions WHERE question_id = %s', (question_id,))
        question = cursor.fetchone()
        cursor.execute('SELECT * FROM quiz_options WHERE question_id = %s', (question_id,))
        question['options'] = cursor.fetchall()

        cursor.close()

        return render_template('edit_question.html', question=question, quiz_id=quiz_id)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if 'username' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM quiz_questions WHERE question_id = %s', (question_id,))
        cursor.execute('DELETE FROM quiz_options WHERE question_id = %s', (question_id,))
        mysql.connection.commit()
        cursor.close()
        flash('Question deleted successfully!', 'success')
        return redirect(request.referrer)
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))
    
@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if 'username' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # First, delete the quiz's options and questions
        cursor.execute('DELETE FROM quiz_options WHERE question_id IN (SELECT question_id FROM quiz_questions WHERE quiz_id = %s)', (quiz_id,))
        cursor.execute('DELETE FROM quiz_questions WHERE quiz_id = %s', (quiz_id,))

        # Then, delete the quiz itself
        cursor.execute('DELETE FROM quizzes WHERE quiz_id = %s', (quiz_id,))
        
        mysql.connection.commit()
        cursor.close()

        flash('Quiz deleted successfully!', 'success')
        return redirect(url_for('class_quizzes', class_code=request.referrer.split("/")[-1]))
    else:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

if __name__=='__main__':
    app.run(debug=True)