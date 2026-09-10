"""
==========================================================
Page Parser
==========================================================

Tugas:
-------
Mengubah input halaman dari user menjadi
struktur data yang dapat diproses service.

Contoh:

Input:
    5

Output:
    [(5, 5)]

------------------------------------------

Input:
    1-5

Output:
    [(1, 5)]

------------------------------------------

Input:
    1-5,8,10-12

Output:
    [
        (1, 5),
        (8, 8),
        (10, 12)
    ]

==========================================================
"""


class PageParser:

    @staticmethod
    def parse_groups(
        text,
        total_pages
    ):
        """
        Parse halaman pilihan.

        Parameters
        ----------
        text : str

            Contoh:
            5
            1-5
            1-5,8,10-12

        total_pages : int

            Total halaman PDF.

        Returns
        -------
        list[tuple]

            Contoh:

            [
                (1,5),
                (8,8),
                (10,12)
            ]

        Raises
        ------
        ValueError
        """

        groups = []

        parts = [
            item.strip()
            for item in text.split(",")
            if item.strip()
        ]

        for part in parts:

            # ======================================
            # Single Page
            # ======================================

            if "-" not in part:

                page = int(part)

                if page < 1:
                    raise ValueError(
                        "Halaman dimulai dari 1."
                    )

                if page > total_pages:
                    raise ValueError(
                        f"Maksimal halaman {total_pages}."
                    )

                groups.append(
                    (page, page)
                )

                continue

            # ======================================
            # Page Range
            # ======================================

            try:

                start_page, end_page = map(
                    int,
                    part.split("-")
                )

            except ValueError:

                raise ValueError(
                    f"Format tidak valid: {part}"
                )

            if start_page > end_page:

                raise ValueError(
                    f"Rentang tidak valid: {part}"
                )

            if start_page < 1:

                raise ValueError(
                    "Halaman dimulai dari 1."
                )

            if end_page > total_pages:

                raise ValueError(
                    f"Maksimal halaman {total_pages}."
                )

            groups.append(
                (
                    start_page,
                    end_page
                )
            )

        return groups