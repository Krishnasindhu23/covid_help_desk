from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import MySQLdb
app = Flask(__name__)

db = MySQLdb.connect("localhost", "root", "root", "mysql")

@app.route('/', methods=['GET', 'POST'])
def first():
    return render_template('first.html')

@app.route('/hospital_login')
def hospital_login():
    return render_template('login_hosp.html')

@app.route('/loginhosp',methods=['POST'])
def loginhosp():
    if request.method == "POST":
        details = request.form
        phoneno = details['phno']
        password = details['pass']
        cur = db.cursor()
        cur.execute('select password from hosp_lst where phone LIKE %s',[phoneno])
        db.commit()
        myresult = cur.fetchall()
        print(myresult)
        s=myresult[0][0]
        if s==password:
            cur.execute('select H1.hosp_name,H2.vbed,H2.obed,H2.nbed from hosp_lst H1,hosp_bed H2 where H1.phone LIKE %s and H2.phone LIKE %s',[phoneno,phoneno])
            data=cur.fetchall()
            return render_template("update.html",value=data)
        else:
            return "Wrong Password"


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == "POST":
        details = request.form
        hospName = details['hos_name']
        stateName = details['state']
        districtName = details['dist']
        password=details['pass']
        phoneNo=details['sphno']
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO hosp_lst VALUES (%s, %s, %s ,%s,%s);", (hospName, stateName,districtName,phoneNo,password))
            db.commit()
            cur.close()
        except Exception as e:
            print(e)
        return "Success"
    return "No success"

@app.route("/update",methods=['GET','POST'])
def update():
    print("Hellooo")
    return None





