from libs import Flask, Response, make_response, render_template
import logic

app = Flask(__name__)
# Create endpoint to homepage
@app.route('/', methods=['GET'])
def home_page():
    response = make_response(render_template('home.html', foo=42))
    response.headers['X-Parachutes'] = 'parachutes are cool'
    return response
# Create endpoint to logic.py
@app.route('/api/data', methods=['GET'])
def get_data():
    result = logic.MakeMapImage()
    response_data = f"{result}"
    return Response(response_data, content_type='plain/text')

# Load server
if __name__ == '__main__':
    app.run(port=5005,debug=True)
