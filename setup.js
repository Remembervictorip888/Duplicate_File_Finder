const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Check if Node.js is installed
function checkNode() {
  try {
    const nodeVersion = execSync('node --version', { encoding: 'utf-8' });
    console.log(`✓ Node.js version: ${nodeVersion.trim()}`);
    const versionNum = parseFloat(nodeVersion.trim().replace('v', ''));
    if (versionNum < 16.0) {
      console.error('✗ Node.js version must be 16.0 or higher');
      return false;
    }
    return true;
  } catch (error) {
    console.error('✗ Node.js is not installed or not in PATH');
    return false;
  }
}

// Check if npm is installed
function checkNpm() {
  try {
    const npmVersion = execSync('npm --version', { encoding: 'utf-8' });
    console.log(`✓ npm version: ${npmVersion.trim()}`);
    return true;
  } catch (error) {
    console.error('✗ npm is not installed or not in PATH');
    return false;
  }
}

// Check if dependencies are installed
function checkDependencies() {
  try {
    // Try to import a key dependency to see if node_modules exist
    require.resolve('react');
    console.log('✓ Dependencies are installed');
    return true;
  } catch (error) {
    console.log('✗ Dependencies need to be installed');
    return false;
  }
}

// Install dependencies
function installDependencies() {
  console.log('Installing dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✓ Dependencies installed successfully');
    return true;
  } catch (error) {
    console.error('✗ Failed to install dependencies');
    return false;
  }
}

// Start the development server
function startDevServer() {
  console.log('Starting development server...');
  
  // Use spawn to start the server and capture output
  const server = spawn('npm', ['run', 'dev'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    shell: true
  });

  server.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(output);
    
    // Check if the server is ready
    if (output.includes('ready in') && output.includes('http://localhost')) {
      const portMatch = output.match(/http:\/\/localhost:(\d{4,})/);
      if (portMatch) {
        const port = portMatch[1];
        console.log(`\n✓ Application is running at: http://localhost:${port}`);
        console.log('You can now open your browser and navigate to the above URL to use the application.');
      } else {
        console.log('\n✓ Development server is running');
      }
    }
  });

  server.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
  });

  server.on('close', (code) => {
    console.log(`Server process exited with code ${code}`);
  });

  // Keep the process running
  return server;
}

// Main setup function
async function main() {
  console.log('🔍 Checking system prerequisites...\n');
  
  // Check prerequisites
  const hasNode = checkNode();
  const hasNpm = checkNpm();
  
  if (!hasNode || !hasNpm) {
    console.error('\n❌ Prerequisites not met. Please install Node.js (version 16.0 or higher) and npm before proceeding.');
    return;
  }
  
  console.log('\n✓ All prerequisites are met');
  
  // Check and install dependencies if needed
  if (!checkDependencies()) {
    const installed = installDependencies();
    if (!installed) {
      console.error('\n❌ Failed to install dependencies. Please check your network connection and try again.');
      return;
    }
  }
  
  // Verify dependencies after installation
  if (!checkDependencies()) {
    console.error('\n❌ Dependencies are still not properly installed');
    return;
  }
  
  console.log('\n🚀 Starting the application...\n');
  
  // Start the development server
  const server = startDevServer();
  
  // Also start the TypeScript compiler in watch mode in the background
  console.log('🔧 TypeScript compilation in watch mode started in the background');
  const tsc = spawn('npx', ['tsc', '--noEmit', '--watch'], {
    stdio: 'ignore' // Run in background
  });
  
  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\n\n🛑 Shutting down the application...');
    server.kill();
    tsc.kill();
    process.exit(0);
  });
}

// Run the setup
main();