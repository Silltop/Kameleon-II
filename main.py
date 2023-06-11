from flask import render_template
from flask_init import app
import logging_setup


@app.route("/")
def hello_world():
    app.logger.info('hello there')
    variable = "HELLO THERE"
    return render_template("index.html", ala=variable)


# # Press the green button in the gutter to run the script.
if __name__ == '__main__':

    app.run()
