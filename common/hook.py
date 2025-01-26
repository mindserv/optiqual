import pytest
import json


custom_test_data = {}
def pytest_addoption(parser):
    group = parser.getgroup("Arguments to initialize instruments and devices")
    group.addoption("--product-type", help="Device type to calibrate and validate")
    group.addoption("--qual-station", help="Device type to calibrate and validate")
    group.addoption("--dut-sn", help="SN of Device under test")
    group.addoption("--dut-pn", help="PN of Device under test")

@pytest.hookimpl
def pytest_configure(config):
    # Programmatically configure the json-report plugin
    config.option.json_report = True  # Enable the json-report plugin
    config.option.json_report_additional_keys = ["user_properties"]  # Add the custom keys

# Add custom data to each test result
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # Collect custom data from the test class (request.cls)
        if hasattr(item.cls, "custom_data"):
            # Add data to the global dictionary
            if item.nodeid not in custom_test_data:
                custom_test_data[item.nodeid] = {}
            custom_test_data[item.nodeid].update(item.cls.custom_data)

            # Add custom data to the report.user_properties for JSON output
            if not hasattr(report, "user_properties"):
                report.user_properties = []
            report.user_properties.extend(item.cls.custom_data.items())
            print(f"User properties for {item.nodeid}: {report.user_properties}")
@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    # Print the custom data for debugging
    print("Custom Test Data:", custom_test_data)

    # Read the existing JSON report
    json_report_path = session.config.option.json_report_file or "report.json"
    with open(json_report_path, "r") as f:
        report_data = json.load(f)

    # Add custom test data to each test result
    for test_result in report_data.get("tests", []):
        nodeid = test_result.get("nodeid")
        if nodeid in custom_test_data:
            test_result["custom_data"] = custom_test_data[nodeid]

    # Write the modified report back
    with open(json_report_path, "w") as f:
        json.dump(report_data, f, indent=4)