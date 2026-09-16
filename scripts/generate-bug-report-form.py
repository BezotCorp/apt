from pathlib import Path
import json
import subprocess

POOL = Path("pool/main")
OUTPUT = Path(".github/ISSUE_TEMPLATE/bug-report.yml")


def field(package: Path, name: str) -> str:
    result = subprocess.run(
        ["dpkg-deb", "-f", str(package), name],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


packages = sorted(POOL.rglob("*.deb"))

if not packages:
    print("No Debian packages found; bug report form was not generated.")
else:
    entries = {
        (
            field(package, "Package"),
            field(package, "Version"),
            field(package, "Architecture"),
        )
        for package in packages
    }

    options = "\n".join(
        f"          - {json.dumps(f'{package} — {version} ({architecture})')}"
        for package, version, architecture in sorted(entries)
    )

    form = (
        "name: Bug report\n"
        "description: Report a bug affecting a BezotCorp package distributed through the APT repository.\n"
        "title: \"[Bug] \"\n"
        "body:\n"
        "  - type: markdown\n"
        "    attributes:\n"
        "      value: |\n"
        "        Select the exact package build you are using, then describe the problem.\n"
        "\n"
        "  - type: dropdown\n"
        "    id: package-build\n"
        "    attributes:\n"
        "      label: Package / version / architecture\n"
        "      description: This list is generated automatically from packages published in the BezotCorp APT repository.\n"
        "      options:\n"
        f"{options}\n"
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

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(form, encoding="utf-8")
    print(f"Generated {OUTPUT} with {len(entries)} package build option(s).")
