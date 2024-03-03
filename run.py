from app import create_app

# Start of the App
app = create_app()


# Routes
@app.route('/hw')
def hello_world():
    return 'Hello, World!'


# Run the App
if __name__ == '__main__':
    app.run(debug=True)