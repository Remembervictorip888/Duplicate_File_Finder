# Dependencies Documentation

This document provides an overview of all project dependencies, their purposes, and update status.

## Security Considerations

The application implements several security measures to protect against XSS and other vulnerabilities:

1. **Content Security Policy (CSP)**: Implemented both in the Electron main process and in the HTML meta tag to restrict resource loading
2. **Context Isolation**: Ensures the renderer process is isolated from the main process
3. **Secure IPC Communication**: Uses contextBridge to expose only necessary APIs to the renderer process
4. **Electron Security**: Updated to the latest version with security patches

## Frontend Dependencies (Node.js/NPM)

### Core Dependencies
- **react**: ^18.2.0 - Frontend library for building user interfaces
- **react-dom**: ^18.2.0 - React package for DOM-specific methods
- **@vitejs/plugin-react**: ^4.2.1 - Vite plugin for React projects with Fast Refresh

### Development Dependencies
- **typescript**: ^5.3.3 - Typed superset of JavaScript that compiles to plain JavaScript
- **vite**: ^5.0.12 - Next generation frontend tooling framework
- **electron**: ^28.2.0 - Framework for building cross-platform desktop applications with security features
- **electron-builder**: ^24.9.1 - Solution to package and build Electron apps
- **electron-packager**: ^17.1.2 - Alternative solution for packaging Electron apps
- **concurrently**: ^8.2.2 - Run multiple commands concurrently in npm scripts
- **webpack**: ^5.89.0 - Static module bundler for modern JavaScript applications
- **webpack-cli**: ^5.1.4 - Command line interface for webpack
- **webpack-dev-server**: ^4.15.1 - Development server for webpack
- **ts-loader**: ^9.5.1 - TypeScript loader for webpack
- **css-loader**: ^6.9.1 - CSS loader for webpack
- **style-loader**: ^3.3.4 - Style loader for webpack
- **html-webpack-plugin**: ^5.6.0 - Simplifies creation of HTML files
- **jest**: ^29.7.0 - JavaScript testing framework
- **@testing-library/react**: ^14.1.2 - React DOM testing utilities
- **ts-jest**: ^29.1.2 - Preprocessor for Jest to handle TypeScript
- **@types/jest**: ^29.5.11 - TypeScript definitions for Jest
- **@types/react**: ^18.2.48 - TypeScript definitions for React
- **@types/react-dom**: ^18.2.18 - TypeScript definitions for React DOM
- **@types/node**: ^20.11.5 - TypeScript definitions for Node.js

## Backend Dependencies (Python)

### Core Dependencies
- **xxhash**: ^3.4.1 - Extremely fast non-cryptographic hash algorithm, used for fast file content comparison
- **Pillow**: ^10.0.0 - Python Imaging Library fork, used for image processing operations
- **imagehash**: ^4.3.1 - Perceptual hashing module for finding visually similar images
- **send2trash**: ^1.8.2 - Cross-platform module to move files to system trash/recycle bin safely

### Optional Dependencies
- **aiofiles**: ^23.0.0 - Provides async file operations if needed for future enhancements
- **pyinstaller**: Used for creating standalone executables from Python scripts (not in requirements.txt but mentioned in docs)

## Why These Updates Were Necessary

### Frontend Updates
1. **Electron 28.2.0**: The previous version (22.0.0) was significantly outdated. Electron 28 includes security fixes, performance improvements, and compatibility with modern web standards.

2. **TypeScript 5.3.3**: The previous version was outdated, and this update provides better type checking, new language features, and improved performance.

3. **Vite 5.0.12**: The previous version was outdated, and this update includes performance improvements, bug fixes, and new features.

4. **Updated React ecosystem**: Updated type definitions and related packages to maintain compatibility.

### Backend Updates
1. **xxhash 3.4.1**: Latest version with performance improvements and bug fixes.

2. **Pillow 10.0.0**: Latest major version with security fixes and new image format support.

3. **imagehash 4.3.1**: Latest version with improved perceptual hashing algorithms.

4. **send2trash 1.8.2**: Latest version with better cross-platform compatibility.

## Installation

### Frontend Dependencies
```bash
npm install
```

### Backend Dependencies
```bash
pip install -r requirements.txt
```

## Development and Production Usage

### Development
- Use `npm run dev` for frontend development with hot reloading
- Use `npm run electron-dev` for Electron app development
- Use `python main.py` for backend CLI development

### Production
- Use `npm run build` to build the frontend
- Use `npm run electron-build` to create a distributable desktop app
- Use `npm run electron-pack` as an alternative packaging method
- Use `pyinstaller` to create standalone Python executable (alternative method)

## Security Measures Implemented

1. Electron security: Updated to newer version with security patches
2. Content Security Policy: Implemented to prevent XSS attacks
3. Context isolation: Ensures renderer process cannot directly access Node.js APIs
4. Python packages: Updated to latest versions with security fixes
5. Dependencies regularly reviewed for vulnerabilities

## Performance Improvements

1. Faster build times with updated Vite
2. Better memory usage with updated libraries
3. Improved file processing with latest xxhash implementation
4. More efficient image processing with updated Pillow and imagehash