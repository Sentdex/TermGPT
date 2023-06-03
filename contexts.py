TERMINAL_COMMANDS = [  
{"role": "user", "content": 'Given text input from a user looking to do programming, help to build a series of console commands that will achieve the goals of the prompt. Your responses will be one command at a time, where each response is JUST the command and nothing else. When ready for the next command, the user will say "NEXT" and you will respond with the next command. When we have reached the end of console commands, respond with "DONE" and then you will do it again with some new input from the user. If you understand, say "OK."'},
{"role": "assistant", "content": "OK."},
{"role": "user", "content": "NEW STARTING INPUT: show me a basic flask web dev example with templates?"},
{"role": "assistant", "content": "pip install flask"},
{"role": "user", "content": "NEXT"},
{"role": "assistant", "content": "mkdir basic_flask_app"},
{"role": "user", "content": "NEXT"},
{"role": "assistant", "content": '''cat << 'EOF' > basic_flask_app/app.py
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
EOF'''},
{"role": "user", "content": "NEXT"},

{"role": "assistant", "content": "mkdir basic_flask_app/templates"},
{"role": "user", "content": "NEXT"},


{"role": "assistant", "content": '''cat << EOF > basic_flask_app/templates/index.html
<!DOCTYPE html>
<html>
<head>
    <title>My Flask App</title>
</head>
<body>
    <h1>Welcome to My Flask App</h1>
    <p>This is the home page!</p>
</body>
</html>
EOF'''},
{"role": "user", "content": "NEXT"},


{"role": "assistant", "content": '''cat << 'EOF' > basic_flask_app/templates/about.html
<!DOCTYPE html>
<html>
<head>
    <title>About My Flask App</title>
</head>
<body>
    <h1>About My Flask App</h1>
    <p>This is a simple Flask app that demonstrates the use of templates!</p>
</body>
</html>
EOF
'''},
{"role": "user", "content": "NEXT"},
{"role": "assistant", "content": "python basic_flask_app/app.py"},
{"role": "user", "content": "NEXT"},
{"role": "assistant", "content": "DONE"}]
