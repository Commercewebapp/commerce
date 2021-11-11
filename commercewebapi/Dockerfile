FROM node

WORKDIR /usr/src/app/

RUN npm install
COPY . /usr/src/app/

EXPOSE 8001
CMD [ "node", "server.js" ]
