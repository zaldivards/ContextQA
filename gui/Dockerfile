FROM node:lts-alpine

WORKDIR /app

COPY ./package*.json /app/

RUN npm install && npm i -g serve

COPY . /app/

RUN npm run build

CMD serve -s dist