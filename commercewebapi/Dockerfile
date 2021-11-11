FROM node

WORKDIR /usr/src/app/

COPY . /usr/src/app/
RUN npm install

EXPOSE 8001
CMD [ "node", "server.js" ]
