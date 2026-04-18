FROM ghcr.io/prefix-dev/pixi:0.46.0-jammy

WORKDIR /app

COPY pixi.toml pixi.lock ./
RUN pixi install --locked

COPY . .

RUN pixi run install-browsers

EXPOSE 8003
CMD ["pixi", "run", "python", "main.py", "serve", "--host", "0.0.0.0"]
