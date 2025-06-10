FROM python:3.11-slim

WORKDIR /app

# Устанавливаем необходимые пакеты
RUN apt update && apt install -y \
    build-essential \
    cmake \
    curl \
    git \
    ccache \
    ninja-build && \
    pip install --upgrade pip

# Задаём Ninja как генератор CMake по умолчанию
ENV CMAKE_GENERATOR=Ninja

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем llama-cpp-python с CPU-бэкендом отдельно
RUN pip install llama-cpp-python[server] --config-settings=llama-cpp:llama_backend=cpu && \
    pip install -r requirements.txt

# Копируем остальной проект
COPY . .

# Делаем скрипт запуска исполняемым
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
