FROM node:20-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install

#Listen on 3001 and all interfaces
ENV PORT=3001
ENV HOST=0.0.0.0

COPY . .
EXPOSE 3001
CMD ["npm","start"]