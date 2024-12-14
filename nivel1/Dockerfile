FROM python:3.9

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias primero para aprovechar la cache
COPY requirements.txt /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . /app

# Exponer el puerto 5000
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD python app/main.py
