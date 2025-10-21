# сборка
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
# игнорируем конфликт пиров, чтобы не трогать пакетные версии
RUN npm ci --legacy-peer-deps --no-audit --no-fund
COPY . ./
RUN npm run build

# отдача билда (если у тебя уже есть такой этап — оставь свой)
FROM nginx:1.25-alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
