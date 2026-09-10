"""
========================================================
Mahdi PDF Studio
Tool Information Model
========================================================

Model data untuk satu buah Tool.

Author : Muhammad Hadi Putra
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ToolInfo:
    """
    Menyimpan informasi sebuah Tool.
    """

    id: str

    icon: str

    title: str

    description: str

    page: str

    enabled: bool = True