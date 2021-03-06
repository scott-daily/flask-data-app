from flask import Flask, render_template, request, jsonify
from datetime import datetime
import joblib
import praw
import os

is_prod = os.environ.get('IS_HEROKU', None)

reddit = None

if is_prod:
    reddit = praw.Reddit(
        client_id=os.environ['CLIENT_ID'],
        client_secret=os.environ['CLIENT_SECRET'],
        password=os.environ['REDDIT_PASSWORD'],
        user_agent=os.environ['USER_AGENT'],
        username=os.environ['REDDIT_USERNAME'],
    )
else:
    reddit = praw.Reddit('sentimentBot')

app = Flask(__name__)

review_clf = joblib.load('review_clf.joblib')

# Use output.item() to convert from numpy int64 to native python int so it can be serialized to json for transmission.
@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.form['review']
    data_list = []
    data_list.append(data)
    prediction = review_clf.predict(data_list)
    output = prediction[0]
    sentiment_value = ''
    if (output.item() == 1):
        sentiment_value = 'Positive'
    else:
        sentiment_value = 'Negative'

    return render_template(
        "home.html",
        output=jsonify(sentiment_value)
    )

@app.route('/api/score', methods=['POST'])
def get_score():
    searchTerm = request.form['searchTerm']

    positive_count = 0
    negative_count = 0

    all = reddit.subreddit("all")

    for submission in all.search(searchTerm, limit=50):
        data_list = []
        data_list.append(submission.title)
        print("Post title: " + submission.title)
        prediction = review_clf.predict(data_list)
        output = prediction[0]
        if (output.item() == 1):
            positive_count += 1
        else:
            negative_count += 1

    return render_template(
        "home.html",
        positive_count=jsonify(positive_count),
        negative_count=jsonify(negative_count),
        search_term=jsonify(searchTerm)
    )

@app.route("/hello/")
@app.route("/hello/<name>")
def index(name = None):
    return render_template(
        "hello.html",
        name=name,
        date=datetime.now()
    )

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/signin', methods = ['POST','GET'])
def signin(wrongpw = None):
    if request.method == 'POST':
        if request.form['pw'] == 'test':
            return render_template('home.html')
        else:
            wrongpw = True
            return render_template(
                "login.html",
                wrongpw=wrongpw
            )

@app.route("/api/data")
def get_data():
    return app.send_static_file("cat.jpg")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/visuals/")
def visuals():
    return render_template("visuals.html")