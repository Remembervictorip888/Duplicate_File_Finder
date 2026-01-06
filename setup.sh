#!/bin/bash

# Duplicate Image Finder - Automated Setup Script for Linux/Mac

echo -e "\033[1;33m🔍 Checking system prerequisites...\033[0m"

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "\033[1;32m✓ Node.js version: $NODE_VERSION\033[0m"
    
    # Extract major version number
    VERSION_NUM=$(echo $NODE_VERSION | sed 's/v//' | cut -d'.' -f1)
    if [ "$VERSION_NUM" -lt 16 ]; then
        echo -e "\033[1;31m✗ Node.js version must be 16.0 or higher\033[0m"
        exit 1
    fi
else
    echo -e "\033[1;31m✗ Node.js is not installed or not in PATH\033[0m"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "\033[1;32m✓ npm version: $NPM_VERSION\033[0m"
else
    echo -e "\033[1;31m✗ npm is not installed or not in PATH\033[0m"
    exit 1
fi

echo -e "\n\033[1;32m✓ All prerequisites are met\033[0m"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo -e "\033[1;32m✓ Dependencies already installed\033[0m"
else
    echo -e "\n\033[1;33m📦 Installing dependencies...\033[0m"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "\n\033[1;31m✗ Failed to install dependencies\033[0m"
        exit 1
    fi
    echo -e "\033[1;32m✓ Dependencies installed successfully\033[0m"
fi

echo -e "\n\033[1;36m🚀 Starting the application...\033[0m"

# Start the development server
npm run dev