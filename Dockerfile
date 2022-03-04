FROM python:3.6-alpine
MAINTAINER Geir Atle Hegsvold "geir.hegsvold@sesam.io"

COPY ./service /service

RUN apk update
RUN pip install --upgrade pip
RUN pip install -r /service/requirements.txt

EXPOSE 5000/tcp
ENTRYPOINT ["python"]
CMD ["./service/service.py"]

