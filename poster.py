#!/usr/bin/python
#https://raw.githubusercontent.com/paddywwoof/pi3d_book/master/programs/sprites01.py
from __future__ import absolute_import, division, print_function, unicode_literals

import pi3d
#import os
import sys

posterTex = "default.jpg"
fps = 30
logLevel = 'critical' #debug, info are used, warning, error & critical will disable logging
logFile = 'poster.log'
enKeyboard = 0

#cwd = os.getcwd()
cwd = "/home/pi/uberPoster"
logger = pi3d.Log(level=logLevel,file=cwd+"/"+logFile)
DISPLAY = pi3d.Display.create(background=(0.0, 0.0, 0.0, 1.0),frames_per_second=fps)
shader = pi3d.Shader("uv_flat")
CAMERA = pi3d.Camera(is_3d=False)
CAMERA.rotateZ(90)
tex1 = pi3d.Texture(cwd+"/"+posterTex)
z1 = 5.0 # z value of sprite1
a1 = 0.0 # alpha value of sprite1
alpha_delta = 0.05
sprite1 = pi3d.ImageSprite(tex1,shader=shader,w=DISPLAY.height, h=DISPLAY.width, z=z1)
sprite1.set_alpha(a1)

if enKeyboard == 1:
  keys = pi3d.Keyboard()

command = 1

####HTTP####
import socket
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p><b>Current Poster: </b>"+posterTex+"</p>", "utf-8"))
        self.wfile.write(bytes("<p><b>Current Command: </b>"+str(command)+"</p>", "utf-8"))
        self.wfile.write(bytes("<p><b>Current Rate: </b>"+str(round((1/alpha_delta)/fps,1))+"s</p>", "utf-8"))
        self.wfile.write(bytes("<br><p><b>Command Reference:</b></p>", "utf-8"))
        self.wfile.write(bytes("<p><b>cmd=0</b> will fade out the current poster</p>", "utf-8"))
        self.wfile.write(bytes("<p><b>cmd=1</b> will fade up the current poster</p>", "utf-8"))
        self.wfile.write(bytes("<p><b>rate=#</b> will set the fade rate in seconds to the value of #</p>", "utf-8"))
        self.wfile.write(bytes("<p><b>poster=filename.ext</b> will change the poster to the new filename (must be in uberPoster directory)</p>", "utf-8"))
        self.wfile.write(bytes("<p><b>quit=1</b> will quit uberPoster</p>", "utf-8"))
        self.wfile.write(bytes("<p>URL command string must begin with <b>?</b> and multiple commands must be separated with <b>&</b></p>", "utf-8"))

        self.wfile.write(bytes("<br><p><b>Sample Command:</b></p>", "utf-8"))
        self.wfile.write(bytes("<p>http://"+ip+":8000/?cmd=0&rate=5 will fade the poster out with a 5 second fade time", "utf-8"))
        self.wfile.write(bytes("<p>http://"+ip+":8000/?poster=2001ASO.jpg will switch the poster to an image named \"2001ASO.jpg\"</p>", "utf-8"))
       
        self.wfile.write(bytes("<br><p><a href=http://"+ip+":8000/?cmd=1"">Fade Up Current Poster</a></p>", "utf-8"))        
        self.wfile.write(bytes("<p><a href=http://"+ip+":8000/?cmd=0"">Fade Down Current Poster</a></p>", "utf-8"))        
#        self.wfile.write(bytes("<p><a href=http://"+ip+":8000/?cmd=0&poster=poster.jpg"">Change to Poster 1 in Black</a></p>", "utf-8"))        
#        self.wfile.write(bytes("<p><a href=http://"+ip+":8000/?cmd=0&poster=poster2.jpg"">Change to Poster 2 in Black</a></p>", "utf-8"))        
#        self.wfile.write(bytes("<p><a href=http://"+ip+":8000/?cmd=1&poster=poster.jpg"">Change to Poster 1, Alpha=1</a></p>", "utf-8"))        
#        self.wfile.write(bytes("<p><a href=http://"+ip+":8000/?cmd=1&poster=poster2.jpg"">Change to Poster 2, Alpha=1</a></p>", "utf-8"))        
        self.wfile.write(bytes("<br><p><a href=http://"+ip+":8000/""><b>REFRESH</b></a></p>", "utf-8"))        
        self.wfile.write(bytes("<br><p><a href=http://"+ip+":8000/?quit=1""><b>QUIT uberPoster</b></a></p>", "utf-8"))        


    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
#        logger.debug("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
#        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        
        if "?" in self.path :
           query = parse_qs(urlparse(self.path).query)
           if "cmd" in query:logger.info("Received command: %s",query['cmd'][0])
           if "rate" in query:logger.info("Received rate: %s",query['rate'][0])
           if "poster" in query:logger.info("Received poster: %s",query['poster'][0])
           global command
           global alpha_delta
           global sprite1
           global a1
           global posterTex
           if "poster" in query:
              if query['poster'][0] != posterTex:
                posterTex = query['poster'][0]
                sprite1 = pi3d.ImageSprite(cwd+"/"+posterTex,shader=shader,w=DISPLAY.height, h=DISPLAY.width, z=z1)
                if a1 <= 0:
                  sprite1.set_alpha(0.0)
                  a1 = 0.0                            
              logger.debug("Maybe loaded new image?")
              logger.debug("Current alpha: %f",a1)

           if "cmd" in query:
               if query["cmd"] == ['0']:
                  command = 0
                  logger.debug("Set: Command %s",command)
               if query["cmd"] == ['1']:
                  command = 1
                  logger.debug("Set: Command %s",command)
           if "rate" in query:
              alpha_delta = 1 / (float(query['rate'][0]) * fps)
              logger.debug("Rate now: %f", alpha_delta)
           if "quit" in query:
              logger.debug("Quit received")
              if query["quit"] == ['1']:
                DISPLAY.destroy()
                sys.exit(0)

    def log_message(self, format, *args):
        return
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip = s.getsockname()[0]
s.close()

logger.info("Starting server at: %s:8000",ip)
httpd = HTTPServer((ip, 8000), SimpleHTTPRequestHandler)
thread = threading.Thread(target=httpd.serve_forever)
thread.daemon = True
thread.start()

###END HTTP####


while DISPLAY.loop_running():
  sprite1.draw()
  if enKeyboard == 1:
    k = keys.read()
    if k > -1:
      if k == 27:
        logger.debug('Key received %s',chr(k))
        break
      elif k == ord('a'): # less solid sprite1
        a1 -= 0.05
      elif k == ord('d'): # more solid sprite1
        a1 += 0.05
        sprite1.set_alpha(a1)
      elif k == ord('u'): # more solid sprite1
        command=1
      elif k == ord('f'): # more solid sprite1
        command=2
      logger.debug('Key received %s',chr(k))

#Fade Up
  if command==1:
    if a1 < 1.0:
      a1 += alpha_delta
      sprite1.set_alpha(a1)
      sprite1.draw()
      logger.debug('Alpha=%f',a1)
#Fade Out
  if command==0:
    if a1 > 0.0:
      a1 -= alpha_delta
      sprite1.set_alpha(a1)
      sprite1.draw()
      logger.debug('Alpha=%f',a1)

    
if enKeyboard==1:keys.close()
DISPLAY.destroy()



