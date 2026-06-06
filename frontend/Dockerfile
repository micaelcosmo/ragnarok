# Frontend Ragnarok — estáticos servidos por nginx.
FROM nginx:1.27-alpine

# Remove config default e injeta a nossa (proxy /api -> backend).
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/ragnarok.conf

# Copia os arquivos estáticos da aplicação.
COPY index.html /usr/share/nginx/html/index.html
COPY progresso.html /usr/share/nginx/html/progresso.html
COPY css /usr/share/nginx/html/css
COPY js /usr/share/nginx/html/js

EXPOSE 80
