FROM python:3.7.3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY baden ./baden
COPY baden/settings_prod.ini ./baden/settings.ini

CMD [ "python", "baden/web.py" ]