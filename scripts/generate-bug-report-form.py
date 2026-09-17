from functools import cmp_to_key
from pathlib import Path
import json
import re
import subprocess

POOL = Path("pool/main")
OUTPUT_DIR = Path(".github/ISSUE_TEMPLATE")
GENERATED_PREFIX = "bug-package-"
LEGACY_OUTPUT = OUTPUT_DIR / "bug-report.yml"


def field(package: Path, name: str) -> str:
    result = subprocess.run(
        ["dpkg-deb", "-f", str(package), name],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def version_compare(left: str, right: str) -> int:
    if subprocess.run(["dpkg", "--compare-versions", left, "gt", right]).returncode == 0:
        return -1
    if subprocess.run(["dpkg", "--compare-versions", left, "lt", right]).returncode == 0:
        return 1
    return 0


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def yaml_options(values: list[str]) -> str:
    return "\n".join(f"          - {json.dumps(value)}" for value in values)


def build_form(package: str, versions: list[str], architectures: list[str]) -> str:
    return (
        f"name: {json.dumps(f'Bug report — {package}')}\n"
        f"description: {json.dumps(f'Report a bug affecting {package}.')}\n"
        f"title: {json.dumps(f'[Bug][{package}] ')}\n"
        "body:\n"
        "  - type: markdown\n"
        "    attributes:\n"
        "      value: |\n"
        f"        Report a problem affecting `{package}`. Select the installed version and architecture, then describe what happened.\n"
        "\n"
        "  - type: dropdown\n"
        "    id: version\n"
        "    attributes:\n"
        "      label: Version\n"
        "      description: Select the installed package version. This list is generated automatically from the BezotCorp APT repository.\n"
        "      options:\n"
        f"{yaml_options(versions)}\n"
        "    validations:\n"
        "      required: true\n"
        "\n"
        "  - type: dropdown\n"
        "    id: architecture\n"
        "    attributes:\n"
        "      label: Architecture\n"
        "      description: Select the architecture of the installed package.\n"
        "      options:\n"
        f"{yaml_options(architectures)}\n"
        "    validations:\n"
        "      required: true\n"
        "\n"
        "  - type: input\n"
        "    id: distribution\n"
        "    attributes:\n"
        "      label: Linux distribution\n"
        "      description: Distribution and version where the problem occurs.\n"
        "      placeholder: \"Example: Kubuntu 26.04\"\n"
        "    validations:\n"
        "      required: true\n"
        "\n"
        "  - type: textarea\n"
        "    id: behavior\n"
        "    attributes:\n"
        "      label: What happened?\n"
        "      description: Describe the observed behavior and the problem.\n"
        "    validations:\n"
        "      required: true\n"
        "\n"
        "  - type: textarea\n"
        "    id: reproduction\n"
        "    attributes:\n"
        "      label: Steps to reproduce\n"
        "      description: Describe the steps that reliably reproduce the problem.\n"
        "      placeholder: |\n"
        "        1. ...\n"
        "        2. ...\n"
        "        3. ...\n"
        "    validations:\n"
        "      required: true\n"
        "\n"
        "  - type: textarea\n"
        "    id: expected\n"
        "    attributes:\n"
        "      label: Expected behavior\n"
        "      description: Describe what you expected to happen instead.\n"
        "    validations:\n"
        "      required: true\n"
        "\n"
        "  - type: textarea\n"
        "    id: logs\n"
        "    attributes:\n"
        "      label: Relevant logs\n"
        "      description: Add relevant logs if available. Remove secrets or personal information before submitting.\n"
        "      render: shell\n"
        "\n"
        "  - type: textarea\n"
        "    id: additional-context\n"
        "    attributes:\n"
        "      label: Additional context\n"
        "      description: Add any other information that may help reproduce or diagnose the problem.\n"
    )


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for generated_form in OUTPUT_DIR.glob(f"{GENERATED_PREFIX}*.yml"):
    generated_form.unlink()

if LEGACY_OUTPUT.exists():
    LEGACY_OUTPUT.unlink()

products: dict[str, dict[str, set[str]]] = {}

for package_path in sorted(POOL.rglob("*.deb")):
    package = field(package_path, "Package")
    version = field(package_path, "Version")
    architecture = field(package_path, "Architecture")

    product = products.setdefault(package, {"versions": set(), "architectures": set()})
    product["versions"].add(version)
    product["architectures"].add(architecture)

if not products:
    print("No Debian packages found; generated bug report forms were removed.")
else:
    for package, product in sorted(products.items()):
        versions = sorted(product["versions"], key=cmp_to_key(version_compare))
        architectures = sorted(product["architectures"])
        output = OUTPUT_DIR / f"{GENERATED_PREFIX}{slug(package)}.yml"
        output.write_text(
            build_form(package, versions, architectures),
            encoding="utf-8",
        )
        print(
            f"Generated {output} with {len(versions)} version(s) "
            f"and {len(architectures)} architecture(s)."
        )
