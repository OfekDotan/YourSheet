# import required libraries
from cgi import test
from operator import truediv
from unicodedata import name
import wave
import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv  
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, request, send_from_directory
import numpy as np
import librosa
import pandas as pd
from keras.models import load_model
from tensorflow.keras.utils import to_categorical
from midiutil import MIDIFile
from midi2audio import FluidSynth
import os
import dash_bootstrap_components as dbc
import sys

app = Flask(__name__, static_url_path="", static_folder="static")

app.config.from_object(__name__) # load config from this file , flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'app.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# Sampling frequency
freq = 44100
  
# Recording duration
duration1 = 5

samplingrate = 44100

noteNum= 105

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.info("test1")
    error = None
    isE=False
    if request.method == 'POST':
        username = request.form['username']
        db = get_db()
        cur = db.execute('select id, uPass from users WHERE users.username=?',(username,))
        rows = cur.fetchall() 
        if not len(rows):
            error = 'Invalid username or password'
            isE=True
        else:
            id = rows[0][0]
            uPass = rows[0][1]
            if  request.form['password'] != uPass:
                error = 'Invalid username or password'
                isE=True
        if not isE:
            session['logged_in'] = True
            session['user_id'] = id
            flash('You were logged in')
            return redirect(url_for('index'))
        
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', False)
    session.pop('user_id', None)
    flash('You are logged out')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cur = cursor.execute("select id from users WHERE username = ?",[username])
        if len(cur.fetchall()):
            error = "username is taken"
        else:
            sql = "INSERT INTO users(username, uPass) VALUES (?, ?)"
            newUser = (username, password)
            cursor.execute(sql, newUser)
            conn.commit()
            flash('registered succesfuly!')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


#Do register 
@app.route('/my-link/')
def my_link():
  # Start recorder with the given values 
  # of duration and sample frequency
  recording = sd.rec(int(duration1 * freq), 
                samplerate=freq, channels=2)

  # Record audio for the given number of seconds
  sd.wait()

  # This will convert the NumPy array to an audio
  # file with the given sampling frequency
  #write("recording0.wav", freq, recording)

  # Convert the NumPy array to audio file
  wv.write("recording1.wav", recording, freq, sampwidth=2)

  filesound ='recording1.wav'
  y, sr = librosa.load(filesound)

  fmin=librosa.note_to_hz('A1')
  C=np.abs(librosa.cqt(y,sr=44100,n_bins=104,bins_per_octave=48,norm=1,fmin=fmin)).transpose()

  print (C.shape)
  #change file name to other model
  filename = r"C:\Users\Ofek\Desktop\Python\Project\models\val016-train017moredata.h5"
  model_final = load_model(filename)

  prediction = model_final.predict(C)
  new_array = to_categorical(np.argmax(prediction, axis=1), 104)

  oneHot = new_array.transpose()

  print (oneHot.shape)

  samplingRate = 44100

  seconds = librosa.get_duration(filename = filesound)
  width = 100

  #print(seconds)

  track    = 0
  channel  = 0
  time     = 0    # In beats
  duration = 1    # In beats
  tempo    = 60*44   # In BPM
  volume   = 100  # 0-127, as per the MIDI standard


  MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
                          # automatically)
  MyMIDI.addTempo(track, time, tempo)
  start = 1
  for i in range(len(oneHot)):
      for j in range(len(oneHot[i])):
          if oneHot[i][j]==1 and oneHot[i][j-1]==0:
              start = round(j)
          elif oneHot[i][j]==0 and oneHot[i][j-1]==1:
              end = round(j)
              duration = round((end-start))
              if duration >0:
                  MyMIDI.addNote(track, channel, i, start, duration, volume)

  #print(tempo * seconds-1)
  #print(end)

  with open("major-scale.mid", "wb") as output_file:
      MyMIDI.writeFile(output_file)

  #fs = FluidSynth()
  #fs.midi_to_audio('D:\programing\Class\AI\project\website\major-scale.mid', 'output.wav')

  print ('I got clicked!')
  return render_template('show.html')


@app.route("/upload-wav", methods = ["GET", "POST"])
def upload_wav():
 # if not session.get('logged_in'):
 #   return redirect(url_for('login'))
  if request.method == 'POST':
    file = request.files['file']
    file.save(os.path.join("wavUploads/", file.filename))
    """ db = get_db()
    db.execute('insert into uploads (title, text) values (?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit() """
    return render_template("uploadWav.html", msg = "File uploaded successfully.")
  return render_template("uploadWav.html", msg = "")

@app.route("/uploads")
def uploads():
  files = os.listdir('wavUploads')
  return render_template('uploads.html', files=files)
  
@app.route('/getFile/<path:filename>')
def getFile(filename):
    path ='wavUploads'
    return send_from_directory(
        path,
        filename,
        as_attachment=True,
        mimetype='audio/wav'
    )

@app.route('/play/')
def play():
  #arr = os.listdir('.')
  #print(arr)

  #FluidSynth().play_midi('major-scale.mid')

    
  import pygame
  import pygame.mixer
  from time import sleep



  pygame.init()
  pygame.mixer.init()
  pygame.mixer.music.load("major-scale.mid")
  pygame.mixer.music.play()
  while pygame.mixer.music.get_busy():
      sleep(1)



  return render_template('show.html')



if __name__ == '__main__':
  app.run(debug=True)
  

  

  
  