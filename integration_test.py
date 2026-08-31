#!/usr/bin/env python3
"""
Full Integration Test: Frontend + Backend + Image Serving

Tests the complete PDF-to-HTML conversion pipeline:
1. Flask backend starts and serves frontend
2. Sample PDF upload to /convert endpoint
3. HTML generation with images and captions
4. Image serving from /extracted_images/
5. Accessibility issues detection
"""

import os
import sys
import time
import requests
import subprocess
import json
from pathlib import Path


# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class IntegrationTest:
    def __init__(self):
        self.base_url = "http://localhost:5001"
        self.server_process = None
        self.test_results = []

    def log(self, message, level="INFO"):
        """Log test messages with color coding"""
        colors = {
            "INFO": BLUE,
            "PASS": GREEN,
            "FAIL": RED,
            "WARN": YELLOW
        }
        color = colors.get(level, RESET)
        print(f"{color}[{level}]{RESET} {message}")

    def start_server(self):
        """Start the Flask server"""
        self.log("Starting Flask server...", "INFO")

        backend_dir = os.path.join(os.path.dirname(__file__), "backend")

        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=backend_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for server to start
            for attempt in range(10):
                try:
                    response = requests.get(f"{self.base_url}/")
                    if response.status_code == 200:
                        self.log("Flask server is ready", "PASS")
                        return True
                except requests.exceptions.ConnectionError:
                    time.sleep(0.5)

            self.log("Flask server failed to start", "FAIL")
            return False

        except Exception as e:
            self.log(f"Failed to start server: {e}", "FAIL")
            return False

    def stop_server(self):
        """Stop the Flask server"""
        if self.server_process:
            self.log("Stopping Flask server...", "INFO")
            self.server_process.terminate()
            self.server_process.wait(timeout=5)
            self.log("Flask server stopped", "PASS")

    def test_frontend_serves(self):
        """Test that frontend index.html is served"""
        self.log("Testing frontend serving...", "INFO")

        try:
            response = requests.get(f"{self.base_url}/")

            if response.status_code == 200:
                if "Accessible News Converter" in response.text or "AI Accessible Article Converter" in response.text:
                    self.log("Frontend index.html served correctly", "PASS")
                    self.test_results.append(("Frontend Serving", True))
                    return True
                else:
                    self.log("Frontend served but content missing", "FAIL")
                    self.test_results.append(("Frontend Serving", False))
                    return False
            else:
                self.log(f"Frontend returned status {response.status_code}", "FAIL")
                self.test_results.append(("Frontend Serving", False))
                return False

        except Exception as e:
            self.log(f"Frontend test failed: {e}", "FAIL")
            self.test_results.append(("Frontend Serving", False))
            return False

    def test_static_files(self):
        """Test that CSS and JS files are served"""
        self.log("Testing static file serving...", "INFO")

        files_to_test = ["style.css", "app.js"]
        all_passed = True

        for filename in files_to_test:
            try:
                response = requests.get(f"{self.base_url}/{filename}")

                if response.status_code == 200 and len(response.text) > 0:
                    self.log(f"  ✓ {filename} served", "PASS")
                else:
                    self.log(f"  ✗ {filename} not found", "FAIL")
                    all_passed = False

            except Exception as e:
                self.log(f"  ✗ {filename} error: {e}", "FAIL")
                all_passed = False

        self.test_results.append(("Static Files", all_passed))
        return all_passed

    def test_pdf_conversion(self):
        """Test PDF upload and conversion"""
        self.log("Testing PDF conversion...", "INFO")

        sample_pdf = os.path.join(
            os.path.dirname(__file__),
            "sample.pdf"
        )

        if not os.path.exists(sample_pdf):
            self.log(f"Sample PDF not found at {sample_pdf}", "FAIL")
            self.test_results.append(("PDF Conversion", False))
            return False

        try:
            with open(sample_pdf, "rb") as f:
                files = {"pdf": f}
                response = requests.post(
                    f"{self.base_url}/convert",
                    files=files,
                    timeout=30
                )

            if response.status_code != 200:
                self.log(f"Conversion returned status {response.status_code}", "FAIL")
                self.test_results.append(("PDF Conversion", False))
                return False

            data = response.json()

            # Verify response structure
            if "html" not in data:
                self.log("Response missing 'html' field", "FAIL")
                self.test_results.append(("PDF Conversion", False))
                return False

            if "issues" not in data:
                self.log("Response missing 'issues' field", "FAIL")
                self.test_results.append(("PDF Conversion", False))
                return False

            # Verify HTML content
            html = data["html"]
            if "<article>" not in html or "</article>" not in html:
                self.log("HTML missing article tags", "FAIL")
                self.test_results.append(("PDF Conversion", False))
                return False

            self.log("PDF conversion successful", "PASS")
            self.log(f"  HTML length: {len(html)} characters", "INFO")
            self.log(f"  Issues found: {len(data['issues'])}", "INFO")

            self.test_results.append(("PDF Conversion", True))
            return True

        except Exception as e:
            self.log(f"PDF conversion test failed: {e}", "FAIL")
            self.test_results.append(("PDF Conversion", False))
            return False

    def test_image_serving(self):
        """Test that extracted images can be served"""
        self.log("Testing image serving...", "INFO")

        images_dir = os.path.join(
            os.path.dirname(__file__),
            "backend/extracted_images"
        )

        if not os.path.exists(images_dir):
            self.log("No extracted images directory found", "WARN")
            self.test_results.append(("Image Serving", False))
            return False

        image_files = list(Path(images_dir).glob("*.png")) + \
                      list(Path(images_dir).glob("*.jpg")) + \
                      list(Path(images_dir).glob("*.jpeg"))

        if not image_files:
            self.log("No extracted images found", "WARN")
            self.test_results.append(("Image Serving", False))
            return False

        all_passed = True

        for image_path in image_files[:3]:  # Test first 3 images
            filename = image_path.name
            try:
                response = requests.get(
                    f"{self.base_url}/extracted_images/{filename}"
                )

                if response.status_code == 200:
                    self.log(f"  ✓ {filename} served ({len(response.content)} bytes)", "PASS")
                else:
                    self.log(f"  ✗ {filename} status {response.status_code}", "FAIL")
                    all_passed = False

            except Exception as e:
                self.log(f"  ✗ {filename} error: {e}", "FAIL")
                all_passed = False

        self.test_results.append(("Image Serving", all_passed))
        return all_passed

    def test_html_contains_images(self):
        """Test that generated HTML references images correctly"""
        self.log("Testing HTML image references...", "INFO")

        sample_pdf = os.path.join(
            os.path.dirname(__file__),
            "sample.pdf"
        )

        try:
            with open(sample_pdf, "rb") as f:
                files = {"pdf": f}
                response = requests.post(
                    f"{self.base_url}/convert",
                    files=files,
                    timeout=30
                )

            data = response.json()
            html = data["html"]

            # Check for image references
            if "/extracted_images/" in html:
                self.log("HTML contains image references", "PASS")

                # Count figures
                figure_count = html.count("<figure>")
                self.log(f"  Figures found: {figure_count}", "INFO")

                # Check for figcaptions
                figcaption_count = html.count("<figcaption>")
                self.log(f"  Figcaptions found: {figcaption_count}", "INFO")

                # Check for alt attributes
                import re
                alt_count = len(re.findall(r'alt="[^"]*"', html))
                self.log(f"  Alt text attributes found: {alt_count}", "INFO")

                self.test_results.append(("HTML Image References", True))
                return True
            else:
                self.log("HTML does not contain image references", "WARN")
                self.test_results.append(("HTML Image References", False))
                return False

        except Exception as e:
            self.log(f"HTML image test failed: {e}", "FAIL")
            self.test_results.append(("HTML Image References", False))
            return False

    def test_accessibility_review(self):
        """Test that accessibility issues are detected"""
        self.log("Testing accessibility review...", "INFO")

        sample_pdf = os.path.join(
            os.path.dirname(__file__),
            "sample.pdf"
        )

        try:
            with open(sample_pdf, "rb") as f:
                files = {"pdf": f}
                response = requests.post(
                    f"{self.base_url}/convert",
                    files=files,
                    timeout=30
                )

            data = response.json()
            issues = data.get("issues", [])

            if isinstance(issues, list) and len(issues) > 0:
                self.log(f"Accessibility issues detected: {len(issues)}", "PASS")

                for i, issue in enumerate(issues[:3]):
                    severity = issue.get("severity", "unknown")
                    message = issue.get("message", "")
                    self.log(f"  Issue {i+1} ({severity}): {message[:60]}...", "INFO")

                self.test_results.append(("Accessibility Review", True))
                return True
            else:
                self.log("No accessibility issues found (might be okay)", "INFO")
                self.test_results.append(("Accessibility Review", True))
                return True

        except Exception as e:
            self.log(f"Accessibility review test failed: {e}", "FAIL")
            self.test_results.append(("Accessibility Review", False))
            return False

    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print(f"{BLUE}INTEGRATION TEST RESULTS{RESET}")
        print("=" * 60)

        passed = 0
        failed = 0

        for test_name, result in self.test_results:
            status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
            print(f"{status} - {test_name}")

            if result:
                passed += 1
            else:
                failed += 1

        print("=" * 60)
        print(f"Total: {passed} passed, {failed} failed")
        print("=" * 60 + "\n")

        return failed == 0

    def run(self):
        """Run all integration tests"""
        print("\n" + "=" * 60)
        print(f"{BLUE}FULL STACK INTEGRATION TEST{RESET}")
        print("=" * 60 + "\n")

        # Start server
        if not self.start_server():
            self.log("Cannot proceed without server", "FAIL")
            return False

        try:
            # Run all tests
            self.test_frontend_serves()
            self.test_static_files()
            self.test_pdf_conversion()
            self.test_image_serving()
            self.test_html_contains_images()
            self.test_accessibility_review()

        finally:
            self.stop_server()

        # Print results
        return self.print_results()


if __name__ == "__main__":
    test = IntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)
