from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import random
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import pytz
from flask_login import login_user, LoginManager, UserMixin, login_required, current_user, logout_user
import os
from flask_wtf import CSRFProtect
