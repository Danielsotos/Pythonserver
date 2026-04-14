FROM postgres:16

ENV POSTGRES_DB=robotsdb
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
  CMD pg_isready -U postgres -d robotsdb || exit 1

