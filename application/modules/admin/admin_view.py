from application import app

@app.route("/admin")
def admin():
    return "This is admin page."

