# 1. Берем легкий образ Node.js
FROM node:20-alpine

# 2. Рабочая папка внутри контейнера
WORKDIR /app

# 3. Сначала копируем только package.json для кэширования библиотек
COPY package*.json ./
RUN npm install

# 4. Копируем остальной код
COPY . .

# 5. Открываем порт Vite
EXPOSE 5173

# 6. ВАЖНО: флаг --host нужен, чтобы Vite слушал запросы вне контейнера
CMD ["npm", "run", "dev", "--", "--host"]