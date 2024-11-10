from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


new_post = [
    {
        "title": "Favorite Books",
        "content": "I love reading books",
        "id": 1,
    },
    {
        "title": "Favorite Movies",
        "content": "I love watching movies",
        "id": 2,
    },
]


def find_post(id: int):
    for post in new_post:
        if post["id"] == id:
            return post


def index_post(id: int):
    for index, post in enumerate(new_post):
        if post["id"] == id:
            return index
    return None


@app.get("/posts")
async def get_posts():
    return {"data": new_post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    id = randrange(1, 100000)
    post_dict = post.dict()
    post_dict["id"] = id
    new_post.append(post_dict)
    return {"data": post_dict}


@app.get("/posts/latest")
def get_latest_post():
    post = new_post[-1]
    return {"data": post}


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    return {"data": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = index_post(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    new_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/update/{id}", status_code=status.HTTP_200_OK)
def update_post(id: int, post: Post):
    index = index_post(id)
    print(index)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    updated_post = post.dict()
    updated_post["id"] = id  # Preserve the existing ID
    new_post[index] = updated_post
    return {"data": updated_post}
