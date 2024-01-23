#!/usr/bin/env python3
from pathlib import Path
from typing import List

import setuptools
from setuptools import setup

this_dir = Path(__file__).parent
module_dir = this_dir / "wyoming_satellite_led_event"
version_path = module_dir / "VERSION"
version = version_path.read_text(encoding="utf-8").strip()


def get_requirements(req_path: Path) -> List[str]:
    if not req_path.is_file():
        return []

    requirements: List[str] = []
    with open(req_path, "r", encoding="utf-8") as req_file:
        for line in req_file:
            line = line.strip()
            if not line:
                continue

            requirements.append(line)

    return requirements


install_requires = get_requirements(this_dir / "requirements.txt")

# -----------------------------------------------------------------------------

setup(
    name="wyoming_satellite_led_event",
    version="0.1.0",
    description="Wyoming server for remote voice satellite led events (led pattern)",
    url="http://github.com/rhasspy/wyoming-satellite-led-event",
    author="???",
    author_email="???",
    packages=setuptools.find_packages(),
    package_data={
        "wyoming_satellite_led_event": [str(p.relative_to(module_dir)) for p in (version_path,)]
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL-3.0 License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="rhasspy wyoming satellite led control",
        entry_points={
        "console_scripts": ["wyoming-satellite-led-control = wyoming_satellite_led_control:__main__.run"]
    },
)
