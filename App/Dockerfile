FROM python:3.13-alpine
RUN apk add --no-cache curl
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
RUN chmod +x /app/Tests/wait-for-app.sh
CMD ["sh", "-c", "./Tests/wait-for-app.sh && python run.py"]