# Stage dev: Vite dev server with hot-reload (used by docker compose watch)
FROM node:22-alpine AS dev

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

# Stage 1: build (production)
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

# Vite bakes env vars at build time — accept via build arg
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY . .
RUN npm run build

# Stage 2: serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
