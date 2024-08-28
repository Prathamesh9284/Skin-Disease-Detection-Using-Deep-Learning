import base64
from io import BytesIO
import secrets
import os
from flask import Flask, render_template, redirect, request, session, url_for, flash,jsonify
from pymongo import MongoClient
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin,current_user
from bson import ObjectId
from PIL import Image
import numpy as np
import tensorflow as tf

app = Flask(__name__)

#sdfshh
# Generate a secure secret key
secret_key = secrets.token_hex(16)

# Set the secret key securely from environment variable or fallback to a default value
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secret_key)

client = MongoClient('mongodb://localhost:27017/')
db = client['SkinDisease']
users = db['users']
skinDisease = db['skinDiseases']

login_manager = LoginManager()
login_manager.init_app(app)

def int_to_str(value):
    return str(value)

app.jinja_env.filters['int_to_str'] = int_to_str

class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        return str(self.username)    

# Load user from database
@login_manager.user_loader
def load_user(username):

    user_data = users.find_one({'username': username})
    if user_data:
        return User(user_data['username'])
    else:
        return None
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']

        

        if users.find_one({'username': username}):
            flash('Username already taken. Please choose a different username.', 'error')
            return redirect(url_for('signup'))

        new_user = {
            'firstname': firstname,
            'lastname': lastname,
            'username': username,
            'email': email,
            'password': password,
            'mobile': mobile
        }
        users.insert_one(new_user)
        flash('Signup successful. You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user_data = users.find_one({'username': username, 'password': password})

        if user_data:
            user = User(user_data['username'])
            
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/',methods=['GET','POST'])
def first():
    return render_template('login.html')

@app.route('/index',methods=['GET','POST'])
def home():
    if current_user.is_authenticated:  # Check if the user is authenticated
        # user_data = users.find_one({'username': current_user.username})

        
        return render_template('index.html')

    return render_template('index.html')

@app.route('/upload',methods=['GET','POST'])
def upload():
    if current_user.is_authenticated:  # Check if the user is authenticated
        None
        return render_template('upload.html')
    
@app.route('/analyze',methods=['GET','POST'])
def analyze():
    if current_user.is_authenticated:  # Check if the user is authenticated
        None
    
    return render_template('analyze.html')


dict = {0: 'cellulitis', 1: 'impetigo', 2: 'Athletes Foot', 3: 'Nail Fungus', 4: 'ringworm', 5: 'Cutaneous Larva Migrans', 6: 'chickenpox',7:'measles',8:'monkeypox' , 9: 'shingles'}

@app.route('/predict',methods=['GET','POST'])
def predict():
    if current_user.is_authenticated:  # Check if the user is authenticated
        # user_data = users.find_one({'username': current_user.username})
        # user_data = users.find_one({'username': current_user.username})
        file = None
        if 'file' in request.files:
            file = request.files['file']
            if file:

                img = Image.open(file)
                
                # Resize the image (example: resize to 100x100 pixels)
                resized_img = img.resize((256, 256))
                
                # Convert the image to a NumPy array
                img_array = np.array(resized_img)
                img_array = np.expand_dims(img_array,axis=0)        
                print(img_array)

                model = tf.keras.models.load_model(r'D:\Skin Disease Ai\model.h5')
                prediction = model.predict(img_array)
                
                predicted_class = dict[np.argmax(prediction)]
                print(predicted_class)
                return jsonify({'predicted_class': predicted_class})
            

        

        # Check if the file is empty
        # if file.filename == '':
        #     # return 'No selected file'
        #     a = 1

        # If the file exists and is allowed, process it
        
        
        predictedDisease = request.form['predictField']
        print(predictedDisease)
        data = skinDisease.find_one({'name':predictedDisease})
        # print(data['name'])
        print(data)
        return render_template('predict.html',data=data)

@app.route('/predict2',methods=['GET','POST'])
def predict2():
    if current_user.is_authenticated:  # Check if the user is authenticated
        image_data_url = request.form['image']
        
        encoded_image = image_data_url.split(',')[1]
        
        # Decode the base64 encoded image data and create a PIL Image object
        img = Image.open(BytesIO(base64.b64decode(encoded_image)))
        
        # Resize the image (example: resize to 256x256 pixels)
        resized_img = img.resize((256, 256))
        
        # Convert the image to a NumPy array
        img_array = np.array(resized_img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Load the trained model
        model = tf.keras.models.load_model(r'D:\Skin Disease Ai\model.h5')
        
        # Perform prediction on the image array
        prediction = model.predict(img_array)
        
        # Get the predicted class
        predicted_class = dict[np.argmax(prediction)]
        
        return jsonify({'predicted_class': predicted_class})
        
    
    return render_template('predict2.html')







if __name__ =='__main__':
    app.run(debug=True,port=5001)