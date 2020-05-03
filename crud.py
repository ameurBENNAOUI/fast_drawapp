from sqlalchemy.orm import Session

import models, schemas

from passlib.context import CryptContext
from proccess import get_first_info

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_context.verify(plain_password, hashed_password)
def create_user(db: Session, user: schemas.UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    print('-------------'+user.password+'----------')
    hashed_password=pwd_context.hash(user.password)
    a=verify_password(user.password, hashed_password)
    
    print(a,"..........",hashed_password)

    # hashed_password=pwd_context.hash(user.password)
    # print("..........",hashed_password)
#    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email,name=user.name,hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item





def create_template(db: Session,item: schemas.TemplateCreate, user_id: int):
    # db_item=db.query(models.Template).filter(models.User.id == user_id).first()
    db_item = models.Template(**item.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return schemas.R_TemplateCreate(id=db_item.id)

def update_template(db: Session,item: schemas.TemplateCreate,template_id:int, user_id: int):
    db_item=db.query(models.Template).filter(models.Template.id == item.id).first()

#    db_item.user_id=user_id
    for i in item.dict():
#        print("...........================",item.id,"=====..",item.dict()[i],item.dict())
        setattr(db_item,i,item.dict()[i])

    
    db.commit()
    db.refresh(db_item)
    print(db_item)
    
    get_first_info(item)
    return db_item
import os

def delete_template(template_id:int,db: Session):
    db_item=db.query(models.Template).filter(models.Template.id == template_id).first()
    
    paths=["template_cropped_img_200","template_cropped_img_300","template_img_200","template_img_300","template_pdf","template_cropped_img_200","template_cropped_img_300"]
    
    for path in paths:
        try:
            if path=="template_pdf":
                filename=os.getcwd()+"\\static\\"+str(path)+"\\"+str(db_item.name)+".pdf"
            else:
                filename=os.getcwd()+"\\static\\"+str(path)+"\\"+str(db_item.name)+".jpg"
            os.remove(filename)
        except:
            print(filename)

    db.delete(db_item)
    db.commit()
    # db.refresh(db_item)
    return schemas.TemplateDelete(status=True)

def get_tmp(db: Session, template_id: int):
    
    tmp= db.query(models.Template).filter(models.Template.id == template_id).first()
    # a= {"id: ":tmp.id, "name:":tmp.name, "json_data:":tmp.json_data,"template_path: ":tmp.template_path,"user_id: ":tmp.user_id}
    # print(str(a))
    # import json
    # y = json.dumps(tmp.json_data)
    # print(y)
    return tmp    
def tmps(db: Session):
    
    tmps= db.query(models.Template).all()
    
    list_=[]
    for tmp in tmps:
        # a= schemas.TemplateDetail(id=tmp.id,name=tmp.name,json_data=tmp.json_data,template_path=tmp.template_path)
        list_.append(tmp)
        
    tmps_schema= schemas.TemplatesDetail(templates=list_)
    # print(str(a))
    # import json
    # y = json.dumps(tmp.json_data)
    # print(y)
    return tmps_schema    

# Queue 

def create_queue(db: Session,item: schemas.Create_Queue, user_id: int):
    db_item = models.Queue(name=item.name, user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return schemas.R_Create_Queue(id=db_item.id)
    
def get_queues(db: Session,user_id:id):
    queues= db.query(models.Queue).filter(models.Queue.user_id == user_id)
    q_list = []
    for queue in queues:
        # print(queue.id,queue.name)
        q=schemas.Get_Queue(id=queue.id,name=queue.name)
        q_list.append(q)
    Queues=schemas.Get_Queues(Queues=q_list)

    return Queues
def get_queue(db: Session,user_id:id,queue_id:id):
    queue= db.query(models.Queue).filter(models.Queue.user_id == user_id).filter(models.Queue.id == queue_id).first()
    return schemas.Get_Queue(id=queue.id,name=queue.name)

def delete_queue(db: Session,queue_id:id):
    db_item=db.query(models.Queue).filter(models.Queue.id == queue_id).first()

    db.delete(db_item)
    db.commit()

    return schemas.QueueDelete(status=True)


def create_pdf(db: Session,url:str ,user_id: int,queue_id=int):

    db_item = models.PdfInfo(queue_id=queue_id,user_id=user_id,url=url)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return schemas.R_PDF(id=db_item.id) 

def delete_pdf(db: Session,user_id: int,pdf_id=int):
    db_item=db.query(models.PdfInfo).filter(models.PdfInfo.id == pdf_id).first()

    db.delete(db_item)
    db.commit()
    return schemas.R_Delete_PDF(status=True)

    

def get_pdfs(db: Session,user_id:id,queue_id:id):
    if queue_id==0:
        queues= db.query(models.PdfInfo).filter(models.PdfInfo.user_id == user_id)
    else:
        queues= db.query(models.PdfInfo).filter(models.PdfInfo.queue_id == queue_id).filter(models.PdfInfo.user_id == user_id)



    q_list = []
    for queue in queues:
        q_name= db.query(models.Queue).filter(models.Queue.id == queue.queue_id).first()

        print("-------------------",queue.id)
        print("-------------------",q_name.name)
        print("-------------------",queue.extracted_data)

        q=schemas.PDF(id=queue.id,
            queue_name=q_name.name,
            queue_id=queue.queue_id,
            user_id=queue.user_id,
            url=queue.url,
            status=queue.status,
            extracted_data=queue.extracted_data,
            score=queue.score,
            feedback_user=queue.feedback_user)
            # print(queue.id,queue.name)
            # q=schemas.Get_Queue(id=queue.id,name=queue.name)
        q_list.append(q)
    PDFs=schemas.PDFs(Queues=q_list)

    return PDFs

def get_pdf(db: Session,user_id:id,queue_id:id,pdf_id:id):
    queue= db.query(models.PdfInfo).filter(models.PdfInfo.queue_id == queue_id).filter(models.PdfInfo.user_id == user_id).filter(models.PdfInfo.id==pdf_id).first()
    q=schemas.PDF(id=queue.id,
        queue_id=queue.queue_id,
        user_id=queue.user_id,
        url=queue.url,
        status=queue.status,
        extracted_data=queue.extracted_data)
    return q

def feedback_pdf(db: Session,user_id:id,queue_id:id,pdf_id:id,item: schemas.Feedback):
    pdf= db.query(models.PdfInfo).filter(models.PdfInfo.id == pdf_id).filter(models.PdfInfo.user_id == user_id).first()
    # print("----------",item.feedback)
    pdf.feedback_user=item.feedback
    print("----------",pdf.feedback_user)
    db.commit()
    db.refresh(pdf)
    
    # get_first_info(item)
    return pdf
from fastapi.responses import FileResponse
import json
from pyexcel_io import save_data
# def convert_to_csv(db: Session,user_id:id,queue_id:id):
#     if queue_id==0:
#         queues= db.query(models.PdfInfo).filter(models.PdfInfo.user_id == user_id)
#     else:
#         queues= db.query(models.PdfInfo).filter(models.PdfInfo.queue_id == queue_id).filter(models.PdfInfo.user_id == user_id)

#     q_list = []
#     for queue in queues:
#         queue= db.query(models.PdfInfo).filter(models.PdfInfo.queue_id == queue_id).filter(models.PdfInfo.user_id == user_id).filter(models.PdfInfo.id==pdf_id).first()
#         q=schemas.PDF(id=queue.id,
#                 queue_name=q_name.name,
#                 queue_id=queue.queue_id,
#                 user_id=queue.user_id,
#                 url=queue.url,
#                 status=queue.status,
#                 extracted_data=queue.extracted_data,
#                 score=queue.score,
#                 feedback_user=queue.feedback_user)
#     # try:
#     #   print("llll")
#     #   save_data("C:/Users/benna/Desktop/Bureau/mabrouk/fast/sql_app/test.xls", a)
#     # except Exception as e:
#     #     print(e)
#     return q_list


    # return FileResponse(some_file_path)


def convert_to_csv(db: Session,user_id:id,queue_id:id):
    if queue_id==0:
        queues= db.query(models.PdfInfo).filter(models.PdfInfo.user_id == user_id)
    else:
        queues= db.query(models.PdfInfo).filter(models.PdfInfo.queue_id == queue_id).filter(models.PdfInfo.user_id == user_id)



    q_list = []
    import pandas as pd

    dataframe = pd.DataFrame()
    for queue in queues:
        q_name= db.query(models.Queue).filter(models.Queue.id == queue.queue_id).first()

        print("-------------------",queue.id)
        print("-------------------",q_name.name)
        print("-------------------",queue.extracted_data)

        q=schemas.PDF(id=queue.id,
            queue_name=q_name.name,
            queue_id=queue.queue_id,
            user_id=queue.user_id,
            url=queue.url,
            status=queue.status,
            extracted_data=queue.extracted_data,
            score=queue.score,
            feedback_user=queue.feedback_user)
        print('----------------------')

        
        dataframe=dataframe.append(q.dict(), ignore_index=True)

    print(dataframe)




            # q=schemas.Get_Queue(id=queue.id,name=queue.name)
    header=['id',	'user_id',	'url',	'status',	'score',	'queue_name',	'queue_id',	'feedback_user'	,'extracted_data']


    # PDFs=schemas.PDFs(Queues=q_list)
    
    dataframe.to_excel ("{0}_{1}.xlsx".format(user_id,queue_id), index = False, header=True)

    return FileResponse("{0}_{1}.xlsx".format(user_id,queue_id))


    # return q_list

