import re
from flask import Flask, make_response, request, Response

app = Flask(__name__)

class BadRequest(KeyError):
    status_code = 403
    def __init__(self, message):
        super(BadRequest, self).__init__()
        self.message = message

@app.errorhandler(BadRequest)
def handle_missing_parameters(error):
    response = make_response(error.message)
    response.status_code = error.status_code
    return response

@app.route("/")
def homepage():
    return make_response("Welcome to a home page.")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method in ["GET"]:
        return "email and message fields are required"
    else:
        try:
            email = request.form["email"]
        except KeyError:
            raise BadRequest("email field is required")
        try:
            message = request.form["message"]
        except KeyEform:
            raise BadRequest("message field is required")

        if not re.compile('[\w.-]+@[\w.-]+').match(email):
            raise BadRequest("{email} is not a valid email address".format(
                email=email))
        return make_response("I got your message, thank you. Stay tune!")

if __name__ == "__main__":
    app.run(debug=True)
