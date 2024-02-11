from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/nigger",methods=["POST"])
def nigger():
    ser = request.form.get('ser')
    return render_template('result.html',ser=ser)
    # def search():



@app.route('/test',methods=["POST","GET"])
def map():
    marker_coords = [0, 0]
    marker_text = "asd"
    return render_template('test.html', marker_coords=marker_coords, marker_text=marker_text)


if __name__ == "__main__":
    app.run(debug=True)