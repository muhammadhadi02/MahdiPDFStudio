"""
==========================================================
Mahdi PDF Studio
Base Plugin
==========================================================

Seluruh Plugin harus mewarisi class ini.

Author : Muhammad Hadi Putra
"""

from abc import ABC, abstractmethod

from data.models.tool_info import ToolInfo


class BasePlugin(ABC):
    """
    Abstract Base Class untuk seluruh Plugin.
    """

    @property
    @abstractmethod
    def info(self) -> ToolInfo:
        """
        Metadata Plugin.
        """
        pass

    @abstractmethod
    def create_page(self, master):
        """
        Membuat halaman plugin.

        Return
        ------
        CTkFrame
        """
        pass

    @abstractmethod
    def execute(self):
        """
        Menjalankan proses utama plugin.
        """
        pass