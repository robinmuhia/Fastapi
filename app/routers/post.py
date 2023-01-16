from .. import models,schemas,oauth2
from fastapi import Response,status,HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List,Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags = ['Posts']
)

@router.get('/',status_code=status.HTTP_200_OK,response_model=List[schemas.PostOut])
def test_post(db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user),limit: int = 10,skip:int = 0,search:Optional[str] = ''):
    posts = db.query(models.Post,func.count(models.Votes.post_id).label('votes')).join(models.Votes,models.Votes.post_id == models.Post.id,isouter = True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts



#@router.post("/posts", status_code=status.HTTP_201_CREATED,response_model=schemas.PostResponse)
#def create_post(post:schemas.PostCreate):
    #cursor.execute(""" INSERT INTO posts(title,content,published) VALUES(%s,%s,%s) RETURNING *""",(post.title,post.content,post.published))
    #new_post = cursor.fetchone()
    #conn.commit()
    #return new_post


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.PostResponse)
def create_post(post:schemas.PostCreate,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    result = models.Post(owner_id = current_user.id,**post.dict())
    db.add(result)
    db.commit()
    db.refresh(result)
    return result



#@router.get('/posts/{id}',status_code=status.HTTP_200_OK,response_model=schemas.PostResponse)
#def get_post(id:int):
#   cursor.execute(''' SELECT * FROM posts WHERE id = %s''',(str(id)))
#    single_post = cursor.fetchone()
#    if single_post == None:
#        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                           detail=f'post with id: {id} was not found')
#   return single_post


@router.get('/{id}',status_code=status.HTTP_200_OK,response_model=schemas.PostOut)
def get_post(id:int,db:Session = Depends(get_db)):
    single_post = db.query(models.Post,func.count(models.Votes.post_id).label('votes')).join(models.Votes,models.Votes.post_id == models.Post.id,isouter = True).group_by(models.Post.id).first()
    if single_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} was not found')
    return single_post
    
    
    

#@router.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
#def delete_post(id:int):
#   cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING *""",(str(id)),)
#   deleted_post = cursor.fetchone()
#   conn.commit()
#   if deleted_post == None:
#       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                           detail=f'post with id: {id} does not exist')
#   return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = post_query.first()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'post with id: {id} does not exist')

    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# @router.put("/posts/{id}",status_code=status.HTTP_200_OK,response_model=schemas.PostResponse)
# def update_post(id:int,post:schemas.PostCreate):
#     cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published,str(id)),)
#     updated_post = cursor.fetchone()
#     conn.commit()
#     if updated_post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'No post with id {id} exists')                
    
#     return updated_post


@router.put("/{id}",status_code=status.HTTP_200_OK,response_model=schemas.PostResponse)
def update_post(id:int,updated_post:schemas.PostCreate,db:Session = Depends(get_db),current_user:int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No post with id {id} exists')

    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Not authorized to perform requested action')               
    
    post_query.update(updated_post.dict(),synchronize_session=False)
    db.commit()
    return post_query.first()
