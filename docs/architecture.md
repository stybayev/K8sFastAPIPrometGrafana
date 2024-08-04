@startuml
!define osaPuml https://raw.githubusercontent.com/Crashedmind/PlantUML-opensecurityarchitecture2-icons/master
!include osaPuml/Common.puml
!include osaPuml/Hardware/all.puml
!include osaPuml/Server/all.puml
!include osaPuml/Site/all.puml

' Services
package "Auth Service" {
    osa_server(auth, "Auth Service", "FastAPI + PostgreSQL")
}

package "Django Admin" {
    osa_server(django_admin, "Django Admin", "Django + PostgreSQL")
}
package "Movie search" {
    osa_server(movie_search, "Movie search", "FastAPI")
}
package "File API Service" {
    osa_server(file_api, "File API Service", "FastAPI + Minio")
}
package "ETL Service" {
    osa_server(etl, "ETL Service", "Python + PostgreSQL + Elasticsearch")
}
package "Rate Limit Service" {
    osa_server(rate_limit, "Rate Limit Service", "Custom")
}
package "Nginx" {
    osa_server(nginx, "Nginx", "Reverse Proxy")
}

' Jaeger Tracing
osa_server(jaeger, "Jaeger", "Tracing")

' Databases
package "Databases" {
    osa_server(db, "PostgreSQL", "Database")
    osa_server(elasticsearch, "Elasticsearch", "Database")
    osa_server(redis, "Redis", "Cache")
    osa_server(minio, "Minio", "Object Storage")
}

' Connections
auth --> db
auth --> redis
auth --> jaeger
auth --> movie_search
auth --> django_admin
django_admin --> db
movie_search --> db
movie_search --> elasticsearch
movie_search --> redis
file_api --> minio
file_api --> db
etl --> db
etl --> elasticsearch
etl --> redis
rate_limit --> movie_search
rate_limit --> auth
nginx --> auth
nginx --> movie_search
nginx --> rate_limit
nginx --> django_admin
nginx --> file_api

@enduml
