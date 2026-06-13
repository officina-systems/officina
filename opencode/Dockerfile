# OpenCode Docker service
# Implementacion B: WorkspaceRuntimeProvider como servicio Docker
#
# Monta el repo como workspace :rw
# Apunta a FastAPI:8000 como Cognitive Provider
# Puerto 3100: opencode serve

FROM node:20-alpine
WORKDIR /workspace

# Instalar opencode globalmente en el contenedor
RUN npm install -g opencode-ai@1.16.2

# Directorio de config XDG dentro del contenedor
ENV XDG_CONFIG_HOME=/workspace/.opencode/config
ENV XDG_DATA_HOME=/workspace/.opencode/data

EXPOSE 3100

# serve mode: headless, acepta conexiones de FastAPI
CMD ["opencode", "serve", "--port", "3100", "--hostname", "0.0.0.0"]
