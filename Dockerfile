FROM python:3.11.2

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia el archivo de requerimientos y el código de la aplicación al contenedor
COPY requirements.txt requirements.txt
COPY . .

# Instala las dependencias
RUN pip install -r requirements.txt

# Expone el puerto que usará la aplicación
EXPOSE 8000

# Define el comando de inicio de la aplicación
CMD ["gunicorn", "WarriorsNet.wsgi:application", "--bind", "0.0.0.0:8000"]S
