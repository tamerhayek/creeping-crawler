FROM ghcr.io/prefix-dev/pixi:0.46.0-jammy

WORKDIR /app

COPY pixi.toml pixi.lock ./
RUN pixi install --locked

COPY . .

EXPOSE 8004
CMD ["pixi", "run", "app"]
