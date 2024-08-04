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
package "App Service" {
    osa_server(app, "App Service", "FastAPI")
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
package "Jaeger" {
    osa_server(jaeger, "Jaeger", "Tracing")
}

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
django_admin --> db
app --> db
app --> elasticsearch
app --> redis
file_api --> minio
file_api --> db
etl --> db
etl --> elasticsearch
etl --> redis
rate_limit --> app
rate_limit --> auth
nginx --> app
nginx --> auth
nginx --> rate_limit
nginx --> django_admin
nginx --> file_api

@enduml
