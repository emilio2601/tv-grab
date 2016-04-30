#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
import datetime
import sys



app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    tunerID = db.Column(db.Integer)
    date_start = db.Column(db.DateTime)
    date_end = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    channel = db.Column(db.String(60))
    done = db.Column(db.Boolean)
    download_url = db.Column(db.String(120))
    format = db.Column(db.String(4))

    def __init__(self, title, tunerID, date_start, duration, channel, format):
        self.title = title
        self.tunerID = tunerID
        self.date_start = date_start
        self.date_end = date_start + datetime.timedelta(seconds=duration)
        self.duration = duration
        self.channel = channel
        self.format = format
        self.done = False
        self.download_url = ""

    def __repr__(self):
        return "{0}: {1}-{2}".format(self.title, self.date_start, self.date_end)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "tunerID": self.tunerID,
            "date_start": dump_datetime(self.date_start),
            "date_end": dump_datetime(self.date_end),
            "duration": self.duration,
            "channel": self.channel,
            "done": self.done,
            "download_url": self.download_url,
            "format": self.format
        }



@app.route('/radio/api/v1/schedule', methods=["GET"])
def list_schedule():
    """Return a JSON array with all the scheduled recordings"""
    return jsonify({"recordings" : [x.serialize() for x in Recording.query.all()]})


@app.route("/radio/api/v1/schedule/<int:rec_id>", methods=["GET"])
def return_schedule(rec_id):
    """Return a JSON object with the specified ID"""
    return jsonify(Recording.query.get_or_404(rec_id).serialize()) 
    

@app.route("/radio/api/v1/schedule", methods=["POST"])
def add_schedule():
    """Schedule a recording with the user provided data via POST"""
    rec = validate_user_input(request)
    db.session.add(rec)
    try:
        db.session.commit()
        return jsonify(rec.serialize()), 201
    except Exception:
        return jsonify({"error": "Unique constraint failed"})

    

@app.route("/radio/api/v1/schedule/<int:rec_id>", methods=["PUT"])
def update_schedule(rec_id):
    """Replace the specified recording with the user provided data via POST"""
    rec = validate_user_input_update(request, Recording.query.get_or_404(rec_id))
    db.session.delete(Recording.query.get_or_404(rec_id))
    db.session.add(rec)
    try:
        db.session.commit()
        return jsonify(rec.serialize())
    except Exception:
        return jsonify({"error": "Unique constraint failed"})


@app.route("/radio/api/v1/schedule/<int:rec_id>", methods=['DELETE'])
def delete_schedule(rec_id):
    """Delete the object with specified ID"""
    db.session.delete(Recording.query.get_or_404(rec_id))
    db.session.commit()
    return jsonify({"msg": "Successful"})

def validate_user_input(post_data):
    """Validate the user provided data via POST request and build a Recording object"""
    if not post_data.json: abort(400)
    else:
        if not "date_start" in post_data.json or not "title" in post_data.json or not "duration" in post_data.json or not "channel" in post_data.json:
            abort(400)
        else:
            title = post_data.json["title"]
            duration = post_data.json["duration"]
            date_start = datetime.datetime.strptime(post_data.json["date_start"][0] + " " + post_data.json["date_start"][1], "%Y-%m-%d %H:%M:%S")
            if date_start < datetime.datetime.now():
                abort(400)
            channel = post_data.json["channel"]
            format = post_data.json.get("format", "raw")
            tunerID = post_data.json.get("tunerID", 1)
            return Recording(title, tunerID, date_start, duration, channel, format)
        
def validate_user_input_update(post_data, existing):
    if not post_data: abort(400)
    else: 
        if "date_start" in post_data.json:
            date_start = datetime.datetime.strptime(post_data.json["date_start"][0] + " " + post_data.json["date_start"][1], "%Y-%m-%d %H:%M:%S")
        else:
            date_start = existing.date_start

        if date_start < datetime.datetime.now():
                abort(400)

        title = post_data.json.get("title", existing.title)
        format = post_data.json.get("format", existing.format)
        tunerID = post_data.json.get("tunerID", existing.tunerID)
        channel = post_data.json.get("channel", existing.channel)
        duration = post_data.json.get("duration", existing.duration)
        done = post_data.json.get("done", existing.done)
        download_url = post_data.json.get("download_url", existing.download_url)
        rec = Recording(title, tunerID, date_start, duration, channel, format)
        rec.id = existing.id
        rec.done = done
        rec.download_url = download_url
        return rec

 
if __name__ == '__main__':
    app.run(debug=True, port=5000)