FROM node:18-alpine as builder

WORKDIR /app

COPY microservices-frontend/package.json .
COPY microservices-frontend/pnpm-lock.yaml .

RUN npm install -g pnpm

RUN pnpm install --frozen-lockfile

COPY microservices-frontend/ .

RUN pnpm run build

FROM nginx:stable-alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]