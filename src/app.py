from flask import Flask, request, make_response
from flask_pymongo import PyMongo
from pymongo import MongoClient
import pandas as pd 

app = Flask(__name__)
app.config['MONGO_URI']='mongodb://localhost:27017/db_test'

cluster = MongoClient('atlas_url')
db = cluster["db_test"]
collection = db["users"]

mongo = PyMongo(app)



@app.route('/hello')
def hello():
    return 'hello'



@app.route('/users', methods=['POST'])
def create_user():
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    if username and email and password:
        id = collection.insert(
            {
                'username': username,
                'email': email, 
                'password': password
            }
        )
        response = {
            'id' : str(id),
            'username': username,
            'email': email
        }
        return response
    else: 
        return {'response': 'recieved'}


@app.route('/get-csv')
def get_csv():
    df = pd.DataFrame({
        'name': ['Raphael', 'Donatello'],
        'mask': ['red', 'purple'],
        'weapon': ['sai', 'bo staff']
        })    
    csv =  df.to_csv('turtles.csv')
    out = make_response(csv)
    out.headers["Content-Disposition"] = "attachment; filename=turtles.csv"
    out.headers["Content-type"] = "text/csv"
    return out




if __name__=="__main__":
    app.run(debug=True)