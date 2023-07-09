from fastapi import FastAPI,UploadFile,Form,Response,Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3

con=sqlite3.connect('db.db',check_same_thread=False)
cur=con.cursor()


app=FastAPI()
#어떻게 인코딩을 할지를 정하는거 , SECRET 키를 노출시키면 JWT를 언제든지 노출 시킬 수 있다.
SERCRET="super-coding"
manager=LoginManager(SERCRET,'/login') #시크릿 URL? 시크릿 토큰이 어디서 발급 될거냐
#로그인 페이지에서만 발급되도록, 
@manager.user_loader()#메니저가 키를 같이 조회함
def query_user(data):
    WHERE_STATEMENTS= f'id="{data}"'
    if type (data) ==dict:
        WHERE_STATEMENTS = f'''id="{data['id']}"'''
    con.row_factory=sqlite3.Row  #컬럼명 가져오기
    cur=con.cursor()
    user = cur.execute(f"""
                     SELECT * from users WHERE {WHERE_STATEMENTS}
                     """).fetchone()
    return user
    
  
    
@app.post('/login')
def login(id:Annotated[str,Form()],
           password:Annotated[str,Form()]):
   user = query_user(id)
   if not user:
       raise InvalidCredentialsException  #401 자동으로 생성해서 내려줌 유저가 없으면 에러메시지를 보여줌
   elif  password != user['password']:    #엘스이프라는 뜻
       raise InvalidCredentialsException
  
  #data ? 어떤 데이터를 넣을 꺼니 
   access_token=manager.create_access_token(data={
    'sub': {
       'id':user['id'],
       'name':user['name'],
       'email':user['email']
       }
  })
    #리턴에 access토큰을 넣어주면 됨
   return {'access_token':access_token}  #자동으로 200상태 코드를 내려줌
    
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
async def get_items(user=Depends(manager)): #유저가 인증된 상태에서만 응답을 보낼 수 있도록 
    print(user)
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



app.mount("/", StaticFiles(directory="frontend",html=True), name="frontend")