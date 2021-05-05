from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy


# creating app object
app = Flask(__name__)

# sample database, using SQLALCHEMY ORM
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# database schema
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=False, nullable=False)
    taskdetails = db.Column(db.String(500), unique=False, nullable=False)

    def __str__(self):
        return f'{self.username} : {self.id} >> {self.taskdetails}'
    
    def serialized(self):
        return {'user_name': self.username,
            'data': {
            'id': self.id,
            'task_content': self.taskdetails,
        }}

tasks = {'Probhakar': [
        {'id': 1,
        'task_content': 'attend meeting at 11:30'},
        {'id': 2,
        'task_content': 'call Parab for testing'}
    ],
    'Sammy':  [
        {'id': 3,
        'task_content': 'Complete Figma Mockup'},
        {'id': 4,
        'task_content': 'Androind testing with AVD'}
    ],
    'Akriti':  [
        {'id': 5,
        'task_content': 'Study global app trend'},
        {'id': 6,
        'task_content': 'meeting with soumen on REST API payload'},
        {'id': 7,
        'task_content': 'kafka broker down issue discussion'}
    ]}

@app.route('/')
def hello_world():
    should_show_alert = request.args.get('should_show_alert') or 'false'
    all_tasks = Task.query.all()
    processed_tasks = {}
    for each_task in all_tasks:
        serialized = each_task.serialized()
        if(serialized['user_name'] in processed_tasks):
            processed_tasks[serialized['user_name']].append(serialized['data'])
        else:
            processed_tasks[serialized['user_name']] = [serialized['data']]
    #print(processed_tasks)

    return render_template('index.html', tasks=processed_tasks, should_show_alert=should_show_alert)

@app.route('/addPerson', methods=['POST'])
def add_person():
    person_name = request.form['personName']
    task = request.form['taskName']
    print(person_name, task)

    result = Task.query.filter_by(username=person_name).all()
    if(len(result)>0):
        print('person already exists')
        return redirect(url_for('hello_world', should_show_alert='true'))
    else:
        db.session.add(Task(username=person_name, taskdetails=task))
        db.session.commit()

    return redirect(url_for('hello_world'))

@app.route('/deleteUser', methods=['POST'])
def delete_Person():
    person_name = request.form['personName']
    print(person_name)
    db.session.query(Task).filter(Task.username==person_name).delete()
    db.session.commit()
    return redirect(url_for('hello_world'))

@app.route('/moveTask', methods=['POST'])
def move_task():
    body = request.get_json()
    print(body)
    task_id = body['task_id']
    task = Task.query.filter_by(id=task_id).first()
    task.username = body['person_name']
    db.session.commit()
    return {'201': 'UPDATED'}

@app.route('/addTask', methods=['POST'])
def add_task():
    person_name = request.form['personName']
    task = request.form['taskName']
    print(person_name, task)
    db.session.add(Task(username=person_name, taskdetails=task))
    db.session.commit()
    return redirect(url_for('hello_world'))

if __name__ == '__main__':
    app.run(port=8080, debug=True)