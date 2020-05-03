from typing import List
from typing import Any, Optional


from pydantic import BaseModel,Json, ValidationError, validator


class ItemBase(BaseModel):
    title: str
    description: str = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBas(BaseModel):
    email: str


class UserCreate(UserBas):
    password: str
    name:str


class User(UserBas):
    id: int
    is_active: bool
    items: List[Item] = []

    class Config:
        orm_mode = True


class TemplateBase(BaseModel):
    # user_id:int
    name: str
    crop_json:Any
    status_crop:bool
    label_json:Any=None
    label_status:bool=None

    template_path:str




    class Config:
        orm_mode = True

class TemplateCreate(TemplateBase):
    crop_json:Json
    label_json:Json=None
    pass

class TemplateUpdate(TemplateBase):
    id:int
    crop_json:Json
    label_json:Json=None
    
    class Config:
        orm_mode = True
        
class R_TemplateUpdate(TemplateBase):
    id:int
    
    class Config:
        orm_mode = True
class R_TemplateCreate(BaseModel):
    id:int


class TemplateDelete(BaseModel):
    status:bool

class TemplateDetail(TemplateBase):
    id:int
    
class TemplatesDetail(BaseModel):
    templates:List[TemplateDetail]

# Queue Section

class Create_Queue(BaseModel):
    name: str
class R_Create_Queue(BaseModel):
    id:int

class Get_Queue(BaseModel):
    id:int
    name:str
class Get_Queues(BaseModel):
    # id=int
    Queues: List[Get_Queue]

class QueueDelete(BaseModel):
    status:bool 



# PDF Sectio

class R_PDF(BaseModel):
    id:int
class PDF(BaseModel):
    id:int
    queue_name:str
    queue_id:int
    user_id:int
    url:str
    status:str=None
    extracted_data:str=None
    score:str=None
    feedback_user:str=None

class R_Delete_PDF(BaseModel):
    status:bool

class PDFs(BaseModel):
    # id=int
    Queues: List[PDF] 


class Post_PdfInfo(BaseModel):
    url:str

class R_Post_PdfInfo(BaseModel):
    pdf_id:str


class ProccessQueue(BaseModel):
    Queue_id:str
    Status:str


class Feedback(BaseModel):
    feedback:str
    








