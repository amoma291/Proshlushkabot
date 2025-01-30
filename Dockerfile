FROM python:3.10-slim 

WORKDIR /project

COPY requirements.txt /project/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /project

EXPOSE 5000

CMD python bot.py