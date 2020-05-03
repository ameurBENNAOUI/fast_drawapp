from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
engine = create_engine('sqlite:///sales.db', echo = True)
meta = MetaData()

students = Table(
   'customers', meta, 
   Column('id', Integer, primary_key = True), 
   Column('name', String), 
   Column('address', String),
   Column('email', String),
)
meta.create_all(engine)