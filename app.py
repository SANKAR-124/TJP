from flask import Flask, render_template,jsonify
import os



app=Flask(__name__)
app.secret_key="tja"

@app.route('/')
def home():
    return jsonify(message="hello")
if __name__=="__main__":
    app.run(debug=True)
