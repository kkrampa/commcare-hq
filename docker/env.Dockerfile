FROM dimagi/commcarehq_base

RUN npm install -g less 

WORKDIR /app

COPY . /app


RUN cp docker/prodsettings.py localsettings.py
RUN bower install
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
