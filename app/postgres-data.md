####################################################

```
CREATE TABLE public.posts
(
    id serial,
    title character varying NOT NULL, -- varchar
    content character varying NOT NULL,
    published boolean DEFAULT True,
    created_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id)
);
```

Tyagraj guided to add rows from the pgadmin UI.
Following data added from the UI:

```
fastapi=# select * from posts
;
 id |       title       |          content           | published |            created_at            
----+-------------------+----------------------------+-----------+----------------------------------
  1 | Kashi post ujjain | We wenmt to Ujjain in 2024 | t         | 2026-07-07 18:32:16.724747+05:30
  2 | Varanasi trip     | Went to Varanasi on 2023.  | t         | 2026-07-07 18:32:16.724747+05:30
(2 rows)
```


## Real db


Install:

sudo apt install python3-dev libpq-dev build-essential
pip install psycopg2

```
import psycopg2





try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi",
        user="bhaijaan",
        password="hind@123",
        port=5433)
except Exception as e:
    print("Error while connecting to PostgreSQL", e)
```



See always use try and except when creating a connection because connection may not succeed and hence u can print an exception back to user saying db conn failed.


Also this library when u do select * from table, returns only rows and not column headers like age, name etc. so if u want those also to print, then u should do extra as follows:
```
from psycopg2.extras import RealDictCursor

# in try block
try:
    conn = psycopg2.connect(
        host="localhost",
        database="fastapi",
        user="bhaijaan",
        password="hind@123",
        port=5433, cursor_factory=RealDictCursor)
```
Here to also get rows and columns pass this realdict cursor.


then 

```
import psycopg2
from psycopg2.extras import RealDictCursor

from random import randrange
from typing import Optional

from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import BaseModel

while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="hind@123",
            port=5433,
            cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as e:
        print("Error while connecting to PostgreSQL", e)
        print("Retrying in 5 seconds...")
        import time
        time.sleep(5)





app  = FastAPI()

post_dict = [{"name": "hind", "age": 20, "id": 1}, {"name": "hind2", "age": 30, "id": 2}]

class MySchema(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

@app.get("/posts/")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return posts


@app.post("/posts/")
def create_post(data: MySchema):
    post = data.dict()
    cursor.execute("INSERT INTO posts (title, content) VALUES (%s, %s) returning *", (post["title"], post["content"]))
    post = cursor.fetchone()
    conn.commit()
    return post


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id),))
    post = cursor.fetchone()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    return post



@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    post = cursor.fetchone()
    conn.commit()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
    return post


@app.put("/posts/{id}")
def update_post(id: int, data: MySchema):
    cursor.execute(""" UPDATE posts SET title = %s, content = %s WHERE id = %s returning *""", (data.title, data.content, str(id)))
    post = cursor.fetchone()
    conn.commit()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")  
    return post
```
everythung is same execpt u create cursor in the trycatch block and then use that cursor to run execute only for select queries and also run conn.commit for update or insert queries. fetch all gives all rows of table. fetchone gives u the most recent entry in the db. 

## connection pool using psycopg2:

```
from psycopg2 import pool

import psycopg2
from psycopg2.extras import RealDictCursor

from random import randrange
from typing import Optional
import time

from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import BaseModel

while True:
    try:
        conn_pool = pool.SimpleConnectionPool(
            minconn=4,      # open 2 connections immediately
            maxconn=10,     # never open more than 10
            host="localhost",
            dbname="fastapi",
            user="postgres",
            password="hind123",
            port=5433,
            cursor_factory=RealDictCursor
        )
        # conn = psycopg2.connect(
        #     host="localhost",
        #     database="fastapi",
        #     user="postgres",
        #     password="hind@123",
        #     port=5433,
        #     cursor_factory=RealDictCursor)
        # cursor = conn.cursor()
        print("Database pool was created successfully")
        break
    except Exception as e:
        print("Error while connecting to PostgreSQL", e)
        print("Retrying in 5 seconds...")
        import time
        time.sleep(5)





app  = FastAPI()

post_dict = [{"name": "hind", "age": 20, "id": 1}, {"name": "hind2", "age": 30, "id": 2}]

class MySchema(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

@app.get("/posts/")
def get_posts():
    conn = conn_pool.getconn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    time.sleep(20)
    conn_pool.putconn(conn)
    return posts
```

See we create connection pool here. earlier we used to create a single connection and use that connection to actually perform all ops. 

but here we create pool of connections. we created 4 min connections. that means, 4 min connections are always open. it will scale to 10 conn depending upon the load.

it immediately opens 4 connections. then we do conn_pool.get_conn to get onbe conn from pool and then we do the operation and then return conn back to pool using put_conn method.



## ORM

orm is layer of abstraction that sits between database and fatsapi app. using psycopg2 we directly talked to dbms. but here we talk to orm and orm will take to database.

We dont use sql commands now and we can perform all db ops through  python code. no more sql. sql complexity can be abstracted. 

In the previous in the PGADMIN ui, we created tables ourselves and schema of table. But here we can define tables as python models. queries can be made using python code and no sql.


sqlalchemy is an example of orm. there could be many orms. and sqlalchemy depends on psycopg2 to talk to db. every orm needs a driver. it could be any driver. inourcase it happens to be psycopg2.

for ex:


```
"""
Simple SQLAlchemy 2.0 ORM example: Create, Read, Update, Delete
Uses SQLite so it runs with zero setup — swap the engine URL for Postgres later.
"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# 1. Base class — every ORM model inherits from this
class Base(DeclarativeBase):
    pass


# 2. Define the table as a class
class Hero(Base):
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int | None] = mapped_column(default=None)
    secret_name: Mapped[str]

    def __repr__(self) -> str:
        return f"Hero(id={self.id}, name={self.name!r}, age={self.age}, secret_name={self.secret_name!r})"



print(Base.metadata.tables)
# 3. Engine — connection pool. SQLite file created in current directory.
engine = create_engine("postgresql://postgres:hind123@localhost/fastapi", echo=True)
# echo=True would print every SQL statement SQLAlchemy generates — useful while learning.


def create_tables():
    Base.metadata.create_all(engine)
```


from the orm we import DeclarativeBase, Mapped, mapped_column, Session these things.


here we created a empty class called base and base extends declarative base in the sense it takes all the attr and methods from that class.

and we create this empty class because in sqlalchemy each table is represented as a class. so we create base class and then whatever number of classes we create (that represents tables) extend this base class.

then in the end we say Base.metadata.create_all() to create all the tables.


And we first open or create a engine, from sqlalchemy we imported `from sqlalchemy import create_engine, select`.

so `engine = create_engine("postgresql://postgres:hind123@localhost/fastapi", echo=True)
` , here see we call create_engine function to actually initialise pool class in the memory.

unlike psycopg2 it doesnt create conns immediately but creates conns lazily on demand. in the sense whenever it sees:
```
    with Session(engine) as session:
```
then it immediately asks engine to give conn from pool. so engine creates it hands it over back.

Now inside the table i.e inside the heroes class, what we do is we define the fields,

like:
```
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    age: Mapped[int | None] = mapped_column(default=None)
    secret_name: Mapped[str]
```

table name we define., then id as int here and we say primary key and name as str and by default not null constraint is set sincde we didnt set default=None. but for age we say it could be int or none. so default val is none. so it allows null values so it is notnull. and secret_name is str and it is also not null actually.

This is an example func of adding row in the table:
```
def create_hero(name: str, age: int | None, secret_name: str) -> int:
    with Session(engine) as session:
        hero = Hero(name=name, age=age, secret_name=secret_name)
        session.add(hero)
        session.commit()
        print(f"Created: {hero}")
        return hero.id
```

here see we instantiate class and set all the values and then call session.add to add the entrey and then do session.commit. 

this is same as cursor.execute and cursor.commit right. but here no plain sql commands are used at all.

read func:
```
def read_hero_by_id(hero_id: int) -> Hero | None:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        print(f"Read by id {hero_id}: {hero}")
        return hero
```

see we do get to read and then directly return hero which is obj. so we have __repr__ dunder method that returns only string. got it.

and also since we have echo=True in create_engine this will print the command it has actually used while creating table:
```
2026-07-10 13:38:44,141 INFO sqlalchemy.engine.Engine 
CREATE TABLE heroes (
        id SERIAL NOT NULL, 
        name VARCHAR NOT NULL, 
        age INTEGER, 
        secret_name VARCHAR NOT NULL, 
        PRIMARY KEY (id)
)
```
and see getting all records:
```
def read_all_heroes() -> list[Hero]:
    with Session(engine) as session:
        stmt = select(Hero).order_by(Hero.id)
        heroes = session.execute(stmt).scalars().all()
        print(f"Read all ({len(heroes)} rows):")
        for h in heroes:
            print(f"  {h}")
        return list(heroes)
```


delete and update funcs:
```
# ---------- UPDATE ----------
def update_hero_age(hero_id: int, new_age: int) -> None:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if hero is None:
            print(f"Update failed: no hero with id {hero_id}")
            return
        hero.age = new_age
        session.commit()  # SQLAlchemy detects the change and generates the UPDATE
        print(f"Updated: {hero}")


# ---------- DELETE ----------
def delete_hero(hero_id: int) -> None:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if hero is None:
            print(f"Delete failed: no hero with id {hero_id}")
            return
        session.delete(hero)
        session.commit()
        print(f"Deleted hero id {hero_id}")
```

Now that we understood the session concept. I implemented this for our posts example.

```
"""
Simple Posts CRUD API using FastAPI and SQLAlchemy.
PostgreSQL is the backend used for this example. Make sure to have a PostgreSQL server running and update the connection string in the code accordingly.
"""

from sqlalchemy import TIMESTAMP, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


from datetime import datetime

from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, EmailStr

from passlib.context import CryptContext

passwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserSchema(BaseModel): # Pydantic model for request validation and serialization
    email: EmailStr
    password: str

class MySchema(BaseModel): # Pydantic model for request validation and serialization
    title: str
    content: str
    published: bool = True



class MySchemaOut(MySchema): # Pydantic model for response serialization
    id: int
    created_at: datetime
    # class Config:
    #     orm_mode = True # This tells Pydantic to treat SQLAlchemy models as dictionaries, allowing for easy serialization of SQLAlchemy objects.

class Base(DeclarativeBase):
    pass


class UserSchemaOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime



class Post(Base): # SQLAlchemy model for the Post table
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True) # marks id as primary key
    title: Mapped[str] # makes title a required field and not nullable
    content: Mapped[str] # make content a required field and not nullable
    published: Mapped[bool] = mapped_column(default=True) # makes published a boolean field with a default value of True
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default="now()") # adds a timestamp field with a default value of the current time

    def __repr__(self) -> str:
        return f"Post(id={self.id}, title={self.title!r}, content={self.content!r}, published={self.published})"



class User(Base): # SQLAlchemy model for the User table
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True) # marks id as primary key
    email: Mapped[str] = mapped_column(unique=True) # makes email a required field, unique and not nullable
    password: Mapped[str] # makes password a required field and not nullable
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default="now()") # adds a timestamp field with a default value of the current time

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email!r}, password={self.password!r})"

print(Base.metadata.tables)
engine = create_engine("postgresql://postgres:hind123@localhost/fastapi", echo=True) # fastapi is the database name, make sure to create it in your PostgreSQL server before running the code.


def create_tables():
    Base.metadata.create_all(engine) # this will create the tables in the database if they don't exist already.






def lifespan(app: FastAPI):
    create_tables() #  This will run when the application starts, ensuring that the tables are created in the database.
    yield
    # Anything you want to do when the application shuts down can be done here, but for this example, we don't have any specific shutdown tasks.

app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=UserSchemaOut)
def create_user(user: UserSchema):
    password = passwd_context.hash(user.password)
    with Session(engine) as session:
        user = User(email=user.email, password=password)
        session.add(user)
        session.commit()
        print(user)
        return user


@app.get("/users/", response_model=list[UserSchemaOut])
def get_users():
    with Session(engine) as session:
        users = session.execute(select(User)).scalars().all()
        print(users)
        return users

@app.get("/users/{id}", response_model=UserSchemaOut)
def get_user(id: int):
    with Session(engine) as session:
        user = session.get(User, str(id))
        print(user)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} not found")
        return user


@app.post("/posts/", response_model=MySchemaOut)
def create_post(post: MySchema):
    with Session(engine) as session:
        post = Post(title=post.title, content=post.content, published=post.published)
        session.add(post)
        session.commit()
        print(post)
        return post


@app.get("/posts/", response_model=list[MySchemaOut])
def get_posts():
    with Session(engine) as session:
        posts = session.execute(select(Post)).scalars().all()
        print()
        print(">>>>>>>>>>>> Size of checkedin:", engine.pool.checkedin())
        print(">>>>>>>>>>>> Size of checkedout:", engine.pool.checkedout())

        return posts


@app.get("/posts/{id}", response_model=MySchemaOut)
def get_post(id: int):
    with Session(engine) as session:
        post = session.get(Post, str(id))
        print(post)
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
        return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    with Session(engine) as session:
        post = session.get(Post, str(id))
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
        session.delete(post)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=MySchemaOut)
def update_post(id: int, updated_post: MySchema, ):
    with Session(engine) as session:
        post = session.get(Post, str(id))
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} not found")
        post.title = updated_post.title
        post.content = updated_post.content
        post.published = updated_post.published
        session.commit()
        print(post)
        return post
```
So earlie we had only schema for input. But I defined for output as well called MySchemaOut and passed response_model inside respective decorator. 

Then I added users endpoint and allowed them to register their username and password. password is hashed using bcyrpt algorithm. 


now since we understood engine instantiates the pool class, u can check the number of conns checked in i.e no of connections created by engine for that respective req. using checkedin() method. checkout means no of connectios sent back to the engine in that session. it would be 0 in our case. every api req creates new session, by default no conns are checkedout at frst. later checkedin wil be 1 as 1 conn is open.

I defined user class also to create user table.




## Routers.


Now here our users and posts routes are present in the same file. in reality we actually place these routes in diff files. Then instead of placing or creating app instance or fastapi instance in each file we just import APIServer and create a router that manages multiple routes. Now they are okay to be placed in diff files.


First I organised all the things in seperate files.


schemas.py: all the schemas such as MySchema for payload, Myschemaout for response sent by API. UserSchema for user creation payload and UserSchemaOut for the response sent back by api.

And hash.py in which we have hash password func to actually hash the passwd. and models.py where we define the classes that represent tables.


And then I imported APIRouter package and then created rotuer instance in routers/posts.py, users.py. This router contains router prefix as /posts and /users because instead of havin to write that /posts in each decorator write once then just specify "/{id}" for exmaple in decorator. then it appends /posts/{id}. This is the advantage. our api is simple and hence it is so simple. But in companies they might have complex paths like /posts/app/id/23 like this. so its easy to have orefix.

And also we can group all the posts into posts tah so that in fastapi ui, all post apis will be under posts umbrella instead of default tags. same for users. they will be under users umbrella.


## Authentication:

2 main ways of authentication:
- session based 
- jwt based

sesion based: we store something on backend server to tract whether a user is logged in. 
jwt based: its stateless. there is nothing stored in our backend server like session based which keeps track of whether  a user is logged in or not.


here we ask user to specify username and passwd, if they are valid, then we issue a token. api issues token to client. he uses that token as  auth bearer and perform reqs to api.



pyjwt is a package to sign and verify tokens. if planning to use rsa then u should: `pip install pyjwt[crypto]`.

and also to convert hashed passwd back to plain text install: `pip install "pwdlib[argon2]"`


SELECT memories.id, memories.title, memories.content, memories.created_at, memories.owner_id, users_1.id AS id_1, users_1.email, users_1.password, users_1.created_at AS created_at_1 
FROM memories LEFT OUTER JOIN users AS users_1 ON users_1.id = memories.owner_id.


so basically joinedload says run the left outer join and fetch the flat rows that contains the post and its user owner.
```
ELECT memories.id, memories.title, memories.content, memories.created_at, memories.owner_id, users_1.id AS id_1, users_1.email, users_1.password, users_1.created_at AS created_at_1 
FROM memories LEFT OUTER JOIN users AS users_1 ON users_1.id = memories.owner_id
fastapi-# ;
 id |       title       |            content             |            created_at            | owner_id | id_1 |      email      |                           password                           |           created_at_1           
----+-------------------+--------------------------------+----------------------------------+----------+------+-----------------+--------------------------------------------------------------+----------------------------------
  1 | 2028 shimla trip  | shimla e to be visited in 2028 | 2026-07-15 19:05:30.869164+05:30 |        1 |    1 | kashi@gmail.com | $2b$12$1Z/tusvgfpdCnS1snUf.wOLcSNGBat4Jb3HdviudX7Z1d6CnO0YT2 | 2026-07-15 19:05:30.869164+05:30
  2 | 2029 kashmir trip | shimla e to be visited in 2029 | 2026-07-15 19:05:30.869164+05:30 |        1 |    1 | kashi@gmail.com | $2b$12$1Z/tusvgfpdCnS1snUf.wOLcSNGBat4Jb3HdviudX7Z1d6CnO0YT2 | 2026-07-15 19:05:30.869164+05:30
(2 rows)
```

Now relationshio(User) here actually takes that flat result and fills the User instance and stores in owner field.

Now here relationship func was used right, then sqlalchemy actually looks that how posts and user are related, what was the foreign key used. it figures out that ok, ownerid is the foreign key that refs user.id, whenever joinedload is used it creates join on that specific condition, user.id = owner_id, here order doesnt matter, owner_id  = user.id also correct.

2026-07-17 12:10:21,484 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-17 12:10:21,485 INFO sqlalchemy.engine.Engine INSERT INTO memories (title, content, owner_id) VALUES (%(title)s, %(content)s, %(owner_id)s) RETURNING memories.id, memories.created_at
2026-07-17 12:10:21,485 INFO sqlalchemy.engine.Engine [cached since 48.67s ago] {'title': 'Family Reunion', 'content': 'Meeting cousins after 5 years', 'owner_id': '1'}
2026-07-17 12:10:21,486 INFO sqlalchemy.engine.Engine COMMIT
2026-07-17 12:10:21,496 INFO sqlalchemy.engine.Engine BEGIN (implicit)
2026-07-17 12:10:21,497 INFO sqlalchemy.engine.Engine SELECT memories.id AS memories_id, memories.title AS memories_title, memories.content AS memories_content, memories.created_at AS memories_created_at, memories.owner_id AS memories_owner_id 
FROM memories 
WHERE memories.id = %(pk_1)s
2026-07-17 12:10:21,497 INFO sqlalchemy.engine.Engine [cached since 48.67s ago] {'pk_1': 5}
2026-07-17 12:10:21,498 INFO sqlalchemy.engine.Engine SELECT users.id AS users_id, users.email AS users_email, users.password AS users_password, users.created_at AS users_created_at 
FROM users 
WHERE users.id = %(pk_1)s


## Cors: (cross origin resource sharing)

origin means combo of scheme, host, port. all 3 must match exactly for 2 urls to be considered the same origin.

ex:
```
https://example.com:443/page1   
https://example.com:443/page2   → SAME origin (path doesn't matter)

http://example.com              vs   https://example.com    → DIFFERENT (scheme differs)
https://example.com             vs   https://api.example.com → DIFFERENT (host differs — subdomains count as different origins!)
https://example.com:443         vs   https://example.com:8000 → DIFFERENT (port differs)
```

This subdomain rule surprises people constantly — app.yourapp.com and api.yourapp.com are different origins from a browser's perspective, even though they're "the same company/domain" conceptually.


cors is a browser sec rule and resource sharing means whether webpage is allowed to fetch data from diff website than the one its currently on.


so when u open a website in ur browser, it runs javascript code right there in your browser on your machine.

 That JavaScript can do things like:
```
fetch("https://someapi.com/data")
```
This means: "hey browser, while this webpage is open, go make a network request to someapi.com and give me back the response, so I (the webpage's code) can use that data — maybe to show it on the page."
This is exactly what your FastAPI backend + a frontend website would do in practice — your frontend's JavaScript calls your backend's API to fetch memories, log in, etc.

**what is the danger?**

You're logged into your bank's website, mybank.com, in one browser tab. Your browser is storing a login cookie for mybank.com right now.

You then open a second tab and visit some sketchy website, evil.com. That site's JavaScript — without you knowing — quietly runs:
```
fetch("https://mybank.com/transfer-money", {
  method: "POST",
  credentials: "include",   // tells browser: attach my mybank.com cookies too
  body: JSON.stringify({ to: "attacker", amount: 10000 })
})
```
here include means whatever tokens u have for mybank.com, send them back to mybank.com as crddentials.

Because browsers automatically attach cookies for whatever domain a request is going to (that's just how cookies work. he asks browser to send stored cookies to bank api), this request WOULD carry your real login cookie for mybank.com, even though you're on evil.com.(one webpage on evil.com website makes network call to another bank website) If nothing stopped this, evil.com's JavaScript could then read the response and confirm the transfer happened, or just fire off the request blindly and it'd still succeed on mybank.com's end.

remember only response from bank is not allowed to read by javascript code of evil.com. it doesnt stop him from making req to bank.com using that cookie. for it csrf tokens are used. we will cover it later.

Browsers enforce a rule automatically, no configuration needed: JavaScript running on one website (evil.com) is NOT allowed to freely read responses from requests made to a different website (mybank.com), unless mybank.com explicitly says "yes, I permit this other website to do that."

Browsers enforce a rule automatically, no configuration needed: JavaScript running on one website (evil.com) is NOT allowed to freely read responses from requests made to a different website (mybank.com), unless mybank.com explicitly says "yes, I permit this other website to do that."
This default-blocking rule is called the Same-Origin Policy — and CORS is the actual mechanism by which a server can selectively loosen that rule, saying "I specifically allow requests coming from this particular other website."

**Two categories of cross-origin requests — "Simple" vs "Preflighted".**

- "Simple" requests — sent directly, no preflight check
A request qualifies as "simple" only if it meets ALL of these conditions:

Method is GET, HEAD, or POST
Only "simple" headers are used (Accept, Accept-Language, Content-Language, Content-Type restricted to a few values)
Content-Type is one of: application/x-www-form-urlencoded, multipart/form-data, or text/plain (NOT application/json!).

For a simple request, the browser just sends it directly, and checks the response's Access-Control-Allow-Origin header before deciding whether to let your JavaScript read the result.


- Preflighted" requests — the browser sends an extra OPTIONS request FIRST, to ask permission
Anything that doesn't qualify as "simple" triggers a preflight — and this includes almost everything you actually do in a real API:
```
fetch("http://localhost:8000/memories/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Trip", content: "..." })
})
```

What actually happens on the wire, step by step

Browser sees this request uses application/json and method POST with a custom header — not "simple" — so it does NOT send your actual POST request yet.
Browser first sends an OPTIONS request to the same URL, asking permission:
```
OPTIONS /memories/ HTTP/1.1
Host: localhost:8000
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type
```
Your server (FastAPI's CORSMiddleware) must respond to this OPTIONS request with headers confirming permission:
```
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: content-type
```
Only if the browser is satisfied with THIS preflight response does it then send your actual POST request with the real body.
The actual response to that POST must ALSO include Access-Control-Allow-Origin for the browser to let your JS read it.


for fastapi u should import the following url:
```
from fastapi.middleware.cors import CORSMiddleware
```
specify list of origins allowed to call the api:

```
origins = [
    "http://localhost:8080",
    "https://www.google.com"
]
```
see google aloso allowed to call this api.
```
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
then u sepcify which methods and headers are allowed to be sent to the api from diff domain or website.

then click on developer tools and console:
```
fetch("http://localhost:8000").then(res => res.json()).then(console.log)
``` 
run this u should see response.

```
{name: 'memories API', version: '1.0.0'}
```