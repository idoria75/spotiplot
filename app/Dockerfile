FROM python:3-alpine

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN ["mkdir", "cache"]

COPY authenticator.py /app/
COPY spotiplot.env /app/

COPY monitor.py /app/

CMD ["python", "authenticator.py"]