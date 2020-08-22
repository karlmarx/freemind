FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./fastapi_app /app/app

RUN pip install --upgrade pip && \
    pip install SQLAlchemy pydantic fastapi sqlalchemy_utils sqlalchemy_enum_list passlib email-validator python-dotenv psycopg2-binary psycopg2
