import base64
import io

from os import renames

import matplotlib
from PIL import Image
from flask import url_for
from flask import Flask, render_template, request, make_response
from flask.templating import render_template_string
from flask_mysqldb import MySQL
matplotlib.use('TkAgg')
import MySQLdb
import numpy as np
import matplotlib.pyplot as plt


# import make_response
app = Flask(__name__)

db = MySQLdb.connect("localhost", "root", "root", "mysql")

@app.route('/',methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/first', methods=['GET', 'POST'])
def first():
    return render_template('first.html')


@app.route('/hospital_login')
def hospital_login():
    return render_template('login_hosp.html')


@app.route('/view')
def view():
    return render_template('view.html')


@app.route('/view1', methods=['POST'])
def view1():
    if request.method == 'POST':
        details = request.form
        state1 = details['state']
        district1=details['city']
        cur = db.cursor()
        cur.execute('select state from st_req')
        db.commit()
        rest=cur.fetchall()
        flag=0
        for x in rest:
            if state1 in x:
                flag=1
        if flag!=1:
            cur.execute("insert into st_req values(%s,%s);", (state1, '0'))
            db.commit()
        cur.execute(
            "select h1.hosp_name,h2.vbed,h2.obed,h2.nbed,h1.phone from hosp_lst h1, hosp_bed h2 where h1.state like %s and h1.district like %s and h1.phone=h2.phone;",[state1, district1])
        db.commit()
        res1 = cur.fetchall()
        cur.execute(
            "select h1.hosp_name, h1.district, h2.vbed, h2.obed, h2.nbed, h1.phone from hosp_lst h1, hosp_bed h2 where h1.state like %s and h1.phone=h2.phone;",
            [state1])
        db.commit()
        res2 = cur.fetchall()
        resp1 = make_response(render_template('show.html', var1=res1, var2=res2,state=state1,district=district1))
        resp1.set_cookie('state', state1)
        return resp1


    #return render_template('show.html', var1=res1, var2=res2,state=state1,district=district1)


@app.route('/loginhosp', methods=['POST'])
def loginhosp():
    if request.method == "POST":
        details = request.form
        phoneno = details['phno']
        password = details['pass']
        #print(phoneno, password)
        cur = db.cursor()
        cur.execute('select password from hosp_lst where phone LIKE %s', [phoneno])
        db.commit()
        myresult = cur.fetchall()
        s = myresult[0][0]
        if s == password:
            cur.execute(
                'select H1.hosp_name,H2.vbed,H2.obed,H2.nbed from hosp_lst H1,hosp_bed H2 where H1.phone LIKE %s and H2.phone LIKE %s',
                [phoneno, phoneno])
            db.commit()
            data = cur.fetchall()
            print(data)
            #print(data)
            resp = make_response(render_template('update.html', value=data))
            resp.set_cookie('user', phoneno)
            return resp
        else:
            return "<h2 style='color:red;'>Wrong Password!!<br>Try again here.</h2> <a href='/hospital_login'><button> Login Page</button></a> "


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        details = request.form
        hospName = details['hos_name']
        stateName = details['state']
        districtName = details['dist']
        password = details['spass']
        phoneNo = details['sphno']
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO hosp_lst VALUES (%s, %s, %s ,%s,%s);",
                        (hospName, stateName, districtName, phoneNo, password))
            db.commit()
            cur.execute("insert into hosp_bed values (%s,%s,%s,%s);", (phoneNo, '0', '0', '0'))
            db.commit()
            cur.close()

        except Exception as e:
            print(e)
        return render_template('signsuccess.html')
    return "No success"


@app.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == "POST":
        details = request.form
        v = details['v']
        o = details['o']
        n = details['n']
        # print(phoneno)
        phn = request.cookies.get('user')
        cur = db.cursor()
        cur.execute("update hosp_bed set vbed =%s, obed = %s,nbed= %s where phone = %s;", (v, o, n, phn))
        db.commit()
        res = cur.fetchall()
        # print(res)
        # print(phn)

    return render_template('updatesuccess.html')

@app.route('/req',methods=['POST','GET'])
def req():
    if request.method=='POST':
        details=request.form
        r=details['r']
        state1 = request.cookies.get('state')
        cur=db.cursor()
        cur.execute('select req from st_req where state  like %s',[state1])
        db.commit()
        res=cur.fetchall()
        cur.execute("update st_req set req =%s where state = %s ;",(str(int(r)+int(res[0][0])),state1))
        db.commit()
    return render_template('redirect.html')



@app.route('/bargraph')
def hello_world():
    demand=[]
    st=[]

    supply=[]

    cur=db.cursor()
    cur.execute('select sum(H2.obed)+sum(H2.nbed)+sum(H2.vbed) as "total" ,H1.state from hosp_bed H2,hosp_lst H1,st_req H3 where H1.phone=H2.phone and H1.state=H3.state group by H1.state order by H1.state;')
    db.commit()
    res1=cur.fetchall()
    print(res1)
    cur.execute('select distinct H2.req,H2.state from st_req H2,hosp_lst H1 where H1.state=H2.state order by H1.state;')
    db.commit()
    res2 = cur.fetchall()
    print(res2)
    for i in range(len(res1)):
        st.append(res1[i][1])
    for i in range(len(res2)):
        demand.append(int(res2[i][0]))
    for i in range(len(res1)):
        supply.append(res1[i][0])
    X_axis = np.arange(len(st))
    plt.bar(X_axis - 0.2, demand, 0.4, label='Demand')
    plt.bar(X_axis + 0.2, supply, 0.4, label='Supply')

    plt.xticks(X_axis, st)
    plt.xlabel("States")
    plt.ylabel("Demand vs Supply")
    plt.legend()

    plt.savefig('static/demandsupply.jpg')
    im = Image.open("static/demandsupply.jpg")
    data = io.BytesIO()
    im.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())

    return render_template("bar.html", img_data=encoded_img_data.decode('utf-8'))

@app.route("/covidhome")
def covidhome():
    return render_template('covidhome.html')


@app.route("/exercise")
def exercise():
    return render_template("exercise.html")
@app.route("/foods")
def foods():
    return render_template("foods.html")

@app.route("/dds")
def dds():
    return render_template("dosdonts.html")





