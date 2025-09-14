#!/bin/bash

# Docker Desktop Installation Guide for Windows
echo "==================================="
echo "   Docker Desktop Setup Guide"
echo "==================================="
echo

echo "Step 1: Download Docker Desktop"
echo "Visit: https://www.docker.com/products/docker-desktop/"
echo "Download: Docker Desktop for Windows"
echo

echo "Step 2: Install Docker Desktop"
echo "- Run the downloaded installer"
echo "- Follow the installation wizard"
echo "- Enable WSL 2 backend when prompted"
echo "- Restart your computer"
echo

echo "Step 3: Verify Installation"
echo "After restart, run these commands:"
echo "docker --version"
echo "docker-compose --version"
echo

echo "Step 4: Start DocFlow with Docker"
echo "cd /c/DocFlow"
echo "docker-compose up -d"
echo

echo "==================================="
echo "Alternative: Local Development Setup"
echo "==================================="
echo

echo "If Docker installation fails, you can run:"
echo "./setup-local.sh"
echo

read -p "Press Enter to continue..."