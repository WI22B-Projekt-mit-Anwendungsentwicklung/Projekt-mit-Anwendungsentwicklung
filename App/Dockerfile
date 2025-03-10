FROM python:3.13-alpine
RUN apk add --no-cache curl
COPY ./requirements.txt /app/requirements.txt
COPY Tests/ /app/Tests/
COPY App/Tests/ /app/Tests/
RUN chmod +x /app/Tests/wait-for-app.sh
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
CMD ["python", "run.py"]