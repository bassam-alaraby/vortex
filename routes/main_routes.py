from flask import render_template

def register_main_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')
    
    @app.route("/size-guide")
    def size_guide():
        return render_template("size_guide.html")
