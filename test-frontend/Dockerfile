# Build context is the package root (parent dir). Needs access to both test-frontend/
# and js/ because the test-frontend aliases @pamfilico/admin-auth-react to ../js/src.
FROM node:20-alpine
WORKDIR /app/test-frontend

COPY test-frontend/package.json test-frontend/tsconfig.json test-frontend/next.config.js ./
COPY test-frontend/app ./app

# Sibling package source resolved via webpack alias (../js/src/index.ts)
COPY js /app/js

RUN npm install

ENV NEXT_TELEMETRY_DISABLED=1

EXPOSE 3000
CMD ["npm", "run", "dev"]
