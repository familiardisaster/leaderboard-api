from flask import Flask, render_template,request, session, redirect, jsonify
from flask_session import Session
import os
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow

# Error handling for env vars
def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = f"Expected environment variable '{name}' not set."
        raise Exception(message)

# Must set env variables for system
SECRET_KEY = get_env_variable("SECRET_KEY")
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")

# Init app
app = Flask(__name__)

# Set secret key
app.secret_key = SECRET_KEY

# Db connection
DB_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}/{POSTGRES_DB}"
app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # silence the deprecation warning

# Init server-side sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Init db + marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Leaderboard Class/Model
class Leaderboard(db.Model):
  leaderboard_id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(20))
  points = db.Column(db.Integer())

  def __init__(self, name, points):
    self.name = name
    self.points = points

# Leaderboard Schema
class LeaderboardSchema(ma.Schema):
  class Meta:
    fields = ("leaderboard_id", "name", "points")

# Init leaderboard schema
leaderboard_schema = LeaderboardSchema(many = True)

# Create a leaderboard entry - must be authorized via session
@app.route("/api/leaderboard/new/", methods=["POST"])
def add_leader():
    if session["leader"]:
        name = request.json["name"]
        points = request.json["points"]

        new_leader = Leaderboard(name, points)

        db.session.add(new_leader)
        db.session.commit()

        return ("", 204)
    else:
        return ("Insufficent Authorization", 401)

# Get current leaderboard (top ten scores and names of those users) - No auth required
@app.route("/api/leaderboard/", methods=["GET"])
def get_leaders():
  all_leaders = Leaderboard.query.order_by(Leaderboard.points.desc()).limit(10)
  result = leaderboard_schema.dump(all_leaders)
  return jsonify(leaderboard = result)

if __name__ == '__main__':
    app.run()