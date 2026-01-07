# Duplicate File Finder

A comprehensive tool to find and manage duplicate files with both command-line and GUI interfaces.

## Features

- **Multiple Detection Methods**: Hash comparison, filename similarity, size comparison, and image similarity
- **Advanced Grouping**: Group potential duplicates using custom rules and patterns
- **Safe File Operations**: Auto-select and delete duplicates with various strategies
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern UI**: React/TypeScript frontend with Electron integration
- **Comprehensive Testing**: Full test coverage for both backend and frontend

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd duplicate-file-finder
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Usage

### Command Line Interface

```bash
# Find duplicates in a directory
python main.py /path/to/directory

# Find duplicates with specific settings
python main.py /path/to/directory --strategy oldest --delete --extensions .jpg .png .pdf

# Use specific detection method
python main.py /path/to/directory --method hash --min-size 0.1 --max-size 100
```

### Graphical User Interface

```bash
# Start the Electron application (with development server)
npm start
```

## Testing

The application includes comprehensive testing for both backend and frontend components:

### Run Backend Tests
```bash
python -m pytest test_engine.py
# Or run directly:
python test_engine.py
```

### Run UI Tests
```bash
python test_ui_engine.py
```

### Run Complete Test Suite
```bash
python test_suite_enhanced.py
```

The test suite includes:
- **Backend Tests**: All core functionality including scanning, hashing, duplicate detection, file operations, data models, and database functionality
- **UI Tests**: Frontend components, TypeScript compilation, build process, and Electron integration
- **Integration Tests**: Verification that backend and frontend work together
- **Performance Tests**: Basic performance checks to ensure application responsiveness
- **Edge Case Tests**: Handling of empty directories, non-existent paths, and other edge cases

## Architecture

The application is organized into several key components:

- **core/**: Core functionality including scanning, hashing, duplicate detection, and file operations
- **utils/**: Utility functions for logging and configuration
- **src/**: React/TypeScript frontend components
- **electron/**: Electron integration files for desktop application
- **tests/**: Various test modules for different aspects of the application

## Technologies Used

- **Backend**: Python 3.7+
- **Frontend**: React, TypeScript, CSS
- **Desktop**: Electron
- **Build Tools**: Webpack, Vite
- **Testing**: Pytest, Jest, React Testing Library

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python test_suite_enhanced.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
