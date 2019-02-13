FROM dimagi/commcarehq_base as commcarehq

RUN npm install -g less

WORKDIR /app

COPY . /app


RUN cp docker/prodsettings.py localsettings.py
RUN bower install && \
     python manage.py collectstatic --noinput && \
     python manage.py compilejsi18n && \
     python manage.py fix_less_imports_collectstatic && \
     python manage.py compress

FROM nginx:1.15-alpine
COPY --from=commcarehq /app/staticfiles /usr/share/nginx/html
