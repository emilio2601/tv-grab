#!flask/bin/python
import multiprocessing
import subprocess
import datetime
import shutil
import time
import app



def set_up_recording(rec):
    if rec.tunerID == 1: #That's you, Hauppauge 950Q
        if rec.format == "raw":
            title = rec.title.replace(" ", "_") + ".ts"
            print("Recording {}".format(title))

            adapter = multiprocessing.Process(target=azap, args=(rec.channel,))
            adapter.start()  #At this point, we've set up the adapter but haven't started recording

            recorder = multiprocessing.Process(target=record, args=("/dev/dvb/adapter0/dvr0", title))
            recorder.start()

            time.sleep(rec.duration + 1)

            recorder.terminate()
            adapter.terminate()

            print("Recorded {}".format(title))

            shutil.move(title, "client/recordings/{}".format(title))
            print("File moved {}".format(title))

            rec.done = True
            rec.download_url = "/recordings/{}".format(title)
            app.db.session.commit()
            
            print("Finished recording {}".format(title))
            return
        elif rec.format == "mp4": #Pretty sure the Raspberry Pi can't handle it, so not implemented for the moment
            pass
        elif rec.format == "mkv": #Ditto
            pass

def azap(channel):
    subprocess.call(["azap", "-r", channel], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def record(route, output):
    subprocess.call(["cp", route, output], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

if __name__ == '__main__':
    print("Started scheduler")
    while True:
        time.sleep(1)
        recordings = app.Recording.query.all()
        pending_recs = [rec for rec in recordings if not rec.done]
        pending_recs = sorted(pending_recs, key=lambda r: r.date_start)

        now = datetime.datetime.now()
        margin_for_deletion = datetime.timedelta(days=3)
        margin_for_recording = datetime.timedelta(seconds=10)
        for rec in pending_recs:
            if rec.date_start + margin_for_deletion < now: #If recording is pending and a day has passed delete it.
                print("Deleting {}".format(rec))
                app.db.session.delete(rec)
                app.db.session.commit()

            if now - margin_for_recording <= rec.date_start <= now + margin_for_recording:
                set_up_recording(rec)
