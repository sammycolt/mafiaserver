from app import app

@app.route('/')
def api_root():
    return "Welcome"

@app.route('/api')
def api_api():
    return "Welcome to API"
