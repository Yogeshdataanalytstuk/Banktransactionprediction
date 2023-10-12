import numpy
from flask import Flask, request, render_template
import pickle
import pandas as pd
import csv 

app = Flask(__name__)

model = pickle.load(open('model/Model_ml.pkl', 'rb'))
type_model=pickle.load(open('model/Model_class_ml.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    df = pd.DataFrame({
        'typeofaction': [1 if request.form['typeofaction'] == "cash-in" else 0],
        'sourceid': [int(request.form['sourceid'])],
        'destinationid': [int(request.form['destinationid'])],
        'amountofmoney': [float(request.form['amountofmoney'])]
        
    })
    
    prediction = model.predict(df)
    prediction_text = "Not Fraud" if prediction[0] == 0 else "Fraud"
    if prediction_text=='Fraud':
        df['isfraud']=1
    if prediction_text=='Not Fraud':
        df['isfraud']=0
        
    print(df)
    if prediction_text == "Fraud":
        print('Fraud')
        prediction_text += str(type_model.predict(df))
    type_mapping = {"['type3']": 'Type3',"['type2']": 'Type2',"['type1']": 'Type1'}
    with open('data/banktransaction.csv', 'a', newline='') as csvfile:
        fieldnames = ['typeofaction','sourceid', 'destinationid', 'amountofmoney','isfraud','typeoffraud']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'typeofaction':'cash-in' if df['typeofaction'].values[0] == 1 else 'transfer','sourceid': df['sourceid'].values[0], 'destinationid': df['destinationid'].values[0], 
                         'amountofmoney': df['amountofmoney'].values[0], 'isfraud':df['isfraud'].values[0],'typeoffraud': 'none' if df['isfraud'].values[0] == 0 else type_mapping.get(type_model.predict(df), "Unknown Type")})



    return render_template('index.html', prediction_text=f'{prediction_text}')
@app.route('/feedback', methods=['POST'])
def feedback():
    fd = pd.DataFrame({
        'feedback': [1 if request.form['typeofaction'] == "Not-Fraud" else 'Fraud'],
        'sourceid': [int(request.form['sourceid'])],
        'destinationid': [int(request.form['destinationid'])]})  
    with open('data/Feedback.csv', 'a', newline='') as csvfile:
        fieldnames = ['sourceid', 'destinationid', 'feedback']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'sourceid': fd['sourceid'].values[0], 'destinationid': fd['destinationid'].values[0], 'feedback': fd['feedback'].values[0]})


    return render_template('index.html')
if __name__ == "__main__":
    app.run()
