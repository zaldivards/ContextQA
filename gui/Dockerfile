FROM node:lts-alpine

WORKDIR /app

EXPOSE 3000

COPY ./package*.json /app/

RUN npm install && npm i -g serve

COPY . /app/

RUN npm run build

ENTRYPOINT serve -s dist