import json
import re
import xml.etree.ElementTree as ET

"""
Process the result of the CI, and return some meaningful insights
"""

file = "/home/bblommers/Downloads/create_report_ls_1.txt"

file1 = open(file, 'r')
count = 0
suites_by_name = dict()

failed_suites = dict()
failing_suite = False
current_suite_content = ""

successfull_suites = dict()


def clean_xml(input):
    "2021-07-06T23:53:41.1505100Z <testsuite"
    output = re.sub(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+Z ", "", input)
    "[mtt.gotest] 2021/07/06 20:06:28 [INFO] "
    output = re.sub("\[mtt.gotest\] [0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \[INFO\] ", "", output)
    return output


while True:

    # Get next line from file
    line = file1.readline()

    if not line:
        break

    # Line with result
    if "'time':" in line:
        suite = json.loads(line.strip()[line.find("{"):].replace("'", "\""))
        suites_by_name[suite["name"]] = suite
        if suite["tests"] == (suite["passed"] + suite["skipped"]):
            successfull_suites[suite["name"]] = suite

    if "<testsuite name" in line:
        failing_suite = True
        current_suite_content = line.strip()
    if "</testsuite>" in line:
        failing_suite = False
        current_suite_content += line.strip()
        current_suite_content = clean_xml(current_suite_content)
        attributes = ET.fromstring(current_suite_content).attrib
        failed_suites[attributes["name"]] = attributes


sorted_suites_by_time = dict(sorted(suites_by_name.items(), key=lambda item: item[1]["time"]))
failed_suites_by_time = dict(sorted(failed_suites.items(), key=lambda item: item[1]["time"]))

for name, suite in sorted_suites_by_time.items():
    print("{} \t(Time: {}, Results: {}/{})".format(name, suite["time"], suite["passed"], suite["tests"]))
print("===============")
for name, suite in failed_suites_by_time.items():
    print("{} \t(Time: {}, Results: {} failures out of {})".format(name, suite["time"], int(suite["errors"])+int(suite["failures"]), suite["tests"]))
print("===============")
for name, suite in successfull_suites.items():
    print("{} \t(Time: {}, Results: {} failures out of {})".format(name, suite["time"], int(suite["errors"])+int(suite["failures"]), suite["tests"]))


file1.close()
