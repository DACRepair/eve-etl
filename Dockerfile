FROM laudio/pyodbc:1.0.4

WORKDIR /source
COPY main.py .
COPY requirements.txt .
COPY eve_etl/ ./eve-etl
COPY templates/ ./templates
COPY static/ ./static

EXPOSE 5555

ENTRYPOINT python
CMD main.py