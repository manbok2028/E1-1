FROM nginx:1.27-alpine

LABEL org.opencontainers.image.title="E1-1 Workstation Web" \
      org.opencontainers.image.description="Custom NGINX image for the developer workstation mission" \
      org.opencontainers.image.source="https://github.com/manbok2028/E1-1"

ENV APP_MODE=workstation-lab \
    NGINX_ENTRYPOINT_QUIET_LOGS=0

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY app/ /usr/share/nginx/html/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
