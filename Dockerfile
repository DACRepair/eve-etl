FROM laudio/pyodbc:1.0.4

WORKDIR /source
COPY main.py .
COPY requirements.txt .
COPY eve_etl/ ./eve_etl
COPY templates/ ./templates
COPY static/ ./static

RUN pip install -r requirements.txt
RUN touch ./config.ini

EXPOSE 5555

ENTRYPOINT python3
CMD main.py