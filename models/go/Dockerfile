# Go Monte Carlo Simulations
FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy go mod files
COPY go.mod ./

# Download dependencies
RUN go mod download

# Copy source
COPY montecarlo/ ./montecarlo/
COPY ostrom/ ./ostrom/
COPY motivation/ ./motivation/

# Build all binaries
RUN CGO_ENABLED=0 go build -o /montecarlo ./montecarlo/main.go
RUN CGO_ENABLED=0 go build -o /ostrom ./ostrom/main.go
RUN CGO_ENABLED=0 go build -o /motivation ./motivation/main.go

# Runtime image
FROM alpine:3.19

RUN adduser -D -s /bin/sh simuser
WORKDIR /app

COPY --from=builder /montecarlo /app/montecarlo
COPY --from=builder /ostrom /app/ostrom
COPY --from=builder /motivation /app/motivation

USER simuser

# Default to montecarlo, can override with docker-compose
ENTRYPOINT ["/app/montecarlo"]
