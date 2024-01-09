FROM python:3-alpine

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY monitor.py /app/
COPY authenticator.py /app/
COPY spotiplot.env /app/

RUN ["mkdir", "cache"]

CMD ["python", "authenticator.py"]