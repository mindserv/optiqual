# fetch_test_classes.py
import subprocess
import re
import os
import requests
import json

OPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DIR = os.path.join(OPT_DIR, "tests")

RUNNER_DIR = os.path.join(OPT_DIR, "common")


def get_test_classes():
    """Get a list of pytest test class names from all test files in a directory."""
    try:
        # Run pytest with --collect-only to list test items in the directory
        result = subprocess.run(
            ["python3", "{}/run_optiqual.py".format(RUNNER_DIR), "optiqual", "--collect-only", "-q"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        # Extract class names using regex (lines starting with '<class>')
        class_pattern = re.compile(r"<Class '(.+?)'>")
        class_names = re.findall(r"<Class\s+(\w+)>", result.stdout)
        return class_names

    except subprocess.CalledProcessError as e:
        print(f"Error collecting tests: {e}")
        print(f"stderr: {e.stderr}")
        return []

def construct_pytest_cli(test_class, prod, station, sn, pn, result_file_name):
    #  python3 run_optiqual.py optiqual
    #  --product-type cpx100g
    #  --qual-station optiqual1
    #  --dut-sn MINDSERV -v -k TestSweeps
    # TODO: I just use default product-type, qual-station and dut-sn. These values has to come
    #  from the GUI/User input
    cmd = ["python3", "{}/run_optiqual.py".format(RUNNER_DIR), "optiqual", "--product-type", prod, "--qual-station", station,
           "--dut-sn", sn, "--dut-pn", pn, "-v", "-k", test_class, "--json-report", "--json-report-file", result_file_name]
    return cmd


if __name__ == "__main__":
    classes = get_test_classes()
    for cls in classes:
        print(cls)
