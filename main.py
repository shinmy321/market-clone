from fastapi import FastAPI,UploadFile,Form,Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3

con=sqlite3.connect('db.db',check_same_thread=False)
cur=con.cursor()
cur.execute(f"""
             CREATE TABLE IF NOT EXISTS items(
	            id INTEGER PRIMARY KEY,
	            title TEXT NOT NULL,
	            image BLOB,
	            price INTEGER NOT NULL,
	            description TEXT,
	            place TEXT NOT NULL,
	            insertAT INTEGER NOT NULL
	
 );

            """)

app=FastAPI()

@app.post('/items')
async def create_item(image:UploadFile,
                title:Annotated[str,Form()],
                price:Annotated[int,Form()],
                description:Annotated[str,Form()],
                place:Annotated[str,Form()],
                insertAT:Annotated[int,Form()]
                ):
    
    image_bytes=await image.read()
    cur.execute(f"""
                INSERT INTO items(title,image,price,description,place,insertAT)
                VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAT})
                """)
    con.commit()
    return '200'

@app.get('/items')
async def get_items():
    con.row_factory=sqlite3.Row  #컬럼명 가져오기 ['id',1], 요렇게
    cur=con.cursor() #db를 가져오면서 connection의 현재위치를 cursor라고 표시함
    rows=cur.execute(f"""
                     SELECT * from items;
                     """).fetchall()
    
    # rows=[['id',1],['title','식칼팝니다']...]
 #rows 중에 각각의 array를 돌면서 그 array를 dictionary 객체형태로 만들어 주는 문법
    return JSONResponse(jsonable_encoder(dict(row) for row in rows))


@app.get('/images/{item_id}') #아이템에 맞는 이미지를 보내줄거야
async def get_image(item_id):
    cur=con.cursor()
    image_bytes = cur.execute(f"""
                           SELECT image from items WHERE id={item_id}
                           """).fetchone()[0]
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

@app.post('/signup')
def signup(id:Annotated[str,Form()],
           password:Annotated[str,Form()],
           name:Annotated[str,Form()],
           email:Annotated[str,Form()]):
    cur.execute(f"""
                INSERT INTO users(id,name,email,password)
                VALUES('{id}','{name}','{email}','{password}')
                """)
    con.commit()
    return '200'
 #커넥션을 확정 지음

app.mount("/", StaticFiles(directory="frontend",html=True), name="frontend")