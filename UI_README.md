# Duplicate File Finder UI

This is a simple UI for the Duplicate File Finder application built with React and TypeScript.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

### For Development (Web):
```bash
npm run dev:web
```
This will start a development server on http://localhost:3000

### For Electron Desktop App:
```bash
npm start
```

## Features

- Directory selection for scanning
- Multiple scan methods (hash, filename, size, all)
- File filtering by extension and size
- Advanced grouping and custom rules options
- Auto-selection strategies (oldest, newest, lowest resolution)
- Visual display of duplicate groups
- Selective deletion of duplicates
- Progress tracking during scans

## Project Structure

```
src/
├── App.tsx           # Main application component
├── index.tsx         # Entry point
├── styles/
│   ├── main.css      # Main styles
│   └── progress.css  # Progress bar styles
```

## Technologies Used

- React (v18) with TypeScript
- Webpack for bundling
- CSS for styling
- Electron for desktop application

## Mock Data

The UI currently uses mock data for demonstration. In a full implementation, this would connect to the Python backend via Electron's IPC mechanism.

## Building for Production

```bash
npm run build
```

This will create a production-ready bundle in the `dist/` folder.