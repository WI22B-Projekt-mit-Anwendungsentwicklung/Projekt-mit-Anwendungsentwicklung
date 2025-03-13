FROM python:3.13-alpine
RUN apk add --no-cache nodejs npm
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
#RUN npm install
CMD ["python", "./src/app.py"]
