from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
engine = create_engine('sqlite:///test.db', echo = True)


class Customers(Base):
   __tablename__ = 'customers'
   
   id = Column(Integer, primary_key=True)
   name = Column(String)
   address = Column(String)
   email = Column(String)


from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind = engine)
session = Session()

# add data
c1 = Customers(name = 'Ravimar', address = 'Stationnded', email = 'ravi@gmail.com')

session.add(c1)
session.commit()

# querry
result = session.query(Customers).all()

for row in result:
   print ("Name: ",row.name, "Address:",row.address, "Email:",row.email)


# update
session = Session()

x = session.query(Customers).get(51)
x.name = 'Banjara Hills Secunderabad'
session.commit()

def update_template(db: Session,item: schemas.TemplateCreate, user_id: int,template_id:int):
    db_item=db.query(models.Template).filter(models.Template.id == 1).first()
    # print("=================")
    # print(db_item{"name"})
    db_item=item
    

    # db_item = models.Template(**item.dict(), user_id=user_id)
    # db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

template_id=TemplateBase(name= "lakdar",json_data="pp",template_path="pp")


    
bb=update(db_item).where(models.Template.id==1)

db_item=db.query(models.Template).filter(models.Template.id == 1).first()
setattr(db_item,'name',152) 
db_item.name


db_item("name")


db_item.update(template_id.dict())
db
for i in db_item:
    print(i)

# update_template(session,a,1,1)


# creat_tempalte
from sqlalchemy.orm import Session
from database import SessionLocal, engine


import models, schemas
db = SessionLocal()

def create_template(db: Session,item: schemas.TemplateCreate):

    db_item = models.Template(**item.dict())
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
x={"user_id":7,"name":"ee","json_data":"mpop","template_path":"ghfdg"}

from pydantic import BaseModel
class TemplateBase(BaseModel):
    name: str
    json_data:str
    template_path:str
    class Config:
        orm_mode = True


a=TemplateBase(name= "lakdar",json_data="pp",template_path="pp")
for i in a.dict():
    print(i)
    print(a.dict()[i])
b=TemplateBase(name= "hggh",json_data="dfd",template_path="dd")
b=a


create_template(db,a)

db_item = models.Template(**a.dict())

print(a)
item=schemas.TemplateCreate(name="gffggf",json_data={"hh":"ii"},template_path="hhg")


db_item = models.Template(**item.dict(), user_id=18)