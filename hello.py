from flask import Flask, render_template


#Create a Flask istance
app = Flask(__name__)

#Create a route decorator
@app.route('/')
def index():
    first_name = "Yaroslaw"
    return render_template("index.html", first_name=first_name)
#def index():
#    return "<h1>Hello world</h1>"

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name = name)

#Create custom Error pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal server error thing
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.secret_key = 'secret123'
    app.run(debug=True)  