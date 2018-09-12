import os
from uuid import uuid4 as uuid
from threading import Thread
from time import sleep

import headless_pdfkit
import pyqrcode

def pdf_cleaner(pdfpath, sleepT=600):
    sleep(sleepT)
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
        'margin-right': '0.5in',
        'user-style-sheet': 'pdfstyle.css'
    }
    pdf_target = 'static/pdfs/'+id+'.pdf'
    genned_pdf = headless_pdfkit.generate_pdf(theString, options=pdfOptions)
    with open(pdf_target, 'w+b') as f:
        f.write(genned_pdf)
    for item in items:
        itemid = str(item.get('_id'))
        Thread(target=pdf_cleaner, args=(id+itemid+'.png',10)).start()
    Thread(target=pdf_cleaner, args=(pdf_target,)).start()
    return pdf_target
