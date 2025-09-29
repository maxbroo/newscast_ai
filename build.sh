#!/bin/bash

# Install system dependencies
echo "Installing system dependencies..."

# Create required directories
mkdir -p episodes uploads templates static logs

# Set permissions
chmod 755 episodes uploads templates static logs

echo "Build completed successfully!"
