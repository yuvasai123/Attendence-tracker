from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.datastructures import MultiDict

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask1'

app.secret_key = "YUVASnujknbhgAI5465"
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('entry.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        password = request.form['password']
        working = request.form['working']
        total = request.form['total']
        attended = request.form['attended']
        session['working'] = working
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM accounts WHERE username = %s AND password = %s", (username, password))
        acc = cur.fetchone()
        if acc:
            return "account already exists"
        else:
            cur.execute("INSERT INTO `accounts`(`username`, `password`, `working`, `total`, `attended`) VALUES (%s, %s, %s, %s, %s)", (username, password, working, total, attended))
            mysql.connection.commit()
            return redirect(url_for('suc'))

@app.route('/postperiods')
def suc():
    return render_template('post periods.html')

@app.route('/redirect1')
def redirect1():
    return render_template('login.html')

@app.route('/redirect2')
def redirect2():
    return render_template('entry.html')

@app.route('/post', methods=['GET', 'POST'])
def post():
    user = session['username']
    per = session['result']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM subjects WHERE username = %s", (user,))
    acc = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return render_template('post.html', data=acc[1:], per=per)

@app.route('/create', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        if 'username' in session:
            user = session['username']
        total = session['working']
        result = request.form
        k = len(result)
        li = []
        pi = []
        res = []
        list = []
        subs = []
        si = []
        list.append("'" + user + "'")
        res.append("date DATE")

        for i in range(int(total)):
            si.append("period" + str(i + 1))
        subs.append("username")
        for field in result.values():
            list.append("'" + field + "'")
        for field in result.values():
            li.append("'" + field + "'")
        for i in range(len(result)):
            pi.append("subject" + str(i + 1))
        for i in range(len(result)):
            subs.append("subject" + str(i + 1))
        for i in si:
            res.append(i + " VARCHAR(50)")
        field_query = " ( " + ", ".join(res) + " ) "
        create_table_query = 'CREATE TABLE `' + user + '`' + field_query
        table = " ( " + ", ".join(subs) + " ) "
        values = " ( " + ", ".join(list) + " ) "

        insertion = 'INSERT INTO `subjects`' + table + "VALUES" + values
        cur = mysql.connection.cursor()
        session['insertion'] = insertion
        cur.execute(create_table_query)
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('luc'))

    return create_table_query

@app.route('/luc')
def luc():
    ins = session['insertion']
    cur = mysql.connection.cursor()
    cur.execute(ins)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('redirect2'))

@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if request.method == 'POST':
        user = session['username']
        res = request.form
        date = request.form['date']
        li = []
        list = []
        x = ""
        li.append("date")
        j = session['result']
        for i in j:
            x += str(i)
        for i in range(int(x)):
            li.append("period" + str(i + 1))
        list.append("'" + date + "'")
        table = " ( " + ", ".join(li) + " ) "
        for i in range(int(x)):
            a = "options" + str(i + 1)
            b = "sub" + str(i + 1)
            list.append("'" + res[b] + "-" + res[a] + "'")
        values = " ( " + ", ".join(list) + " ) "
        insertion = 'INSERT INTO `' + user + '`' + table + "VALUES" + values
        cur = mysql.connection.cursor()
        cur.execute(insertion)
        cur.execute("SELECT * FROM subjects WHERE username = %s", (user,))
        per = session['result']
        acc = cur.fetchone()
        
   
       
        
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main', data=acc[1:], per=per))

@app.route('/main')
def main():
    user = session['username']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM subjects WHERE username = %s", (user,))
    per = session['result']
    acc = cursor.fetchone()
    query = f"SELECT * FROM `{user}`"
    cursor.execute(query)
    fulldata = cursor.fetchall()
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'yuva'ORDER BY ORDINAL_POSITION")
    columns=cursor.fetchall()
    columning=[]
                
    for colu in columns:
        columning.append(colu[0])
               
            
    abs_counts = 0
    pre_counts = 0
    for period in columning:
        query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%abs'"
        cursor.execute(query)
        abs_counts = abs_counts+cursor.fetchone()[0]
    for period in columning:
         query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%pre'"
         cursor.execute(query)
         pre_counts = pre_counts+cursor.fetchone()[0]
    data=acc[1:]
    print(data)
                
    subject_names = [subj for subj in acc if isinstance(subj, str)]
    my_list = [item for item in subject_names if item != '']
                
    subcount=[]
    for data in my_list[1:]:
        sub=0
        for period in columning[1:]:
            query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{data}%'"
            cursor.execute(query)
            sub=sub+(cursor.fetchone()[0])
            print(period,data,sub)
            subcount.append(sub)
                    
    subject_counts = {subject: {'present': 0, 'absent': 0} for subject in my_list[1:]}
                
    for period in columning[1:]:
        for subject in my_list[1:]:
                        # Count absents
            query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{subject}%' AND `{period}` LIKE '%abs%'"
            cursor.execute(query)
            abs_count = cursor.fetchone()[0]
            subject_counts[subject]['absent'] += abs_count

                        # Count presents
            query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{subject}%' AND `{period}` LIKE '%pre%'"
            cursor.execute(query)
            pre_count = cursor.fetchone()[0]
            subject_counts[subject]['present'] += pre_count
    mysql.connection.commit()
    cursor.close()
    return render_template('main.html',query=fulldata,data=my_list[1:],per=per,pre_counts=pre_counts,abs_counts=abs_counts,dict=subject_counts,user=session['username'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            if 'username' in session:
                user = session['username']
                cursor.execute('SELECT `working` FROM `accounts` WHERE username=%s', (user,))
                result = cursor.fetchone()
                session['result'] = (result)
                cursor.execute("SELECT * FROM subjects WHERE username = %s", (user,))
                per = session['result']
                acc = cursor.fetchone()
                cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'yuva'ORDER BY ORDINAL_POSITION")
                columns=cursor.fetchall()
                columning=[]
                
                for colu in columns:
                    columning.append(colu[0])
               
                
                abs_counts = 0
                pre_counts = 0
                for period in columning:
                    query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%abs'"
                    cursor.execute(query)
                    abs_counts = abs_counts+cursor.fetchone()[0]
                for period in columning:
                    query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%pre'"
                    cursor.execute(query)
                    pre_counts = pre_counts+cursor.fetchone()[0]
                data=acc[1:]
                print(data)
                
                subject_names = [subj for subj in acc if isinstance(subj, str)]
                my_list = [item for item in subject_names if item != '']
                
                subcount=[]
                for data in my_list[1:]:
                    sub=0
                    for period in columning[1:]:
                        query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{data}%'"
                        cursor.execute(query)
                        sub=sub+(cursor.fetchone()[0])
                        print(period,data,sub)
                    subcount.append(sub)
                    
                subject_counts = {subject: {'present': 0, 'absent': 0} for subject in my_list[1:]}
                
                for period in columning[1:]:
                    for subject in my_list[1:]:
                        # Count absents
                        query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{subject}%' AND `{period}` LIKE '%abs%'"
                        cursor.execute(query)
                        abs_count = cursor.fetchone()[0]
                        subject_counts[subject]['absent'] += abs_count

                        # Count presents
                        query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{subject}%' AND `{period}` LIKE '%pre%'"
                        cursor.execute(query)
                        pre_count = cursor.fetchone()[0]
                        subject_counts[subject]['present'] += pre_count
                    
                mysql.connection.commit()
                cursor.close()
                # return str(subject_counts["english"]["present"])
                return render_template('main.html',data=my_list[1:],per=per,pre_counts=pre_counts,abs_counts=abs_counts,dict=subject_counts,user=session['username'])
                # return render_template('main.html',data=acc[1:],per=per,pre_counts=pre_counts,abs_counts=abs_counts)
                
        else:
            msg = 'Incorrect username / password !'
    return render_template('entry.html', msg=msg)

@app.route('/view attendence',methods=['GET','POST'])
def viewdata():
    user = session['username']
    print(user)
    cursor = mysql.connection.cursor()
    fromdate = request.form['fromdate']
    print(fromdate) 
    todate = request.form['todate']
    print(todate)
    # Assuming the table has columns 'date', 'period1', 'period2', etc.
    cursor.execute("SELECT * FROM subjects WHERE username = % s", (user, ))
    per=session['result']
    acc=cursor.fetchone()
    per=session['result']
    query = "SELECT * FROM `{}` WHERE `date` BETWEEN %s AND %s".format(user)
    cursor.execute(query, (fromdate, todate))
    
    fulldata = cursor.fetchall()
    cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'yuva'ORDER BY ORDINAL_POSITION")
    columns=cursor.fetchall()
    columning=[]
                
    for colu in columns:
        columning.append(colu[0])
               
            
    abs_counts = 0
    pre_counts = 0
    for period in columning:
        query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%abs'"
        cursor.execute(query)
        abs_counts = abs_counts+cursor.fetchone()[0]
    for period in columning:
         query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%pre'"
         cursor.execute(query)
         pre_counts = pre_counts+cursor.fetchone()[0]
    data=acc[1:]
    print(data)
                
    subject_names = [subj for subj in acc if isinstance(subj, str)]
    my_list = [item for item in subject_names if item != '']
                
    subcount=[]
    for data in my_list[1:]:
        sub=0
        for period in columning[1:]:
            query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{data}%'"
            cursor.execute(query)
            sub=sub+(cursor.fetchone()[0])
            print(period,data,sub)
            subcount.append(sub)
                    
    subject_counts = {subject: {'present': 0, 'absent': 0} for subject in my_list[1:]}
                
    for period in columning[1:]:
        for subject in my_list[1:]:
                        # Count absents
            query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{subject}%' AND `{period}` LIKE '%abs%'"
            cursor.execute(query)
            abs_count = cursor.fetchone()[0]
            subject_counts[subject]['absent'] += abs_count

                        # Count presents
            query = f"SELECT COUNT(*) FROM `{user}` WHERE `{period}` LIKE '%{subject}%' AND `{period}` LIKE '%pre%'"
            cursor.execute(query)
            pre_count = cursor.fetchone()[0]
            subject_counts[subject]['present'] += pre_count
    mysql.connection.commit()
    cursor.close()
    print(fromdate,todate)
    return render_template('main.html',scroll_to='viewdata',query=fulldata,data=my_list[1:],per=per,pre_counts=pre_counts,abs_counts=abs_counts,dict=subject_counts,user=session['username'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('redirect2'))

if __name__ == '__main__':
    app.run(debug=True)
