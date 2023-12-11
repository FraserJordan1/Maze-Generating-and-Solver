FROM python:3.10-slim

WORKDIR /usr/src/assignment_8
COPY . .
RUN pip install -r requirements.txt

CMD ["pytest a8_test.py"]