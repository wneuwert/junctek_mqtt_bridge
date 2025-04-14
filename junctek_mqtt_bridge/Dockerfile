ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN pip install paho-mqtt

COPY run.py /run.py
CMD ["python", "/run.py"]
