from flask import render_template
from flask_init import app

@app.route("/")
def hello_world():
    return render_template("index.html")


# # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run()
