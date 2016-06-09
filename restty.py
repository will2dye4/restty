import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
	SQLALCHEMY_DATABASE_URI = "sqlite:///%s" % os.path.join(app.root_path, 'restty.db'),
	SECRET_KEY = 'development_key',
	USERNAME = 'admin',
	PASSWORD = 'default'
))
app.config.from_envvar('RESTTY_SETTINGS', silent = True)

db = SQLAlchemy(app)

class Command(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	command_name = db.Column(db.String, nullable=False)
	args = db.Column(db.String, nullable=True)

	def __repr__(self):
		return "<Command %r>" % self.command

@app.route("/")
def index():
	return str(Command.query.count())
