from sqlalchemy.orm import Session
from database import SessionLocal, engine
import proccess

import models, schemas
db = SessionLocal()
session = Session()
import time
import wget

#while True:
#    try:
#        result = db.query(models.PdfInfo).filter(models.PdfInfo.status =="In Proccess")
#        for row in result :
#            r=db.query(models.PdfInfo).filter(models.PdfInfo.id ==row.id).first()
#            r.status=None
#            db.commit()
#    except:
#        pass


#------------------------------------------------
#time.sleep(1)
print("Procceing......")
#try:
try:
    result = db.query(models.PdfInfo).filter(models.PdfInfo.status ==None)
    result = db.query(models.PdfInfo)

except:
    print('error')
#        continue
for row in result :
    row=result[0]
    r=db.query(models.PdfInfo).filter(models.PdfInfo.id ==row.id).first()
    r.status="In Proccess"
    db.commit()
    url_path=row.url
    if "http"==url_path[:4] or "ftp" == url_path[:3]:
        url="https://www.researchgate.net/profile/El_Habib_Benlahmar/publication/318723931_ETUDE_DE_LA_QUALITE_DE_SERVICE_DANS_LES_RESEAUX_VANET/links/5979d17f4585154d23be6d32/ETUDE-DE-LA-QUALITE-DE-SERVICE-DANS-LES-RESEAUX-VANET.pdf?origin=publication_detail"
        filename = wget.download(url,out="./check")
        url_path=filename
        
    try:
        proccess.check_file(db,url_path)
    except Exception as e:
        print(e)
        result = db.query(models.PdfInfo).filter(models.PdfInfo.url==url_path).first()
        result.status="Failed"
        db.commit()
#except KeyboardInterrupt:
#        break





#  import json

#             text_extract = json.loads(text_extract)

#             title=mstext_extractg['text'][0]["Title"]
#             drawing=text_extract['text'][0]["drawingN"]
#             revsion = text_extract['text'][0]["revsion"]