# Coordination Trilemma - Computational Models
#
# Using python:3.11-slim-bookworm instead of Alpine because:
# - Scientific packages (numpy, scipy, mesa) have pre-built wheels for glibc
# - Alpine uses musl libc which requires compilation from source
# - Results in faster builds and smaller final image
#
# To use Alpine, you'd need: apk add --no-cache gcc musl-dev python3-dev
# and compilation would take 10+ minutes

FROM python:3.11-slim-bookworm AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For matplotlib
    libfreetype6-dev \
    # For general build needs
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash modeluser
WORKDIR /app

# Install Python dependencies
COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY python/ ./python/
COPY README.md .

# Change ownership
RUN chown -R modeluser:modeluser /app

USER modeluser

# Default command
CMD ["python", "-m", "python.abm.corruption_dynamics", "--help"]

# ---
# Development stage with additional tools
FROM base AS dev

USER root

RUN pip install --no-cache-dir \
    ipython \
    jupyterlab

USER modeluser

# Expose Jupyter port
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--NotebookApp.token=''"]
