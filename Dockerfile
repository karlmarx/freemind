#FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
#
#COPY . /app/app
#
#RUN set -ex; \
#    pip install --upgrade pip && \
#    pip install SQLAlchemy pydantic fastapi sqlalchemy_utils sqlalchemy_enum_list passlib email-validator python-dotenv psycopg2-binary  uvicorn pg8000 && \
#    pip install gunicorn
#
#CMD exec uvicorn main:app --reload

#/eighth-orbit-287212

FROM python:3.8

# Copy application dependency manifests to the container image.
# Copying this separately prevents re-running pip install on every code change.
COPY requirements.txt ./

# Install production dependencies.
RUN set -ex; \
    pip install -r requirements.txt; \
    pip install gunicorn

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 -k uvicorn.workers.UvicornWorker main:app




#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app
#FROM python:3.8
#
## Copy application dependency manifests to the container image.
## Copying this separately prevents re-running pip install on every code change.
#COPY requirements.txt ./
#
## Install production dependencies.
#RUN set -ex; \
#    pip install -r requirements.txt; \
#
#
## Copy local code to the container image.
#ENV APP_HOME /app
#WORKDIR $APP_HOME
#COPY . ./
#
## Run the web service on container startup. Here we use the gunicorn
## webserver, with one worker process and 8 threads.
## For environments with multiple CPU cores, increase the number of workers
## to be equal to the cores available.
