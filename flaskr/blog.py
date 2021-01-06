import os
import shutil
import time
import random
from shutil import copyfile

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask import current_app as app
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
import numpy as np
import imageio
from . import celery

#from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.STROTSS.styleTransfer import run_st
#from . import celery

bp = Blueprint('blog', __name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg','JPG','PNG','JPEG'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(f, field='File', style=False, username=None, landing=False):
    error = None
    if not f:
        error = field+' is required.'

    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        filename_rec = ''

        if style:
            filename = username+"_s_"+filename
            filename_rec = username+"_recent_s."+filename.split('.')[-1]
        else:
            filename = username+"_c_"+filename
            filename_rec = username+"_recent_c."+filename.split('.')[-1]


        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        for ext in list(ALLOWED_EXTENSIONS):
            fn = filename_rec.split('.')[0]+'.'+ext
            full_fn = os.path.join(app.config['UPLOAD_FOLDER'],fn)
            if os.path.exists(full_fn):
                os.remove(full_fn)

        copyfile(os.path.join(app.config['UPLOAD_FOLDER'], filename),os.path.join(app.config['UPLOAD_FOLDER'], filename_rec))

    return error, filename

@bp.route('/', methods=('GET', 'POST'))
def land():

    ip = str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)).replace('.','')

    if request.method == 'POST':
        contentWeight = float(request.form['contentWeight'])/4.0

        style_default = 'generic_s.jpg'
        content_default = 'generic_c.png'

        styleName = ''
        contentName = ''

        error = None

        if 0:
            style = request.files['styleName']
            error, styleName = upload_file(style, 'Style Image',style=True, username=ip, landing=True)

            content = request.files['contentName']
            error, contentName = upload_file(content, 'Content Image', username=ip, landing=True)

        else:
            try:
                style = request.files['styleName']
                error, styleName = upload_file(style, 'Style Image',style=True, username=ip, landing=True)
            except:
                error = None
                styleName = style_default
                for ext in list(ALLOWED_EXTENSIONS):
                    filename = os.path.join(app.config['UPLOAD_FOLDER'], ip+"_recent_s."+ext)
                    if os.path.isfile(filename):
                        styleName = filename.split('/')[-1]

            try:
                content = request.files['contentName']
                error, contentName = upload_file(content, 'Content Image', username=ip, landing=True)
            except:
                error = None
                contentName = content_default

                for ext in list(ALLOWED_EXTENSIONS):
                    filename = os.path.join(app.config['UPLOAD_FOLDER'], ip+"_recent_c."+ext)
                    if os.path.isfile(filename):
                        contentName = filename.split('/')[-1]

        if error is not None:
            flash(error)
        else:

            shutil.copyfile('./output_ims/qmark.png', './output_ims/'+str(ip).zfill(8)+'.png')

            run_styleTransfer.delay(styleName,contentName,contentWeight,ip)

        return render_template('landing.html', ip_path=ip, ip_path_c=contentName+'?rand=' + str(random.random())[2:], ip_path_s=styleName+'?rand=' + str(random.random())[2:])


    return render_template('landing.html', ip_path='generic', ip_path_c='generic_c.png', ip_path_s='generic_s.jpg')

@celery.task
def run_styleTransfer(style, content, contentWeight, output_id):

    style_path = './uploaded_ims/'+style
    content_path = './uploaded_ims/'+content

    try:
        regions = [[imageio.imread(content_path)[:,:,0]*0.+1.], [imageio.imread(style_path)[:,:,0]*0.+1.]]
    except:
        regions = [[imageio.imread(content_path)[:,:]*0.+1.], [imageio.imread(style_path)[:,:]*0.+1.]]

    run_st(content_path, style_path, contentWeight*16.0, 5, 0., False, regions, output_path='./output_ims/'+str(output_id).zfill(8)+'.png')

    return True

