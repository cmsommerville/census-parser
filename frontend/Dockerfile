FROM node:lts-alpine as build 
WORKDIR /app 
COPY package*.json ./
RUN npm install 
COPY . .
RUN npm run build 

FROM nginx:stable-alpine as production
COPY nginx.default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /var/www/frontend
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]