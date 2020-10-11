# from pydantic import EmailStr
# from sqlalchemy.orm import Session
#
# import main
# import schemas
# import models
#
#
# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()
#
#
# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()
#
#
# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()
#
#
# def create_user(db: Session, user: schemas.UserCreate):
#     userdict = user.dict()
#     userdict['hashed_password'] = main.pwd_context.hash(user.password)
#     userdict.pop('password', None)
#     db_user = models.User(**userdict)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
#
# def update_user(db: Session, user_id: int, user_in: schemas.UserPatch):
#     update_data = user_in.dict(exclude_unset=True)
#     if 'password' in update_data:
#         update_data['hashed_password'] = main.pwd_context.hash(user_in.password)
#         update_data.pop('password', None)
#     # stored_data = schemas.UserPatch(**db_user)
#     db.query(models.User).filter(models.User.id == user_id).update(update_data, synchronize_session=False)
#     db.commit()
#     return db.query(models.User).filter(models.User.id == user_id).first()
