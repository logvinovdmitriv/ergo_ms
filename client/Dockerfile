FROM node:18-bullseye-slim
WORKDIR /app

ENV ROLLUP_SKIP_NODEJS_NATIVE=true ROLLUP_FORCE_JS=true ROLLUP_DISABLE_NATIVE=true npm_config_optional=false

COPY package.json ./
RUN if [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm install; \
    elif [ -f yarn.lock ]; then yarn install; \
    else npm install --force; fi

# Source code will be mounted, so we don't copy it here.
EXPOSE 8001
# Use HOST 0.0.0.0 and port 8001 for dev
ENV HOST=0.0.0.0 PORT=8001 CHOKIDAR_USEPOLLING=true
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8001"]


