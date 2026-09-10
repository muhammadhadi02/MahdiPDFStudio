"""
navigation.py
----------------------------------
Mengatur perpindahan halaman (Page Navigation)
Mahdi PDF Studio
"""


class Navigation:

    def __init__(self):
        self.workspace = None

    def set_workspace(self, workspace):
        """
        Menghubungkan Navigation dengan Workspace.
        """
        self.workspace = workspace

    def navigate(self, page_name):
        """
        Berpindah ke halaman tertentu.
        """

        if self.workspace is None:
            return

        self.workspace.show_page(page_name)

        # Update Sidebar Active State

        if hasattr(self, "sidebar"):

            self.sidebar.set_active(
                page_name
            )