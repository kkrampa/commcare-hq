FROM dimagi/commcarehq_base

RUN npm install -g less 

WORKDIR /app

COPY . /app


RUN cp docker/prodsettings.py localsettings.py
RUN bower install && \
     python manage.py collectstatic --noinput && \
     python manage.py compilejsi18n && \
     python manage.py fix_less_imports_collectstatic && \
     python manage.py compress
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
