import datetime
import os
import webbrowser
import pymysql
from functools import wraps
from flask import Flask, render_template, Response, redirect, url_for, request, session, flash, send_from_directory
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email

app = Flask(__name__)
app.secret_key = "DMVTees"


class User:  # Define User Group
    def __init__(self, username, password, authority=""):
        self.username = username
        self.password = password
        self.authority = authority

    def __eq__(self, other):
        return self.username == other.username and self.password == other.username


def login_Requir(func):
    @wraps(func)  # 保留源信息，本质是endpoint装饰，否则修改函数名很危险
    def inner(*args, **kwargs):  # 接收参数，*args接收多余参数形成元组，**kwargs接收对于参数形成字典
        user = session.get('username')  # 表单接手网页中登录信息，存入到session中，判断用户是否登录
        if not user:
            return redirect('/login')  # 没有登录就跳转到登录路由下
        return func(*args, **kwargs)  # 登录成功就执行传过来的函数

    return inner


@app.route('/test1')  # test page
def test1():
    return render_template('form.html')


@app.route('/')
def init():
    return render_template('login.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')
        # names = ["admin", "Admin"]
        # passwords = ["admin", "Admin"]
        userInfo = "SELECT Username, Password_show, AES_DECRYPT (Encryptedpassword, 'DMVTees') as Password, Authority from User_Account;"
        log_user = User(username, password)
        users = get_users(get_dict_data_sql(userInfo))
        for i in users:
            if log_user == i:  # Default Login
                session['username'] = i.username
                session['authority'] = i.authority
                return redirect(url_for('index'))

    flash("Wrong input", 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_Requir
def logout():
    session.clear()
    flash("Logout Successfully!", 'success')
    return redirect(url_for('login'))


@app.route('/editable/<tableName>')
def editable(tableName="Orders"):
    if session['authority'] == 'root':
        sql = "SELECT * FROM " + tableName
        db = connectdb()
        cur = db.cursor()
        cur.execute("show tables")
        table_list = [tuple[0] for tuple in cur.fetchall()]
        cur.execute(sql)
        content = cur.fetchall()
        # 获取数据库表的表头
        labels = [tuple[0] for tuple in cur.description]
        db.close()
        return render_template('editable.html', content=content, labels=labels,
                               table_list=table_list, tableName=tableName)
    else:
        return redirect(url_for('index'))


@app.route('/post', methods=['POST', 'GET'])
def signUpUse():
    if request.method == 'POST':
        print(request.form['username'])


@app.route('/index.html')
@login_Requir
def index(sql="SELECT * FROM Orders"):
    if True:
        orders = get_dict_data_sql(sql)
        keys, value = barData(orders)

        barChart = {'label': keys, 'data': value}
        status = job_status(orders)
        user = session.get('username')
        return render_template('index.html', orders=orders, bar=barChart, status=status, username=user)
    else:
        return render_template('login.html')


@app.route('/uncompleted_orders')
@login_Requir
def uncompleted_orders():
    return index(sql="SELECT * FROM Orders where OrderStatus != 'Done' or OrderStatus != 'done'")


@app.route('/completed_orders')
@login_Requir
def completed_orders():
    return index(sql="SELECT * FROM Orders where OrderStatus = 'Done' or OrderStatus = 'done'")


@app.route('/new_orders')
@login_Requir
def new_orders():
    return index(sql="SELECT * FROM Orders where TO_DAYS(OrderDate) = TO_DAYS(NOW())")


@app.route('/error_orders')
@login_Requir
def error_orders():
    return index(sql="SELECT * FROM Orders where "
                     "DueDate is null or OrderDate is null or DueDate ='0000-00-00'or OrderDate='0000-00-00' ")


@app.route('/delete/<tableName>', methods=['get'])
def delete(tableName):
    id = request.args.get("ID")

    con = connectdb()
    cur = con.cursor()
    cur.execute("SELECT * FROM " + tableName)
    label = [tuple[0] for tuple in cur.description]
    IDName = label[0]
    sql = 'DELETE FROM {0} WHERE {1}={2}'.format(tableName, IDName, id)
    print(sql)
    cur.execute(sql)
    con.commit()
    con.close()
    flash("Delete Successful", 'success')
    return redirect(url_for("editable", tableName=tableName))


@app.route('/edit/<tableName>', methods=['get'])
def edit(tableName):
    sql = "SELECT * FROM " + tableName
    con = connectdb()
    cur = con.cursor()
    cur.execute(sql)
    label = [tuple[0] for tuple in cur.description]
    print(label)
    content = [request.args.get(i) for i in label]
    print(content)
    n = 1
    if [content[0]] is not None:
        sqlExist = "SELECT * FROM " + tableName + "  WHERE " + label[0] + " = " + content[0]
        res = cur.execute(sqlExist)
        if res:
            print("Existing ", res)
        else:
            sql = 'insert into {0} ({1}) values({2})'.format(tableName, label[0], content[0])
            cur = con.cursor()
            print(sql)
            cur.execute(sql)

        while n < len(content):
            if content[n] is not None:
                sql = 'update {0} set {1}="{2}" where {3}={4}'.format(tableName, label[n], content[n], label[0],
                                                                      content[0])
                cur = con.cursor()
                print(sql)
                cur.execute(sql)
                n += 1
    else:
        flash('Wrong ID input', 'danger')
        return redirect(url_for("editable", tableName=tableName))

    con.commit()
    con.close()
    flash('Submit Successful!', 'success')
    return redirect(url_for("editable", tableName=tableName))


@app.route('/print')
@login_Requir
def printOrder():
    Info = ''

    return render_template('Print.html', Info=Info)


@app.route('/check', methods=['post'])
@login_Requir
def check():
    ID = request.form.get('ID')
    Info = "Successful！"
    out = []
    if ID is not None:
        ID = ID.replace(' ', '').split(",")
        for i in ID:
            try:
                out.append(int(i))
            except:
                pass
        if len(out) == 0:
            Info = "wrong Input!"
            return render_template('Print.html', Info=Info)
    else:
        Info = "wrong Input!"
        return render_template('Print.html', Info=Info)
    out = str(out).replace("[", "(").replace("]", ")")
    db = connectdb()
    cur = db.cursor()
    if len(ID) > 1:
        sql = "SELECT * FROM Orders Natural join Customer Natural join Order_Detail where OrderID in {0}".format(out)
        cur.execute(sql)
        content = cur.fetchall()
        labels = [tuple[0] for tuple in cur.description]
        db.close()
        Info = "Printed at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template('PrintResult.html', labels=labels, content=content, Info=Info)
    else:
        sql = "SELECT * FROM Orders Natural join Customer Natural join Order_Detail where OrderID =" + out
        cur.execute(sql)
        content = cur.fetchall()
        labels = [tuple[0] for tuple in cur.description]

        design = get_design()
        cur.execute("SELECT DesignId FROM Orders where OrderId=" + out)
        des_name = cur.fetchall()
        des_name = str(des_name).replace('(', '').replace(')', '').replace(',', '')
        if des_name:
            des_name = change_ID(int(des_name), "DesignID")
        print(des_name)
        herf = check_design(design, des_name)

        db.close()
        Info = "Printed at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template('PrintResult.html', labels=labels, content=content, Info=Info, herf=herf)


def job_status(sql):
    status = {'Done': 0,
              'Pending': 0,
              'OrdersDue': 0
              }
    today = datetime.date.today()

    for i in sql:
        if type(i['DueDate']) is datetime.date and i['DueDate'] >= today:
            if i["OrderStatus"] == "Done":
                status["Done"] += 1
            elif i["OrderStatus"] == "Pending":
                status["Pending"] += 1
            else:
                status["OrdersDue"] += 1
    return status


def check_status(orderdate, duedate):
    try:
        period = duedate - orderdate
        if period.days <= 1:
            status = '1-Urgent'
            return status
        elif 1 < period.days <= 3:
            status = '2-High'
            return status
        elif 3 < period.days <= 7:
            status = '3-Medium'
            return status
        else:
            status = '4-Low'
            return status
    except:
        status = "Wrong date"
        return status


def barData(data):
    barData = dict()
    keys = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i in data:
        if i['DueDate'] is not None and type(i['DueDate']) is datetime.date:
            d = i['DueDate']
            d = d.strftime("%b")
            s = round(i['TotalPrice'])
            if d in barData.keys():
                barData[d] += s
            else:
                barData[d] = s
    k = list(barData.keys())
    keys = list((set(keys).union(set(k))) ^ (set(keys) ^ set(k)))

    value = [barData[key] for key in keys]

    return keys, value


def connectdb():
    print('Creating Connection...')
    db = pymysql.connect(host="test.csxyg8gxd1zd.us-east-2.rds.amazonaws.com", user="admin", passwd="LYC438sby",
                         db="IT493", charset="utf8")
    print('Connect successfully ...')
    return db


def get_users(data):
    users = []
    a = 0
    names = locals()
    for i in data:
        names['user' + str(a)] = User(i["Username"], i["Password"], i["Authority"])
        users.append(locals()['user' + str(a)])
        a += 1
    return users


def get_dict_data_sql(sql):
    """
    运行sql语句，获取结果，并根据表中字段名，转化成dict格式（默认是tuple格式）
    """
    design = get_design()
    db = connectdb()
    cursor = db.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    fields = cursor.description
    db.close()
    cursor.close()
    index_dict = []  # 定义字段名的列表
    for i in fields:
        index_dict.append(i[0])
    res_out = []
    for d in data:
        res = dict()
        for i in index_dict:
            if i is str:
                res[i] = d[index_dict.index(i)]
            else:
                i = str(i)
                res[i] = d[index_dict.index(i)]
        for k in res.keys():
            if 'ID' in k:
                res[k] = change_ID(res[k], k)
        if 'DueDate' in res.keys() and 'OrderDate' in res.keys():
            if res['OrderStatus'] == "Done" or res['OrderStatus'] == "done":
                res['Priority'] = "Completed"
            else:
                res['Priority'] = check_status(res['OrderDate'], res['DueDate'])
        if 'DesignID' in res.keys():
            herf = check_design(design, res['DesignID'])
            res['design_herf'] = herf
            if herf != '#':
                res['Img_id'] = 'designId' + str(res['DesignID'])
            else:
                res['Img_id'] = 'No_design'
            # print(herf)
        res_out.append(res)
    return res_out


def get_design():  # get all designs in this file
    filePath = 'static\designs'
    d = os.listdir(filePath)
    print("Design Files: ", d)
    return d


def check_design(d, n):  # check if this design in this file and return path
    filePath = "static\designs\\"
    f = str(n) + ".jpg"
    for i in d:
        if f in d:
            return filePath + f
    return "#"


def get_table_names(db):  # Get all table names from database
    cursor = db.cursor()
    cursor.execute("show tables")
    table_list = [tuple[0] for tuple in cursor.fetchall()]
    db.close()
    return table_list


def change_ID(i, name):
    if "ID" in name and i is not None:
        new = (name[0:2]).upper()
        new += "%04d" % i
        return new
    else:
        return None


def insert(tablename, label=[], content=[]):
    sql = 'insert into {0} ({1},{2},{3},{4},{5}) values({6},"{7}","{8}","{9}","{10}")'.format(tablename, label[0],
                                                                                              label[1],
                                                                                              label[2], label[3],
                                                                                              label[4], content[0],
                                                                                              content[1], content[2],
                                                                                              content[3], content[4])
    con = connectdb()
    cur = con.cursor()
    result = cur.execute(sql)
    con.commit()
    con.close()
    return True if result else False


def openWeb():
    url = "http://127.0.0.1:5000/"
    webbrowser.open(url, new=0, autoraise=True)


UPLOAD_FOLDER = "/static/img/"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB


@app.route('/order_form', methods=["POST"])
def order_form():
    dataKeys = ['fName', 'lName', 'inputAddress', 'inputAddress2', 'inputCity', 'inputState', 'inputZip', 'inputEmail',
                'inputOrg', 'inputType', 'phone', 'Size', 'collapseTwo', 'Size_Y', 'Y_XS', 'Y_S', 'Y_M', 'Y_L',
                'Y_XL', 'Size_A', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', 'designHelp',
                'designDone', 'designFile', 'DesignF', 'orderChoice', 'art',
                'customFile_left_chest', 'customFile_full_chest', 'customFile_upper_back',
                'customFile_full_back', 'collapseThreeThree', 'customFile_right_sleeve', 'customFile_left_sleeve',
                'customFile_hat_front', 'customFile_hat_back', 'customFile_leg_left',
                'customFile_leg_right', 'order_date', 'due_date', 'quantity', 'pickUp', 'ship', 'comments']
    sizeKeys = ['Y_XS', 'Y_S', 'Y_M', 'Y_L', 'Y_XL', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL']
    dataDict = {}

    if request.method == "POST":
        for k in dataKeys:
            try:
                # dataDict[k] = request.form.get(k)
                if request.form.get(k) and request.form.get(k) != 'Choose...':
                    dataDict[k] = request.form.get(k)
                    print(request.form.get(k))
            except:
                # dataDict[k] = ""
                pass
    """img = request.files
    path = "/static/img/"
    file_path = path + img.filename
    img.save(file_path)"""
    print(dataDict)
    sizeInfo = ""
    total = 0
    for k in sizeKeys:
        if k in dataDict.keys():
            sizeInfo += k + ": " + dataDict[k] + '\n'
            total += int(dataDict[k])
    sizeInfo += "total: " + str(total)
    print(sizeInfo)
    cus_keys = ['fName', 'lName', 'inputAddress', 'inputAddress2', 'inputCity', 'inputState', 'inputZip', 'inputEmail',
                'inputOrg']
    if "inputAddress2" not in dataDict.keys():
        dataDict["inputAddress2"] = ""
    cus_sql = """INSERT INTO Customer(customerid, firstname, lastname, email, org_school, address, phonenum) 
    VALUES (null,'{0}','{1}','{2}','{3}','{4}','{5}');""".format(
        dataDict["fName"], dataDict["lName"], dataDict["inputEmail"], dataDict["inputOrg"],
        dataDict["inputAddress"] + "\n" + dataDict["inputAddress2"] + "\n" + dataDict[
            "inputCity"] + "\n" + dataDict["inputState"] + "\n" + dataDict["inputZip"],
        dataDict["phone"])
    print(cus_sql)
    db = connectdb()
    cur = db.cursor()
    cur.execute(cus_sql)
    cus_id = cur.lastrowid
    ord_sql = """
    INSERT INTO Orders(orderid, orderdate, duedate, totalprice, ordertype, orderstatus, customerid) 
    VALUES (null,'{0}','{1}',{2},'Printing','Pending',{3});
    """.format(dataDict["order_date"], dataDict["due_date"], total * 10, cus_id)
    cur.execute(ord_sql)
    ord_id = cur.lastrowid
    if not dataDict["comments"]:
        dataDict["comments"] = ''
    det_sql = """
    INSERT INTO Order_Detail(detailid, sizetable, orderid, extrainfo)
    VALUES (null,'{0}',{1},'{2}');
    """.format(sizeInfo, ord_id, dataDict["comments"])
    cur.execute(det_sql)
    print(det_sql)
    db.commit()
    db.close()
    send_email(dataDict["inputEmail"], str(dataDict),ord_id)
    flash('Submit successful! Confirm email has sent.', "success")

    return render_template('form.html')


# set mail information
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'excaliburye@gmail.com'
app.config['MAIL_PASSWORD'] = 'kzbyqqlptshpoojn'
mail = Mail(app)


def send_email(reci, content, OrderID):
    msg = Message('Order Confirmation!', sender='Excaliburye@gmail.com', recipients=[reci])
    msg.body = "Congratulations you've successfully placed an Order!\nYour OrderID: " + str(OrderID) + "\nOrder Information: " \
               + content
    mail.send(msg)
    return 'Mail sent'


# pyinstaller -F -i static/img/favicon.ico app.py
if __name__ == '__main__':
    openWeb()

    app.run(host='0.0.0.0', port=5000, debug=True)
