FROM python:3.12.3-slim

RUN apt-get update

WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY help.json /code
COPY opensplitbot.py /code

CMD ["python", "opensplitbot.py"]
