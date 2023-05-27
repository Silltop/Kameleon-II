from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run()
