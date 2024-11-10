FROM golang:1.23-alpine AS build

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN go build -o main cmd/api/main.go

FROM alpine:3.20.1 AS prod
WORKDIR /app
COPY --from=build /app/main /app/main
ENV PORT=3003
ENV APP_ENV=local

ENV DB_HOST=db_postgres
ENV DB_PORT=5432
ENV DB_DATABASE=postgres
ENV DB_USERNAME=postgres
ENV DB_PASSWORD=postgres
ENV DB_SCHEMA=public

EXPOSE ${PORT}
CMD ["./main"]