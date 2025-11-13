# Docker Setup for LaTeX Compilation

## What This Does

This setup lets you compile your LaTeX paper **without installing LaTeX** on your computer. Everything runs inside a Docker container with a complete TeX Live distribution.

## Installation

### macOS
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop from:
# https://docs.docker.com/desktop/install/mac-install/
```

### Windows
```bash
# Download and install Docker Desktop:
# https://docs.docker.com/desktop/install/windows-install/

# After installation, open PowerShell and verify:
docker --version
```

### Linux (Ubuntu/Debian)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Log out and back in for changes to take effect

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

### Linux (Fedora/RHEL)
```bash
sudo dnf install docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
# Log out and back in
```

## First Time Setup

After installing Docker:

```bash
# 1. Pull the LaTeX Docker image (one-time, ~2GB)
make docker-pull

# 2. Build your paper
make

# That's it! Your PDF is ready
```

## How It Works

The Makefile runs commands like this:
```bash
docker run --rm \
  -v $(pwd):/workdir \
  -w /workdir \
  texlive/texlive:latest \
  pdflatex main
```

This:
- Starts a temporary container with TeX Live
- Mounts your project directory inside
- Runs pdflatex on your files
- Removes the container when done
- Leaves the generated PDF on your computer

## Advantages

✅ **No local installation** - LaTeX stack is ~4-6GB, Docker handles it  
✅ **Consistent environment** - Same version everywhere  
✅ **Isolated** - Won't conflict with other software  
✅ **Easy updates** - `docker pull texlive/texlive:latest`  
✅ **Works offline** - After first pull, no internet needed  

## Docker Image Details

**Image:** `texlive/texlive:latest`  
**Size:** ~2GB  
**Includes:** Complete TeX Live distribution with all packages  
**Updates:** Regularly maintained by TeX Live team  

### Alternative: Smaller Image

If 2GB is too large, edit line 10 of Makefile:

```makefile
DOCKER_IMAGE = texlive/texlive:latest-small
```

The small image is ~400MB but may be missing some packages.

## Verifying Installation

```bash
# Check Docker is installed
docker --version

# Check Docker daemon is running  
docker ps

# Test with hello-world
docker run hello-world

# Pull LaTeX image
docker pull texlive/texlive:latest

# Test compilation
make
```

## Common Issues

### Docker daemon not running
```bash
# macOS/Windows: Open Docker Desktop application

# Linux:
sudo systemctl start docker
```

### Permission denied
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Then log out and back in
```

### Container conflicts
```bash
# If you see "container already exists"
docker rm <container-name>

# Or clean everything
docker system prune
```

### Disk space issues
```bash
# Docker images take space. Free up with:
docker system df           # Check usage
docker system prune -a     # Remove unused images
```

## Advanced: Custom Configuration

### Run with specific user (avoid root-owned files)
Edit Makefile line 14:
```makefile
DOCKER_RUN = docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(PWD):/workdir -w /workdir \
  $(DOCKER_IMAGE)
```

### Use specific TeX Live version
```makefile
DOCKER_IMAGE = texlive/texlive:TL2023-historic
```

### Add custom packages
Create `Dockerfile`:
```dockerfile
FROM texlive/texlive:latest
RUN tlmgr install <package-name>
```

Build and use:
```bash
docker build -t my-latex .
# Then edit Makefile to use my-latex
```

## Still Prefer Local Installation?

You can use your local LaTeX installation instead:

```bash
# Install TeX Live locally
# Then use:
make local

# This bypasses Docker and uses your local pdflatex
```

## Need Help?

- **Docker documentation:** https://docs.docker.com/
- **TeX Live image:** https://hub.docker.com/r/texlive/texlive
- **Issue tracker:** https://github.com/TeX-Live/texlive-docker

## Summary

1. Install Docker (one-time)
2. Run `make docker-pull` (one-time, ~2GB download)
3. Run `make` to build your paper (fast)
4. That's it!

No multi-gigabyte LaTeX installation needed. No configuration. No conflicts. Just Docker and Make.
