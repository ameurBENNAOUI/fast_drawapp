from typing import List
from fastapi.responses import FileResponse

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

from fastapi.staticfiles import StaticFiles


from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'])
]

from fastapi import Form,File, UploadFile


models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




from datetime import datetime, timedelta

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext
from pydantic import BaseModel
import random
import string
letters = string.ascii_letters
import numpy as np
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 #24 H

users = db.query(models.User).all()

users_db={}
for user in users:
    users_db[user.email]={"username":user.email,
                 "user_id":user.id,
                 "full_name": user.id,
                 "email": user.email,
                 "hashed_password":user.hashed_password,
                 "disabled": False}
    
fake_users_db =users_db


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    username: str
    user_id =int
    email: str = None
    full_name: int
    disabled: bool = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    print("====",user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]






#app = FastAPI()












# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




@app.post("/users/", response_model=schemas.User,tags=["user"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # return 
    a=crud.create_user(db=db, user=user)
    users = db.query(models.User).all()

    # users_db={}
    for user in users:
        users_db[user.email]={"username":user.email,
                    "user_id":user.id,
                    "full_name": user.id,
                    "email": user.email,
                    "hashed_password":user.hashed_password,
                    "disabled": False}
        
    fake_users_db =users_db

    return a

@app.get("/users/", response_model=List[schemas.User],tags=["user"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User,tags=["user"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item,tags=["item"])
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item],tags=["item"])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
from pixels_match import converter_pdf,resizer_img,sub_image

import shutil
import os
@app.post("/uploadfile/",tags=["template"])
async def create_file(file: UploadFile = File(...),current_user: User = Depends(get_current_active_user)):
    global upload_folder
    upload_folder=".//static//template_pdf"
    if '.pdf' in file.filename:
            file_object = file.file
            user_id=current_user.full_name
            rand_letters =''.join(random.choices(letters,k=5))

            filename=file.filename.replace('.pdf','')+'___'+str(user_id)+'_'+rand_letters+'.pdf'
            #create empty file to copy the file_object to
            upload_folder = open(os.path.join(upload_folder, filename), 'wb+')
            shutil.copyfileobj(file_object, upload_folder)
            upload_folder.close()
    # elif '.txt' in file.filename:
    #     upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    #     shutil.copyfileobj(file_object, upload_folder)
    #     upload_folder.close()
    #     list_urls=list(np.loadtxt(demostring, delimiter =';', unpack = True))
    #     for url in urls: 
    #             if "http"==file.filename[:4] or "ftp" == file.filename[:3]:
    #             filename = wget.download(url,out="./check")
    #             url_path=filename


    path_source="//static//template_pdf//"

#    path_src=url_path


    file_300="static/template_img_300/"
    file_200="static/template_img_200/"
    imgfilename=(filename).replace(".pdf",".jpg")
    pdffilename=filename


    alpha=7
    converter_pdf(path_source,pdffilename,file_300,imgfilename,300)
    resizer_img(os.path.join(os.getcwd(), file_300), imgfilename,os.path.join(os.getcwd(), file_200) , imgfilename, alpha)

#    converter_pdf(path_source,pdffilename,file_200,imgfilename,200)
    
    try:
        name=".".join(filename.split(".")[:-1])
    except:
        name=filename.split(".")[:-1]
    template=schemas.TemplateCreate(name=name, crop_json=None, status_crop=False,label_json=None,label_status=False,template_path=(filename).replace(".pdf",".jpg"))
    crud.create_template(db=db, item=template,user_id="1")
    return {"filename": filename}

@app.post("/template/", response_model=schemas.R_TemplateCreate,tags=["template"])
def create_templat(template:schemas.TemplateCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    # print(request.body)
    
    return crud.create_template(db=db, item=template,user_id=user_id)

@app.put("/template/{template_id}", response_model=schemas.R_TemplateUpdate,tags=["template"])
def update_templat(template_id:int,template:schemas.TemplateUpdate, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    print(template)
    user_id=current_user.full_name
    # print(template.dict())
    return crud.update_template(db=db,item=template,user_id=user_id,template_id=template_id)

@app.delete("/template/{template_id}", response_model=schemas.TemplateDelete,tags=["template"] )
def delete_templat(template_id:int,db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    return crud.delete_template(template_id=template_id,db=db)

@app.get("/template/{template_id}", response_model=schemas.TemplateDetail,tags=["template"])
def get_templat(template_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
#    print(current_user.user_id)
    return crud.get_tmp(db=db,template_id=template_id)

@app.get("/template",response_model=schemas.TemplatesDetail,tags=["template"])
def get_templates( db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    return crud.tmps(db=db)











@app.post("/queue/", response_model=schemas.R_Create_Queue,tags=["queue"])
def Create_Queue(template:schemas.Create_Queue, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    
    user_id=current_user.full_name

    print("..........",user_id)
    return crud.create_queue(db=db,item=template,user_id=user_id)

@app.get("/queue/", response_model=schemas.Get_Queues,tags=["queue"])
def get_queues( db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name

    print("..........",user_id)
    return crud.get_queues(db=db,user_id=user_id)

@app.get("/queue/{queue_id}", response_model=schemas.Get_Queue,tags=["queue"])
def get_queue(user_id:int,queue_id:int, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.get_queue(db=db,user_id=user_id,queue_id=queue_id)

# @app.get("/template/{item_id}", response_model=schemas.TemplateDetail,tags=["template"])
# def delete_templat(user_id: int,template:schemas.TemplateDelete, db: Session = Depends(get_db)):
#     return "j"

@app.delete("/queue/{queue_id}", response_model=schemas.QueueDelete,tags=["queue"])
def delete_queue(queue_id:int,db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    print(queue_id)
    return crud.delete_queue(db=db,queue_id=queue_id)







# @app.post("/ProccessQueue//{user_id}/{queue_id}/",response_model=schemas.R_PDF, tags=["Proccess Queue"])
# def upload_pdf(user_id:int,queue_id:int,template:schemas.Post_PdfInfo, db: Session = Depends(get_db)):
#     return crud.create_pdf(db=db,item=template,user_id=user_id,queue_id=queue_id)

# @app.delete("/ProccessQueue//{user_id}/{pdf_id}/",response_model=schemas.R_Delete_PDF, tags=["Proccess Queue"])
# def delete_pdf(user_id: int,pdf_id:int, db: Session = Depends(get_db)):
#     return crud.delete_pdf(db=db,user_id=user_id,pdf_id=pdf_id)

# @app.get("/ProccessQueue/{user_id}/{queue_id}", response_model=schemas.PDFs,tags=["Proccess Queue"])
# def get_pdfs(user_id:int,queue_id:int, db: Session = Depends(get_db)):
#     return crud.get_pdfs(db=db,user_id=user_id,queue_id=queue_id)

# @app.get("/ProccessQueue/{user_id}/{queue_id}/{pdf_id}", response_model=schemas.PDF,tags=["Proccess Queue"])
# def get_pdf(user_id:int,queue_id:int,pdf_id:int, db: Session = Depends(get_db)):
#     return crud.get_pdf(db=db,user_id=user_id,queue_id=queue_id,pdf_id=pdf_id)

# @app.get("/queue/{user_id}/{queue_id}", response_model=schemas.Get_Queue,tags=["queue"])
# def get_queue(user_id:int,queue_id:int, db: Session = Depends(get_db)):
#     return crud.get_queue(db=db,user_id=user_id,queue_id=queue_id)

# @app.delete("/queue/{user_id}/{queue_id}", tags=["queue"])
# def delete_queues(queue_id: int,queue_id:int, db: Session = Depends(get_db)):
#     return crud.delete_queue(db=db,user_id=user_id,queue_id=queue_id)

    # return crud.get_queues(db=db,user_id=user_id)

# @app.get("/queue/{user_id}/{queue_id}", response_model=schemas.Get_Queue,tags=["queue"])
# def get_queue(user_id:int,queue_id:int, db: Session = Depends(get_db)):
#     return crud.get_queue(db=db,user_id=user_id,queue_id=queue_id)

# @app.delete("/queue/{queue_id}", response_model=schemas.QueueDelete,tags=["queue"])
# def delete_queue(queue_id:int,db: Session = Depends(get_db)):
#     print(queue_id)
#     return crud.delete_queue(db=db,queue_id=queue_id)




@app.post("/upload_queue_file",tags=["Proccess Queue"])
async def create_queue_file(queue_id: str = Form(...),file: UploadFile = File(...),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    global upload_folder
    upload_folder=".//static//queues_pdf"
    # global upload_folder
    if '.pdf' in file.filename:
            file_object = file.file
            # user_id=current_user.full_name
            rand_letters =''.join(random.choices(letters,k=5))

            filename=file.filename.replace('.pdf','')+'___'+str(user_id)+'_'+rand_letters+'.pdf'
            #create empty file to copy the file_object to
            upload_folder = open(os.path.join(upload_folder, filename), 'wb+')
            shutil.copyfileobj(file_object, upload_folder)
            upload_folder.close()
    crud.create_pdf(db,user_id=user_id,queue_id=queue_id,url=filename)
    return {"filename": filename}

@app.post("/ProccessQueue/{queue_id}/",response_model=schemas.R_PDF, tags=["Proccess Queue"])
def upload_pdf(queue_id:int,template:schemas.Post_PdfInfo, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.create_pdf(db=db,item=template,user_id=user_id,queue_id=queue_id)

@app.delete("/ProccessQueue//{pdf_id}/",response_model=schemas.R_Delete_PDF, tags=["Proccess Queue"])
def delete_pdf(pdf_id:int, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.delete_pdf(db=db,user_id=user_id,pdf_id=pdf_id)

@app.get("/ProccessQueue/{queue_id}", response_model=schemas.PDFs,tags=["Proccess Queue"])
def get_pdfs(queue_id:int, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.get_pdfs(db=db,user_id=user_id,queue_id=queue_id)

@app.get("/ProccessQueue/{queue_id}/{pdf_id}", response_model=schemas.PDF,tags=["Proccess Queue"])
def get_pdf(user_id:int,queue_id:int,pdf_id:int, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.get_pdf(db=db,user_id=user_id,queue_id=queue_id,pdf_id=pdf_id)


@app.put("/ProccessQueue/{queue_id}/{pdf_id}", tags=["Proccess Queue"])
def upload_pdf(pdf_id,queue_id:int,template:schemas.Feedback, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.feedback_pdf(db=db,item=template,user_id=user_id,queue_id=queue_id,pdf_id=pdf_id)

# @app.get("/queue/{user_id}/{queue_id}", response_model=schemas.Get_Queue,tags=["queue"])
# def get_queue(user_id:int,queue_id:int, db: Session = Depends(get_db)):
#     return crud.get_queue(db=db,user_id=user_id,queue_id=queue_id)

# @app.delete("/queue/{user_id}/{queue_id}", tags=["queue"])
# def delete_queues(queue_id: int,queue_id:int, db: Session = Depends(get_db)):
#     return crud.delete_queue(db=db,user_id=user_id,queue_id=queue_id)

@app.get("/csv/{queue_id}", tags=["csv"])
def convert_to_csv(queue_id:int, db: Session = Depends(get_db),current_user: User = Depends(get_current_active_user)):
    user_id=current_user.full_name
    return crud.convert_to_csv(db=db,user_id=user_id,queue_id=queue_id)