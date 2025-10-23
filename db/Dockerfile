FROM mysql:8.0

# Set environment variables
ENV MYSQL_ROOT_PASSWORD=password
ENV MYSQL_DATABASE=image_detection
ENV MYSQL_USER=app_user
ENV MYSQL_PASSWORD=app_password

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Add MySQL configuration to fix authentication issues
RUN echo "[mysqld]" >> /etc/mysql/conf.d/docker.cnf && \
    echo "default_authentication_plugin=mysql_native_password" >> /etc/mysql/conf.d/docker.cnf

# Expose MySQL port
EXPOSE 3306

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD mysqladmin ping -h localhost -u root -p$MYSQL_ROOT_PASSWORD || exit 1