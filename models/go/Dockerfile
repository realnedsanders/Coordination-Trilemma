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
COPY bifurcation/ ./bifurcation/

# Build all binaries
RUN CGO_ENABLED=0 go build -o /montecarlo ./montecarlo/main.go
RUN CGO_ENABLED=0 go build -o /ostrom ./ostrom/main.go
RUN CGO_ENABLED=0 go build -o /motivation ./motivation/main.go
RUN CGO_ENABLED=0 go build -o /bifurcation ./bifurcation/main.go

# Runtime image
FROM alpine:3.19

WORKDIR /app

COPY --from=builder /montecarlo /app/montecarlo
COPY --from=builder /ostrom /app/ostrom
COPY --from=builder /motivation /app/motivation
COPY --from=builder /bifurcation /app/bifurcation

# Default to montecarlo, can override with docker-compose
ENTRYPOINT ["/app/montecarlo"]
