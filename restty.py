import datetime
import json
import os
from subprocess import Popen, PIPE, STDOUT
from time import clock

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///%s' % os.path.join(app.root_path, 'restty.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=True,
    SECRET_KEY='development_key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('RESTTY_SETTINGS', silent=True)

db = SQLAlchemy(app)


class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command_name = db.Column(db.String)
    args = db.Column(db.String, nullable=True)
    start_time = db.Column(db.DateTime)
    execution_time = db.Column(db.Integer)
    result = db.Column(db.String)
    return_code = db.Column(db.Integer)

    def __init__(self, command_name, args=None):
        self.command_name = command_name
        self.args = args
        self.execute()

    def __repr__(self):
        return 'Command(command_name=%r,args=%r)' % (self.command_name, self.args)

    def execute(self):
        def _exec():
            args = self.command_name
            if self.args is not None:
                args += ' ' + self.args
            start = clock()
            process = Popen(args, stdout=PIPE, stderr=STDOUT, shell=True)
            stdout, _ = process.communicate()
            process.wait()
            end = clock()
            return stdout, process.returncode, end - start

        self.start_time = datetime.datetime.now()
        stdout, code, time = _exec()
        self.execution_time = time
        self.return_code = code
        self.result = stdout


@app.route('/')
def index():
    return str(Command.query.count())


@app.route('/exec', methods=['GET'])
def run():
    c = request.args.get('c')
    if ' ' in c:
        command_name, _, args = c.partition(' ')
        command = Command(command_name, args)
    else:
        command = Command(c)
    db.session.add(command)
    db.session.commit()
    # return json.dumps({'id': command.id, 'status': command.return_code, 'result': command.result})
    return command.result


@app.route('/history', methods=['GET'])
def history():
    return json.dumps([c.command_name for c in Command.query.order_by(db.desc('start_time')).all()])


if __name__ == '__main__':
    db.create_all()
    app.run()
