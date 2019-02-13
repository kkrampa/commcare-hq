FROM kkrampa/commcarehq as commcarehq

FROM nginx:1.15-alpine
COPY --from=commcarehq /app/staticfiles /usr/share/nginx/html/static
