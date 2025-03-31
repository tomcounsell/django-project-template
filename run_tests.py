#!/usr/bin/env python
"""
Test runner script for the Django Project Template.

This script provides a unified interface for running different types of tests:
- Unit tests
- Integration tests
- E2E tests
- Visual tests

It also supports generating coverage reports and running browser-based tests.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
import glob


def run_command(cmd, verbose=False):
    """Run a command and optionally print its output."""
    process = subprocess.run(
        cmd,
        shell=True,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    if verbose or process.returncode != 0:
        print(f"$ {cmd}")
        if process.stdout:
            print(process.stdout)
        if process.stderr:
            print(process.stderr)
    
    return process.returncode == 0


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Run tests with various options")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "e2e", "visual", "api", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML coverage report"
    )
    parser.add_argument(
        "--xml-report",
        action="store_true",
        help="Generate XML coverage report for CI"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Run browser-based tests"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in non-headless mode"
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=0,
        help="Slow down browser actions by specified milliseconds"
    )
    parser.add_argument(
        "--browser-type",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser type to use for testing"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate Django settings
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    
    # Run standard tests
    if args.type != "visual" and not args.browser:
        test_cmd = f"python tools/testing/test_manager.py run --category {args.type}"
        if args.verbose:
            test_cmd += " --verbose"
        
        if not run_command(test_cmd, args.verbose):
            sys.exit(1)
    
    # Run browser-based tests if requested
    if args.browser or args.type in ["e2e", "visual"]:
        patterns = []
        if args.type == "e2e":
            patterns = ["apps/**/tests/test_e2e_*.py", "apps/**/tests/test_*_browser.py"]
        elif args.type == "visual":
            patterns = ["apps/**/tests/test_visual_*.py", "apps/**/tests/test_screenshot_*.py"]
        elif args.type == "all":
            patterns = [
                "apps/**/tests/test_e2e_*.py", 
                "apps/**/tests/test_*_browser.py",
                "apps/**/tests/test_visual_*.py", 
                "apps/**/tests/test_screenshot_*.py"
            ]
        
        if patterns:
            test_files = []
            for pattern in patterns:
                test_files.extend(glob.glob(pattern))
            
            if test_files:
                browser_cmd = "python tools/testing/browser_test_runner.py"
                if args.no_headless:
                    browser_cmd += " --no-headless"
                if args.slow_mo > 0:
                    browser_cmd += f" --slow-mo {args.slow_mo}"
                if args.browser_type:
                    browser_cmd += f" --browser {args.browser_type}"
                if args.verbose:
                    browser_cmd += " --verbose"
                
                browser_cmd += " " + " ".join(test_files)
                
                if not run_command(browser_cmd, args.verbose):
                    sys.exit(1)
            elif args.verbose:
                print(f"No browser-based tests found for type: {args.type}")
    
    # Generate coverage reports if requested
    if args.coverage or args.html_report or args.xml_report:
        report_types = []
        if args.html_report:
            report_types.append("html")
        if args.xml_report:
            report_types.append("xml")
        if args.coverage and not (args.html_report or args.xml_report):
            report_types.append("term-missing")
        
        for report_type in report_types:
            coverage_cmd = f"python tools/testing/coverage_reporter.py --type {report_type}"
            if args.verbose:
                coverage_cmd += " --verbose"
            
            coverage_cmd += " apps"
            
            if not run_command(coverage_cmd, args.verbose):
                sys.exit(1)
    
    print("All tests completed successfully!")


if __name__ == "__main__":
    main()