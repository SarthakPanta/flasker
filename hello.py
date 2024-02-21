from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def hello():
    first_name = 'sarthak'
    stuff = "this is <strong>Bold</strong> Text"

    brand = ["honda", "huyndia", 45]
    return render_template('index.html', first_name=first_name, stuff=stuff, brand=brand)

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)


#create custom error pages

#Invalid URL

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404 

#Internal server error

@app.errorhandler(500)
def page_not_found(e):
	return render_template('500.html'), 500





