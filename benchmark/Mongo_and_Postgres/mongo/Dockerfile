FROM mongo
RUN mkdir -p /app/data
WORKDIR /app/data
COPY users.csv /app/data
COPY movies.csv /app/data
COPY likes.csv /app/data
COPY import.sh /app/data
RUN chmod +x /app/data/import.sh
CMD ["sh", "-c", "/app/data/import.sh"]
