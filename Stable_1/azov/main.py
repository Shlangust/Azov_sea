from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/nigger",methods=["POST"])
def nigger():
    ser = request.form.get('ser')
    return render_template('result.html',ser=ser)


if __name__ == "__main__":
    app.run(debug=True)