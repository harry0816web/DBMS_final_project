from flask import Flask,request,render_template,redirect,session

# init flask
app = Flask(__name__,
            static_folder='static',
            static_url_path='/',
            template_folder='templates'
            )
app.secret_key = '1234567890'

# router
@app.route('/')
def index():return redirect('/login')
    
# test database
# user dictionary to store user data
user_data = [
    {'username':'test','password':'test'},
    {'username':'elle','password':'1114'}
]

# register
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']
        # 將資料寫入資料庫
        user_data.append({'username':username,'password':password})
        print(user_data)
        return redirect('/login')
    
# login
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        print(username,password)
        if {'username':username,'password':password} in user_data:
            print('登入成功')
            session['user'] = username
            return redirect('/main_page')
        return render_template('login.html',login_error=True)

# main page
@app.route('/main_page')
def main_page():
    user = session['user']
    return render_template('main_page.html',user=user)

# run server
if __name__ == '__main__':
    app.run(debug=True,port=5001)

