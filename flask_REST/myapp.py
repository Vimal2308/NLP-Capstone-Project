import pickle
from flask import Flask, request, jsonify
import helper

app = Flask(__name__)

# app.debug = True
class PrefixMiddleware(object):
    # class for URL sorting
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        # in this line I'm doing a replace of the word flaskredirect which is my app name in IIS to ensure proper URL redirect
        if environ['PATH_INFO'].lower().replace('/greatlearning', '').startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'].lower().replace('/greatlearning', '')[len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ["This url does not belong to the app.".encode()]

app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/')

model = pickle.load(open('auto_ticket_assignment.pkl','rb'))

@app.route('/predict',methods=['POST'])
def predict():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    # Make prediction using model loaded from disk as per the data.
    description = [[data['description']]]
    description = helper.clean_text(description)
    description = helper.pre_process(description)
    prediction = model.predict(description)
    print(prediction)
    output = prediction[0]
    return jsonify(int(output))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9010)