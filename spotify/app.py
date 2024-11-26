from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/query", methods=["POST"])
def query():
    spotify_artist = request.form.get("spotify_artist")
    return f"You entered: {spotify_artist}"


if __name__ == "__main__":
    app.debug = True
    app.run()
