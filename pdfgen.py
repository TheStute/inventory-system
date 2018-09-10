import os
from uuid import uuid4 as uuid
from threading import Thread
from time import sleep

import pdfkit
import pyqrcode

pdfconfig = pdfkit.configuration(wkhtmltopdf='xvfb-run wkhtmltopdf')

def pdf_cleaner(pdfpath):
    sleep(600)
    os.remove(pdfpath)

def PDFGen(items):
    id = str(uuid())
    theString = '''
    <head>
    <base href={}>
    </head>
    '''.format(os.getcwd()+'/')
    for item in items:
        itemid = str(item.get('_id'))
        url = pyqrcode.create(itemid)
        url.png(id+itemid+'.png', scale=8)
        theString = theString + '''
        <div class=label>
        <img src="{id}{itemid}.png">
        <h3>{name}</h3>
        <h6>Property of The Stute</h6>
        </div>
        '''.format(id=id, itemid=itemid, name=item.get('name'))
    pdfOptions = {
        'page-size': 'Letter',
        'margin-top': '0.5in',
        'margin-bottom': '0.5in',
        'margin-left': '0.5in',
        'margin-right': '0.5in'
    }
    pdfkit.from_string(theString, 'static/pdfs/'+id+'.pdf', css='pdfstyle.css', options=pdfOptions, configuration=pdfconfig)
    for item in items:
        itemid = str(item.get('_id'))
        os.remove(id+itemid+'.png')
    Thread(target=pdf_cleaner, args=('static/pdfs/'+id+'.pdf',)).start()
    return '/static/pdfs/'+id+'.pdf'
