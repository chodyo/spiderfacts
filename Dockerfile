FROM python:3
# FROM nikolaik/python-nodejs

ADD . app
WORKDIR /app

# RUN npm install -g nodemon
RUN pip install -r requirements.txt

CMD [ "python", "./src/spiderfacts.py" ]
# CMD [ "nodemon", "--exec", "python ./src/spiderfacts.py", "--verbose" ]


# docker build -t spiderfacts .
# docker run -e SPIDER_FACTS_TOKEN=xoxb-############-######################## spiderfacts