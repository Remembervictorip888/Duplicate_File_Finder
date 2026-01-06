"""
Test runner for the duplicate file finder application.
This module runs both basic and comprehensive tests with configuration options.
"""
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

from test_engine import run_self_test
from test_suite import run_comprehensive_test
from utils.logger import setup_logger


def run_all_tests(config):
    """
    Run all tests based on the configuration.
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Setup logger for the test runner
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    runner_logger = setup_logger('test_runner', f'test_runner_{timestamp}.log', level=20)  # INFO level
    
    runner_logger.info("Starting test runner for duplicate file finder")
    runner_logger.info(f"Configuration: {config}")
    
    results = {
        'basic_tests_passed': None,
        'comprehensive_tests_passed': None,
        'start_time': time.time()
    }
    
    if config.run_basic_tests:
        runner_logger.info("Running basic self-tests...")
        print("Running basic self-tests...")
        results['basic_tests_passed'] = run_self_test()
        print()
    
    if config.run_comprehensive_tests:
        runner_logger.info("Running comprehensive tests...")
        print("Running comprehensive tests...")
        results['comprehensive_tests_passed'] = run_comprehensive_test()
        print()
    
    results['end_time'] = time.time()
    results['duration'] = results['end_time'] - results['start_time']
    
    # Summary
    runner_logger.info(f"Test run completed in {results['duration']:.2f} seconds")
    
    basic_result = results['basic_tests_passed']
    comp_result = results['comprehensive_tests_passed']
    
    if basic_result is not None:
        runner_logger.info(f"Basic tests: {'PASSED' if basic_result else 'FAILED'}")
    if comp_result is not None:
        runner_logger.info(f"Comprehensive tests: {'PASSED' if comp_result else 'FAILED'}")
    
    # Overall result
    all_passed = True
    if basic_result is not None:
        all_passed = all_passed and basic_result
    if comp_result is not None:
        all_passed = all_passed and comp_result
    
    runner_logger.info(f"Overall result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    print(f"Test run completed in {results['duration']:.2f} seconds")
    print(f"Overall result: {'🎉 ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    return all_passed


def main():
    """
    Main function to parse arguments and run tests.
    """
    parser = argparse.ArgumentParser(description='Test runner for duplicate file finder')
    parser.add_argument('--basic', action='store_true', help='Run basic self-tests')
    parser.add_argument('--comprehensive', action='store_true', help='Run comprehensive tests')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run all tests
    if not args.basic and not args.comprehensive and not args.all:
        args.all = True
    
    # Create a simple config object
    class Config:
        pass
    
    config = Config()
    config.run_basic_tests = args.basic or args.all
    config.run_comprehensive_tests = args.comprehensive or args.all
    
    # Run the tests
    success = run_all_tests(config)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()