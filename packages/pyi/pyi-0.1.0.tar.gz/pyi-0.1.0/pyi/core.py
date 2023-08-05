# python std lib
import json
import re
import sys
from pprint import pprint

# 3rd party imports
import requests


def sort_software_versions(versions=[], reverse=False):
    """
    Custom software sorting function.
    """
    def split_version(version):
        def toint(x):
            try:
                return int(x)
            except:
                return x
        return map(toint, re.sub(r'([a-z])([0-9])', r'\1.\2', re.sub(r'([0-9])([a-z])', r'\1.\2', version.lower().replace('-', '.'))).split('.'))

    def compare_version_list(l1, l2):
        def compare_version(v1, v2):
            if isinstance(v1, int):
                if isinstance(v2, int):
                    return v1 - v2
                else:
                    return 1
            else:
                if isinstance(v2, int):
                    return -1
                else:
                    return cmp(v1, v2)

        ret = 0
        n1 = len(l1)
        n2 = len(l2)
        if n1 < n2:
            l1.extend([0]*(n2 - n1))
        if n2 < n1:
            l2.extend([0]*(n1 - n2))
        n = max(n1, n2)
        i = 0
        while not ret and i < n:
            ret = compare_version(l1[i], l2[i])
            i += 1
        return ret
    return sorted(versions, cmp=compare_version_list, key=split_version)


class Core:
    BASE_PYPI_URL = "https://pypi.python.org/pypi/{0}/json"

    def __init__(self, packages):
        self.packages = packages

    def p(self):
        print("")
        for package in self.packages:
            url = self.BASE_PYPI_URL.format(package)

            raw_data = requests.get(url)
            if raw_data.status_code != 200:
                print("ERROR: Package do not exists on pypi")
                sys.exit(1)
            data = json.loads(raw_data.text)

            yield (data, package)

            print("\n")

    def basic(self):
        for data, package in self.p():
            print("Package: {0}".format(package))
            print("Latest version: {0}".format(data["info"]["version"]))
            print("Author: {0}".format(data["info"]["author"]))
            print("Author email: {0}".format(data["info"]["author_email"]))
            print("Maintainer: {0}".format(data["info"]["maintainer"]))
            print("Maintainer email: {0}".format(data["info"]["maintainer_email"]))
            print("Download url: {0}".format(data["info"]["download_url"]))
            print("Release url: {0}".format(data["info"]["release_url"]))
            print("Package url: {0}".format(data["info"]["package_url"]))
            print("Classifiers: {0}".format(data["info"]["classifiers"]))
            print("License: {0}".format(data["info"]["license"]))
            print("Summary: {0}".format(data["info"]["summary"]))
            print("Homepage: {0}".format(data["info"]["home_page"]))
            print("Downloads:")
            print(" - Last day: {0}".format(data["info"]["downloads"]["last_day"]))
            print(" - Last week: {0}".format(data["info"]["downloads"]["last_week"]))
            print(" - Last month: {0}".format(data["info"]["downloads"]["last_month"]))

    def description(self):
        for data, package in self.p():
            print("Package: {0}".format(package))
            print("{0}".format(data["info"]["description"]))

    def downloads(self):
        for data, package in self.p():
            print("Package: {0}".format(package))
            print("Downloads")
            print(" - Last day: {0}".format(data["info"]["downloads"]["last_day"]))
            print(" - Last week: {0}".format(data["info"]["downloads"]["last_week"]))
            print(" - Last month: {0}".format(data["info"]["downloads"]["last_month"]))
            print("")

            total_downloads = 0

            releases = sort_software_versions([r for r, d in data["releases"].items()])

            for release in releases:
                for release_data in data["releases"][release]:
                    downloads = release_data["downloads"]
                    print(" Release: {0} ({1}) -- {2}".format(
                        release,
                        release_data["url"].split("/")[-1],
                        downloads,
                    ))
                    total_downloads += downloads
            print("\nTotal downloads: {0}".format(total_downloads))

    def releases(self):
        for data, package in self.p():
            print("Package: {0}".format(package))
            print("Releases:")
            releases = sort_software_versions([r for r, d in data["releases"].items()])
            for release in releases:
                print(" - {0}".format(release))
                for release_data in data["releases"][release]:
                    print("  - {0}".format(release_data["url"].split("/")[-1]))

    def release(self, version):
        for data, package in self.p():
            if version not in data["releases"]:
                print("ERROR: release not found")
                return
            else:
                for release_data in data["releases"][version]:
                    print("Release: {0}".format(version))
                    print(" Has sig: {0}".format(release_data["has_sig"]))
                    print(" Upload time: {0}".format(release_data["upload_time"]))
                    print(" Comment text: {0}".format(release_data["comment_text"]))
                    print(" Python version: {0}".format(release_data["python_version"]))
                    print(" Url: {0}".format(release_data["url"]))
                    print(" md5 digest: {0}".format(release_data["md5_digest"]))
                    print(" downloads: {0}".format(release_data["downloads"]))
                    print(" filename: {0}".format(release_data["filename"]))
                    print(" packagetype: {0}".format(release_data["packagetype"]))
                    print(" Size: {0}".format(release_data["size"]))

    def raw(self):
        for data, package in self.p():
            pprint(data)
