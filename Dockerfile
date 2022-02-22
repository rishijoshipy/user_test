FROM python:3

RUN mkdir /static

RUN pip3 install --upgrade pip

WORKDIR /code

COPY requirements.txt /code/

# RUN pip3 install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# RUN apt-get install -y postgresql
# RUN apt-get install -y python-dev libpq-dev

COPY . /code/

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

