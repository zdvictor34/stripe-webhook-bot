# Usamos Python 3.12 slim para evitar errores con imghdr
FROM python:3.12-slim

# Evitamos warnings de locales
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Carpeta de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Puerto que usará Flask
EXPOSE 5000

# Comando para arrancar el bot
CMD ["python3", "app.py"]

