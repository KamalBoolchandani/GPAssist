# importing Flask and other modules
from flask import Flask, request, render_template 

import resources as resource

# Flask constructor
app = Flask(__name__)   
 
# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods =["GET", "POST"])
def gfg():
    return render_template("bot.html")

@app.route('/process', methods=['POST'])
def process():
    user_input = request.form.get('data')
    response = resource.chatbot_response(user_input)
    return response

if __name__=='__main__':
   app.run()