-- Создаем базу данных
CREATE DATABASE IF NOT EXISTS movies ON CLUSTER company_cluster;

-- Создаем локальные таблицы на каждой ноде
CREATE TABLE IF NOT EXISTS movies.events ON CLUSTER company_cluster (
    event_type String,
    source String,
    timestamp String,
    data String
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events_table', '{replica}')
ORDER BY timestamp;

-- Создаем распределенную таблицу, которая будет объединять данные со всех нод
CREATE TABLE IF NOT EXISTS movies.events_table ON CLUSTER company_cluster AS movies.events
ENGINE = Distributed(company_cluster, movies, events, rand());
