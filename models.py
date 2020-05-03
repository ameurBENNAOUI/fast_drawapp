from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,JSON
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name=Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    templates = relationship("Template")
    # items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")

class Template(Base):
    __tablename__ = "template"
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String, index=True)
    label_json= Column(JSON, index=True)
    label_status=Column(Boolean, index=True)
    crop_json= Column(JSON, index=True)
    status_crop= Column(Boolean, index=True)
    template_path=Column(String, index=True)

    user_id=Column(Integer,ForeignKey('users.id'))
  
    # user = relationship("User", back_populates="templates")
    


class Queue(Base):
    __tablename__ = "queue"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id=Column(String, index=True)
    # status=Column(String, index=True)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    # owner = relationship("User", back_populates="queue")

    
    # items = relationship("PdfInfo", back_populates="owner")


class PdfInfo(Base):
    __tablename__ = "pdfinfo"
    id = Column(Integer, primary_key=True, index=True)
    queue_id=Column(Integer, index=True)
    user_id=Column(Integer, index=True)
    url = Column(String, index=True)
    status=Column(String, index=True)
    score=Column(String, index=True)
    feedback_user=Column(String, index=True)

    # proccess=Column(String, index=True)
    extracted_data=Column(String, index=True)


    # owner_id = Column(Integer, ForeignKey("queue.id"))

    # owner = relationship("Queue", back_populates="PdfInfo")




