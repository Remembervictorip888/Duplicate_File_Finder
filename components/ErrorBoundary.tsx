import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center justify-center p-4">
          <div className="max-w-2xl bg-gray-800 rounded-lg p-6 shadow-lg">
            <h1 className="text-2xl font-bold text-red-500 mb-4">Application Error</h1>
            <p className="mb-4">
              An error occurred in the application. Please check the console for more details.
            </p>
            <details className="mb-4 bg-gray-700 p-4 rounded">
              <summary className="cursor-pointer">Error Details</summary>
              <pre className="text-red-400 mt-2 p-2 bg-gray-900 rounded overflow-auto">
                {this.state.error?.stack}
              </pre>
            </details>
            <button
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors"
              onClick={() => window.location.reload()}
            >
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;