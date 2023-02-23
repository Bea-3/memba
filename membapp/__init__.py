from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

#local imports 
#we want to make the object-based config available
from membapp import config

app = Flask(__name__,instance_relative_config=True)
#Initialize extension,this weillprotect ALL your post routes against csrf and you must pass the csrf token when submitting to these routes
csrf = CSRFProtect(app)

#load the config
#how to load from instance folder file
app.config.from_pyfile('config.py', silent=False)
#loading from object-based config that is within your package
app.config.from_object(config.LiveConfig)

db=SQLAlchemy(app)

#load the routes
from membapp import adminroutes,userroutes
