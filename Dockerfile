FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy local code to the container image.
ENV APP_HOME /workspace
#ENV PORT 8080
WORKDIR $APP_HOME

COPY *.* $APP_HOME/

# Install production dependencies.
#RUN pip install --no-cache-dir -r requirements.txt
RUN ls -la

RUN uv sync --frozen

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

#RUN uv venv
#RUN source .venv/bin/activate

ENTRYPOINT ["uv", "run", "."]