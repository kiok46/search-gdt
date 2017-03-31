from flask import Flask, request, g, render_template, Response
from flask import session, flash, redirect, url_for, make_response

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        search_string = request.form['search-string']
        return render_template('result.html', search_string=search_string)

    return render_template("index.html")


if __name__ == "__main__":
    app.run()
