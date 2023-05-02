# Use a imagem oficial do Python 3.9 como base
FROM python:3.9-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo de requisitos para instalar as dependências
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o script para o diretório de trabalho
COPY LoadTester.py .

# Defina a variável de ambiente PYTHONUNBUFFERED para que os logs do Python sejam exibidos corretamente
ENV PYTHONUNBUFFERED=1

# Execute o script quando o contêiner for iniciado
CMD ["python", "LoadTester.py"]

# Build & Run
# docker build -t load-tester .
# docker run -it load-tester
# docker run -it -e URL=<url> -e AUTH_HEADER=<auth_header> -e DATA=<data> -e NUM_USERS=<num_users> -e NUM_REQUESTS=<num_requests> load-tester

