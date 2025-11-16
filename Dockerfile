# Estágio 1: Build
# Usamos uma imagem oficial do Python. Escolha a versão exata do seu projeto.
# A variante "slim" é mais pequena, ideal para produção.
FROM python:3.12-slim AS builder

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala o 'uv', a nossa ferramenta de gestão de pacotes
RUN pip install uv

# Copia os ficheiros de requisitos primeiro.
# Isto aproveita o cache do Docker: se estes ficheiros não mudarem,
# o Docker não reinstala as dependências, acelerando o build.
COPY requirements.txt requirements-dev.txt ./

# Instala as dependências de produção usando 'uv'
# Usamos --system para instalar no ambiente global do contêiner
RUN uv pip install --system --no-cache-dir -r requirements.txt


# Estágio 2: Final
# Começamos de novo com uma imagem Python "slim" limpa para a imagem final.
# Isto torna a imagem final muito mais pequena, pois não inclui
# as ferramentas de build e dependências de desenvolvimento.
FROM python:3.12-slim

ARG CUSTOMER_PROFILE=default

# Define o diretório de trabalho
WORKDIR /app

# (IMPORTANTE) Instala o driver ODBC para o SQL Server
# Esta é a parte "mágica" que instala as dependências de sistema operativo.
# Este exemplo é para Debian/Ubuntu. Para outras bases de SO, os comandos podem mudar.
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  gnupg \
  unixodbc-dev \
  # Adiciona a chave GPG da Microsoft de forma segura
  && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
  # Adiciona o repositório da Microsoft para Debian 12 (Bookworm)
  && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
  # Atualiza as listas de pacotes
  && apt-get update \
  # --- ALTERAÇÃO AQUI ---
  # Instala o driver ODBC 17, aceitando o EULA
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
  # Limpa o cache
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copia as dependências já instaladas do estágio "builder"
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv

# Copia o código da sua aplicação para o contêiner

# Copia o código do "core"
COPY core/ /app/core/

# Copia os scripts da raiz
COPY pyproject.toml /app/
COPY run_*.py /app/

# Copia os específicos do perfil de cliente
COPY customer_mappers/${CUSTOMER_PROFILE}/ /app/customer_mappers/${CUSTOMER_PROFILE}/

# Copia o mapper default (comum a todos os clientes)
COPY customer_mappers/__init__.py /app/customer_mappers/
COPY customer_mappers/default/ /app/customer_mappers/default/

# Define o comando padrão que será executado quando o contêiner arrancar
# (para o serviço). Pode ser sobreposto na linha de comando.
CMD ["python", "run_service.py"]