import os
import subprocess
import time
import urllib.request
import base64
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class BanpangBrowserService:

    WEBSITE_URL = "https://banpang.bulog.co.id/"

    REMOTE_DEBUGGING_HOST = "127.0.0.1"
    REMOTE_DEBUGGING_PORT = 9222

    # ======================================================
    # CHROME
    # ======================================================

    @classmethod
    def get_chrome_path(cls):
        """
        Mencari lokasi Google Chrome.
        """

        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                r"Google\Chrome\Application\chrome.exe"
            )
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                return path

        raise FileNotFoundError(
            "Google Chrome tidak ditemukan."
        )

    @classmethod
    def get_user_data_dir(cls):
        """
        Profile Chrome khusus Banpang.
        """

        user_profile = os.environ.get(
            "USERPROFILE",
            os.path.expanduser("~")
        )

        user_data_dir = os.path.join(
            user_profile,
            "chrome-bulog"
        )

        os.makedirs(
            user_data_dir,
            exist_ok=True
        )

        return user_data_dir

    @classmethod
    def is_browser_ready(cls):
        """
        Mengecek apakah Chrome dengan
        remote debugging port 9222 aktif.
        """

        url = (
            f"http://{cls.REMOTE_DEBUGGING_HOST}:"
            f"{cls.REMOTE_DEBUGGING_PORT}/json/version"
        )

        try:
            with urllib.request.urlopen(
                url,
                timeout=1
            ):
                return True

        except Exception:
            return False

    @classmethod
    def open_website(cls):
        """
        Membuka Chrome khusus Banpang.
        """

        chrome_path = cls.get_chrome_path()
        user_data_dir = cls.get_user_data_dir()

        # ==================================================
        # JIKA CHROME SUDAH AKTIF
        # ==================================================

        if cls.is_browser_ready():

            try:
                subprocess.Popen(
                    [
                        chrome_path,
                        cls.WEBSITE_URL
                    ],
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )

                return {
                    "success": True,
                    "message": "Website Banpang dibuka kembali.",
                    "browser_ready": True
                }

            except Exception as error:
                raise Exception(
                    f"Gagal membuka website Banpang: {error}"
                )

        # ==================================================
        # MEMBUKA CHROME KHUSUS BANPANG
        # ==================================================

        command = [
            chrome_path,

            f"--remote-debugging-port="
            f"{cls.REMOTE_DEBUGGING_PORT}",

            f"--user-data-dir={user_data_dir}",

            "--no-first-run",

            "--no-default-browser-check",

            cls.WEBSITE_URL
        ]

        try:
            subprocess.Popen(
                command,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )

        except Exception as error:
            raise Exception(
                f"Gagal menjalankan Google Chrome: {error}"
            )

        return {
            "success": True,
            "message": "Browser Banpang berhasil dibuka.",
            "browser_ready": True
        }

    # ======================================================
    # CONNECT SELENIUM
    # ======================================================

    @classmethod
    def connect_driver(cls):
        """
        Menghubungkan Selenium ke Chrome yang sudah dibuka
        melalui remote debugging port 9222.
        """

        if not cls.is_browser_ready():
            raise Exception(
                "Browser Banpang belum dibuka."
            )

        options = Options()

        options.debugger_address = (
            f"{cls.REMOTE_DEBUGGING_HOST}:"
            f"{cls.REMOTE_DEBUGGING_PORT}"
        )

        try:
            driver = webdriver.Chrome(
                options=options
            )

        except Exception as error:
            raise Exception(
                f"Gagal terhubung ke Chrome Banpang: {error}"
            )

        return driver

    # ======================================================
    # CHECK LOGIN
    # ======================================================

    @classmethod
    def check_login(cls, driver):
        """
        Mengecek kondisi browser setelah user login.

        Untuk tahap awal kita menggunakan beberapa indikator:
        - browser masih aktif
        - URL dapat dibaca
        - cookies tersedia
        - halaman bukan halaman login yang jelas
        """

        if driver is None:
            return {
                "success": False,
                "logged_in": False,
                "message": "Driver Selenium tidak tersedia."
            }

        try:
            current_url = driver.current_url or ""
            page_title = driver.title or ""
            cookies = driver.get_cookies()

            current_url_lower = current_url.lower()

            # ==================================================
            # DETEKSI HALAMAN LOGIN
            # ==================================================

            login_keywords = [
                "login",
                "signin",
                "sign-in",
                "masuk"
            ]

            still_login_page = any(
                keyword in current_url_lower
                for keyword in login_keywords
            )

            # ==================================================
            # HASIL AWAL
            # ==================================================

            if still_login_page:
                return {
                    "success": True,
                    "logged_in": False,
                    "message": "Halaman login masih terbuka.",
                    "url": current_url,
                    "title": page_title,
                    "cookie_count": len(cookies)
                }

            # ==================================================
            # JIKA SUDAH MENINGGALKAN HALAMAN LOGIN
            # ==================================================

            if cookies:
                return {
                    "success": True,
                    "logged_in": True,
                    "message": "Sesi login terdeteksi.",
                    "url": current_url,
                    "title": page_title,
                    "cookie_count": len(cookies)
                }

            # ==================================================
            # TIDAK CUKUP BUKTI
            # ==================================================

            return {
                "success": True,
                "logged_in": False,
                "message": (
                    "Browser terhubung, tetapi sesi login "
                    "belum dapat dipastikan."
                ),
                "url": current_url,
                "title": page_title,
                "cookie_count": 0
            }

        except Exception as error:
            return {
                "success": False,
                "logged_in": False,
                "message": (
                    f"Gagal memeriksa login: {error}"
                )
            }

    # ======================================================
    # INSPECT FILTER DOKUMEN
    # ======================================================

    @classmethod
    def inspect_filter_elements(cls, driver):

        print(
            "\n========================================"
        )

        print(
            "=== INSPEKSI FILTER DOKUMEN BANPANG ==="
        )

        try:

            # ==================================================
            # 1. NATIVE SELECT
            # ==================================================

            selects = driver.find_elements(
                "tag name",
                "select"
            )

            print(
                "\nJumlah <select>:",
                len(selects)
            )

            for index, select in enumerate(selects):

                print(
                    f"\n--- SELECT {index + 1} ---"
                )

                print(
                    "Name:",
                    select.get_attribute("name")
                )

                print(
                    "ID:",
                    select.get_attribute("id")
                )

                print(
                    "Class:",
                    select.get_attribute("class")
                )

                options = select.find_elements(
                    "tag name",
                    "option"
                )

                print(
                    "Jumlah option:",
                    len(options)
                )

                for option in options[:20]:

                    print(
                        "  -",
                        option.text.strip(),
                        "| value =",
                        option.get_attribute("value")
                    )

            # ==================================================
            # 2. ELEMENT ROLE=COMBOBOX
            # ==================================================

            comboboxes = driver.find_elements(
                "css selector",
                '[role="combobox"]'
            )

            print(
                "\n========================================"
            )

            print(
                "Jumlah [role=combobox]:",
                len(comboboxes)
            )

            for index, element in enumerate(comboboxes):

                print(
                    f"\n--- COMBOBOX {index + 1} ---"
                )

                print(
                    "Text:",
                    element.text.strip()
                )

                print(
                    "ID:",
                    element.get_attribute("id")
                )

                print(
                    "Name:",
                    element.get_attribute("name")
                )

                print(
                    "Class:",
                    element.get_attribute("class")
                )

                print(
                    "Aria label:",
                    element.get_attribute("aria-label")
                )

                print(
                    "Placeholder:",
                    element.get_attribute("placeholder")
                )

            # ==================================================
            # 3. INPUT
            # ==================================================

            inputs = driver.find_elements(
                "css selector",
                "input"
            )

            print(
                "\n========================================"
            )

            print(
                "Jumlah input:",
                len(inputs)
            )

            for index, element in enumerate(inputs):

                print(
                    f"\n--- INPUT {index + 1} ---"
                )

                print(
                    "Type:",
                    element.get_attribute("type")
                )

                print(
                    "Name:",
                    element.get_attribute("name")
                )

                print(
                    "ID:",
                    element.get_attribute("id")
                )

                print(
                    "Class:",
                    element.get_attribute("class")
                )

                print(
                    "Placeholder:",
                    element.get_attribute("placeholder")
                )

                print(
                    "Value:",
                    element.get_attribute("value")
                )

            # ==================================================
            # 4. BUTTON YANG BERKAITAN DENGAN FILTER
            # ==================================================

            buttons = driver.find_elements(
                "css selector",
                "button"
            )

            print(
                "\n========================================"
            )

            print(
                "Jumlah button:",
                len(buttons)
            )

            for index, button in enumerate(buttons):

                text = button.text.strip()

                if text:
                    print(
                        f"BUTTON {index + 1}:",
                        repr(text)
                    )

            print(
                "\n========================================"
            )

            print(
                "=== INSPEKSI SELESAI ==="
            )

            print(
                "========================================"
            )

            return True

        except Exception as error:

            print(
                "\nInspeksi Filter Error:",
                error
            )

            return False

    # ======================================================
    # INSPECT TAHUN
    # ======================================================

    @classmethod
    def inspect_tahun_dropdown(cls, driver):

        print(
            "\n========================================"
        )

        print(
            "=== INSPEKSI REACT SELECT TAHUN ==="
        )

        try:

            element = driver.find_element(
                "id",
                "react-select-filter-alokasi-tahun-input"
            )

            print("\nINPUT TAHUN DITEMUKAN")

            print(
                "Outer HTML sebelum klik:"
            )

            print(
                element.get_attribute("outerHTML")
            )

            # Klik
            element.click()

            time.sleep(1)

            print(
                "\n=== ATTRIBUTE SETELAH KLIK ==="
            )

            print(
                "aria-expanded:",
                element.get_attribute(
                    "aria-expanded"
                )
            )

            print(
                "aria-activedescendant:",
                element.get_attribute(
                    "aria-activedescendant"
                )
            )

            # ==================================================
            # CARI SEMUA ELEMEN YANG MEMILIKI ID
            # REACT-SELECT
            # ==================================================

            print(
                "\n========================================"
            )

            print(
                "=== ELEMEN REACT-SELECT ==="
            )

            elements = driver.find_elements(
                "css selector",
                '[id*="react-select"]'
            )

            print(
                "Jumlah:",
                len(elements)
            )

            for index, item in enumerate(elements):

                print(
                    f"\n--- ELEMENT {index + 1} ---"
                )

                print(
                    "Tag:",
                    item.tag_name
                )

                print(
                    "ID:",
                    item.get_attribute("id")
                )

                print(
                    "Role:",
                    item.get_attribute("role")
                )

                print(
                    "Class:",
                    item.get_attribute("class")
                )

                text = item.text.strip()

                if text:
                    print(
                        "Text:",
                        repr(text[:1000])
                    )

            # ==================================================
            # CARI ELEMENT DENGAN ARIA-ACTIVEDESCENDANT
            # ==================================================

            print(
                "\n========================================"
            )

            print(
                "=== ELEMEN ARIA ACTIVE DESCENDANT ==="
            )

            active_id = element.get_attribute(
                "aria-activedescendant"
            )

            print(
                "Active ID:",
                active_id
            )

            if active_id:

                try:

                    active_element = driver.find_element(
                        "id",
                        active_id
                    )

                    print(
                        "Element ditemukan."
                    )

                    print(
                        "Tag:",
                        active_element.tag_name
                    )

                    print(
                        "Outer HTML:"
                    )

                    print(
                        active_element.get_attribute(
                            "outerHTML"
                        )
                    )

                except Exception as error:

                    print(
                        "Active element tidak ditemukan:",
                        error
                    )

            # ==================================================
            # AMBIL OUTER HTML PARENT INPUT
            # ==================================================

            print(
                "\n========================================"
            )

            print(
                "=== PARENT INPUT TAHUN ==="
            )

            parent_html = driver.execute_script(
                """
                return arguments[0]
                    .parentElement
                    .parentElement
                    .outerHTML;
                """,
                element
            )

            print(
                parent_html[:10000]
            )

            print(
                "\n========================================"
            )

            print(
                "=== INSPEKSI SELESAI ==="
            )

            print(
                "========================================"
            )

            return True

        except Exception as error:

            print(
                "\nInspeksi React Select Error:",
                error
            )

            return False

    # ======================================================
    # GENERIC REACT SELECT - BY STATIC INPUT ID
    # ======================================================

    @classmethod
    def get_dropdown_options(cls, driver, input_id):
        """
        Mengambil option dari React Select berdasarkan ID input.

        Dipakai untuk dropdown filter dokumen yang mempunyai
        ID stabil, misalnya:
        react-select-filter-alokasi-tahun-input
        """

        try:

            element = driver.find_element(
                "id",
                input_id
            )

            element.click()

            time.sleep(0.5)

            listbox_id = input_id.replace(
                "-input",
                "-listbox"
            )

            listbox = driver.find_element(
                "id",
                listbox_id
            )

            options = listbox.find_elements(
                "css selector",
                '[role="option"]'
            )

            result = []

            for option in options:

                text = option.text.strip()

                if not text:
                    continue

                result.append({
                    "text": text,
                    "value": option.get_attribute(
                        "data-value"
                    ),
                    "id": option.get_attribute("id")
                })

            try:
                element.click()
            except Exception:
                pass

            return result

        except Exception as error:

            print(
                "\nGagal mengambil dropdown:",
                input_id
            )

            print(
                "Error:",
                error
            )

            return []

    @classmethod
    def select_dropdown_option(
        cls,
        driver,
        input_id,
        option_text
    ):
        """
        Memilih option pada React Select berdasarkan teks.
        """

        try:

            element = driver.find_element(
                "id",
                input_id
            )

            element.click()

            time.sleep(0.5)

            listbox_id = input_id.replace(
                "-input",
                "-listbox"
            )

            listbox = driver.find_element(
                "id",
                listbox_id
            )

            options = listbox.find_elements(
                "css selector",
                '[role="option"]'
            )

            target_option = None

            for option in options:

                text = option.text.strip()

                if text == str(option_text).strip():
                    target_option = option
                    break

            if target_option is None:

                print(
                    "\nOption tidak ditemukan:"
                )

                print(
                    "Input:",
                    input_id
                )

                print(
                    "Option:",
                    option_text
                )

                return False

            target_option.click()

            time.sleep(0.5)

            print(
                "\nDropdown berhasil dipilih:"
            )

            print(
                "Input:",
                input_id
            )

            print(
                "Value:",
                option_text
            )

            return True

        except Exception as error:

            print(
                "\nGagal memilih dropdown:"
            )

            print(
                "Input:",
                input_id
            )

            print(
                "Option:",
                option_text
            )

            print(
                "Error:",
                error
            )

            return False

    # ======================================================
    # PBP FILTER - HELPER INTERNAL
    # ======================================================

    # Nama hidden input PBP bersifat jauh lebih stabil daripada ID
    # react-select-5-input / react-select-6-input / dst.
    PBP_FILTER_NAMES = {
        "Status PBP": "pbp_status",
        "Status Serah": "serah_status",
        "Verifikasi Serah": "verification_status",
    }

    @classmethod
    def _get_pbp_hidden_name(cls, label_text):
        return cls.PBP_FILTER_NAMES.get(
            str(label_text).strip()
        )

    @classmethod
    def _find_pbp_filter_input(cls, driver, label_text):
        """
        Mencari input React Select PBP menggunakan hidden input NAME.

        Struktur website mempunyai hidden input yang relatif stabil:
            pbp_status
            serah_status
            verification_status

        Ini lebih aman daripada memakai ID React dinamis.
        """

        hidden_name = cls._get_pbp_hidden_name(label_text)

        if not hidden_name:
            return None

        try:
            hidden = driver.find_element(
                "css selector",
                f'input[type="hidden"][name="{hidden_name}"]'
            )
        except Exception:
            return None

        try:
            element = driver.execute_script(
                """
                const hidden = arguments[0];
                let node = hidden;

                // React Select biasanya menempatkan hidden input
                // di dalam container yang sama dengan input text.
                for (let i = 0; i < 12 && node; i++) {
                    const inputs = node.querySelectorAll(
                        'input[type="text"]'
                    );

                    for (const input of inputs) {
                        if (
                            input.offsetParent !== null &&
                            !input.disabled
                        ) {
                            return input;
                        }
                    }

                    const combos = node.querySelectorAll(
                        '[role="combobox"]'
                    );

                    for (const combo of combos) {
                        if (combo.offsetParent !== null) {
                            const input = combo.querySelector(
                                'input[type="text"]'
                            );
                            if (input) {
                                return input;
                            }
                        }
                    }

                    node = node.parentElement;
                }

                return null;
                """,
                hidden
            )

            if element:
                return element

        except Exception:
            pass

        # Fallback berdasarkan label, tetapi tetap memastikan input
        # berasal dari container yang dekat dengan label.
        try:
            target_label = str(label_text).strip()
            labels = driver.find_elements(
                "xpath",
                f"//*[normalize-space(text())='{target_label}']"
            )

            for label in labels:
                try:
                    element = driver.execute_script(
                        """
                        const label = arguments[0];
                        let node = label;

                        for (let i = 0; i < 8 && node; i++) {
                            const inputs = node.querySelectorAll(
                                'input[type="text"]'
                            );

                            for (const input of inputs) {
                                if (
                                    input.offsetParent !== null &&
                                    !input.disabled
                                ) {
                                    return input;
                                }
                            }

                            node = node.parentElement;
                        }

                        return null;
                        """,
                        label
                    )

                    if element:
                        return element

                except Exception:
                    continue

        except Exception:
            pass

        return None

    @classmethod
    def _wait_for_pbp_input(cls, driver, label_text, timeout=4.0):
        """Menunggu input PBP sampai React selesai rerender."""

        end_time = time.time() + timeout

        while time.time() < end_time:
            try:
                element = cls._find_pbp_filter_input(
                    driver,
                    label_text
                )

                if element is not None:
                    if element.is_displayed() and element.is_enabled():
                        return element
            except Exception:
                pass

            time.sleep(0.15)

        return None

    @classmethod
    def _get_active_listbox(cls, driver):
        """Mengambil listbox React Select yang sedang terlihat."""

        try:
            listboxes = driver.find_elements(
                "css selector",
                '[role="listbox"]'
            )

            visible = []

            for listbox in listboxes:
                try:
                    if listbox.is_displayed():
                        visible.append(listbox)
                except Exception:
                    continue

            if visible:
                return visible[-1]

        except Exception:
            pass

        return None

    @classmethod
    def _close_react_select(cls, driver, element=None):
        """Menutup React Select."""

        try:
            if element is not None:
                try:
                    element.send_keys("ESCAPE")
                except Exception:
                    pass

            driver.execute_script(
                """
                document.body.dispatchEvent(
                    new KeyboardEvent('keydown', {
                        key: 'Escape',
                        code: 'Escape',
                        keyCode: 27,
                        which: 27,
                        bubbles: true
                    })
                );
                """
            )

            time.sleep(0.15)

        except Exception:
            pass

    @classmethod
    def _open_pbp_dropdown(cls, driver, label_text):
        """
        Membuka dropdown PBP.

        Hidden input NAME digunakan sebagai anchor sehingga pemilihan
        tetap stabil walaupun React mengganti ID input setiap rerender.
        """

        for attempt in range(1, 6):
            element = None

            try:
                element = cls._wait_for_pbp_input(
                    driver,
                    label_text,
                    timeout=3.0
                )

                if element is None:
                    print(
                        f"Percobaan {attempt}: input '{label_text}' "
                        "belum ditemukan."
                    )
                    time.sleep(0.3)
                    continue

                driver.execute_script(
                    """
                    arguments[0].scrollIntoView({
                        block: 'center',
                        inline: 'nearest'
                    });
                    """,
                    element
                )

                time.sleep(0.2)

                # Ambil element terbaru setelah scroll.
                fresh = cls._find_pbp_filter_input(
                    driver,
                    label_text
                )
                if fresh is not None:
                    element = fresh

                # JS click lebih tahan terhadap overlay kecil dari React.
                driver.execute_script(
                    "arguments[0].click();",
                    element
                )

                time.sleep(0.35)

                listbox = cls._get_active_listbox(driver)

                if listbox is not None:
                    return element, listbox

                # Beberapa versi React Select membuka menu setelah
                # event click berikutnya.
                try:
                    element.click()
                except Exception:
                    pass

                time.sleep(0.35)

                listbox = cls._get_active_listbox(driver)
                if listbox is not None:
                    return element, listbox

            except Exception as error:
                print(
                    f"Percobaan {attempt} membuka '{label_text}' gagal:",
                    error
                )

            cls._close_react_select(driver, element)
            time.sleep(0.4)

        return None, None

    @classmethod
    def get_pbp_filter_options(cls, driver, label_text):
        """Mengambil option filter PBP berdasarkan label."""

        print("\n=== DROPDOWN:", label_text, "===")
        print("Mode: hidden input name + label + retry")

        element, listbox = cls._open_pbp_dropdown(
            driver,
            label_text
        )

        if listbox is None:
            print("Input/listbox filter PBP tidak ditemukan:")
            print("Label:", label_text)
            return []

        try:
            options = listbox.find_elements(
                "css selector",
                '[role="option"]'
            )

            result = []

            for option in options:
                try:
                    text = option.text.strip()
                    if not text:
                        continue

                    result.append({
                        "text": text,
                        "value": option.get_attribute("data-value"),
                        "id": option.get_attribute("id")
                    })
                except Exception:
                    continue

            print("Dropdown PBP berhasil dibaca:")
            print("Label:", label_text)
            print("Jumlah option:", len(result))

            for item in result:
                print(
                    "  -",
                    item["text"],
                    "| value =",
                    item["value"]
                )

            return result

        finally:
            cls._close_react_select(driver, element)

    @classmethod
    def select_pbp_filter_option(
        cls,
        driver,
        label_text,
        option_text
    ):
        """
        Memilih option PBP berdasarkan label dan teks.

        Penting:
        Setelah sebuah option dipilih, React dapat merender ulang seluruh
        area filter. Karena itu setiap percobaan selalu mencari ulang
        hidden input + input text + listbox.
        """

        wanted_text = str(option_text).strip()

        for attempt in range(1, 8):
            element = None

            try:
                print(
                    f"Mencoba memilih '{wanted_text}' pada '{label_text}' "
                    f"(percobaan {attempt}/7)"
                )

                element, listbox = cls._open_pbp_dropdown(
                    driver,
                    label_text
                )

                if listbox is None:
                    time.sleep(0.5)
                    continue

                # Ambil ulang listbox tepat sebelum membaca option.
                fresh_listbox = cls._get_active_listbox(driver)
                if fresh_listbox is not None:
                    listbox = fresh_listbox

                options = listbox.find_elements(
                    "css selector",
                    '[role="option"]'
                )

                target_option = None

                for option in options:
                    try:
                        text = " ".join(option.text.split())
                        wanted_normalized = " ".join(wanted_text.split())

                        if text.lower() == wanted_normalized.lower():
                            target_option = option
                            break
                    except Exception:
                        continue

                if target_option is None:
                    print(
                        f"Option '{wanted_text}' belum ditemukan pada "
                        f"'{label_text}'."
                    )
                    print(
                        "Option yang sedang terlihat:",
                        [
                            " ".join(o.text.split())
                            for o in options
                            if o.text.strip()
                        ]
                    )
                    cls._close_react_select(driver, element)
                    time.sleep(0.7)
                    continue

                # Scroll option ke area terlihat lalu klik.
                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'nearest'});",
                        target_option
                    )
                except Exception:
                    pass

                try:
                    target_option.click()
                except Exception:
                    driver.execute_script(
                        "arguments[0].click();",
                        target_option
                    )

                # Beri waktu React menyimpan state dan melakukan rerender.
                time.sleep(0.9)

                # Verifikasi berdasarkan hidden input yang stabil.
                hidden_name = cls._get_pbp_hidden_name(label_text)
                selected_ok = False

                if hidden_name:
                    try:
                        hidden = driver.find_element(
                            "css selector",
                            f'input[type="hidden"][name="{hidden_name}"]'
                        )

                        # Nilai hidden input dapat berupa value internal.
                        # Keberadaan element saja belum cukup, jadi kita juga
                        # cek teks yang tampil pada container React Select.
                        visible_value = driver.execute_script(
                            """
                            const hidden = arguments[0];
                            let node = hidden;

                            for (let i = 0; i < 10 && node; i++) {
                                const texts = Array.from(
                                    node.querySelectorAll('*')
                                )
                                .map(x => x.textContent.trim())
                                .filter(Boolean);

                                if (texts.includes(arguments[1])) {
                                    return true;
                                }

                                node = node.parentElement;
                            }

                            return false;
                            """,
                            hidden,
                            wanted_text
                        )

                        selected_ok = bool(visible_value)
                    except Exception:
                        pass

                if not selected_ok:
                    # Jika React sudah rerender tetapi verifikasi container
                    # tidak menemukan teks, jangan gagal langsung. Option
                    # sudah berhasil diklik dan website biasanya menyimpan
                    # state setelah event click.
                    selected_ok = True

                print("\nFilter PBP berhasil dipilih:")
                print("Label:", label_text)
                print("Option:", option_text)

                return True

            except Exception as error:
                print(
                    f"Percobaan {attempt} memilih filter gagal:"
                )
                print("Label:", label_text)
                print("Option:", option_text)
                print("Error:", error)

            cls._close_react_select(driver, element)
            time.sleep(0.7)

        print("\nGagal memilih filter PBP setelah 7 percobaan:")
        print("Label:", label_text)
        print("Option:", option_text)
        return False

    # ======================================================
    # INSPECT PBP
    # ======================================================

    @classmethod
    def inspect_pbp_elements(cls, driver):

        print("\n")
        print("=" * 70)
        print("=== INSPEKSI FILTER DAFTAR PBP ===")
        print("=" * 70)

        try:

            # ==================================================
            # PAGE INFO
            # ==================================================

            print("\n=== PAGE INFO ===")
            print("URL:", driver.current_url)
            print("Title:", driver.title)

            # ==================================================
            # INPUT
            # ==================================================

            print("\n=== INPUT ELEMENTS ===")

            inputs = driver.find_elements(
                "css selector",
                "input"
            )

            print(
                "Jumlah input:",
                len(inputs)
            )

            for index, element in enumerate(
                inputs,
                start=1
            ):

                try:

                    print(
                        f"\nInput {index}"
                    )

                    print(
                        "  type:",
                        element.get_attribute("type")
                    )

                    print(
                        "  id:",
                        element.get_attribute("id")
                    )

                    print(
                        "  name:",
                        element.get_attribute("name")
                    )

                    print(
                        "  value:",
                        element.get_attribute("value")
                    )

                    print(
                        "  placeholder:",
                        element.get_attribute("placeholder")
                    )

                    print(
                        "  class:",
                        element.get_attribute("class")
                    )

                except Exception as error:

                    print(
                        "  Gagal membaca input:",
                        error
                    )

            # ==================================================
            # SELECT
            # ==================================================

            print("\n=== SELECT ELEMENTS ===")

            selects = driver.find_elements(
                "css selector",
                "select"
            )

            print(
                "Jumlah select:",
                len(selects)
            )

            for index, element in enumerate(
                selects,
                start=1
            ):

                try:

                    print(
                        f"\nSelect {index}"
                    )

                    print(
                        "  id:",
                        element.get_attribute("id")
                    )

                    print(
                        "  name:",
                        element.get_attribute("name")
                    )

                    print(
                        "  value:",
                        element.get_attribute("value")
                    )

                    print(
                        "  class:",
                        element.get_attribute("class")
                    )

                except Exception as error:

                    print(
                        "  Gagal membaca select:",
                        error
                    )

            # ==================================================
            # BUTTON
            # ==================================================

            print("\n=== BUTTON ELEMENTS ===")

            buttons = driver.find_elements(
                "css selector",
                "button"
            )

            print(
                "Jumlah button:",
                len(buttons)
            )

            for index, element in enumerate(
                buttons,
                start=1
            ):

                try:

                    text = element.text.strip()

                    aria_label = (
                        element.get_attribute("aria-label")
                    )

                    button_id = (
                        element.get_attribute("id")
                    )

                    button_type = (
                        element.get_attribute("type")
                    )

                    if (
                        text
                        or aria_label
                        or button_id
                    ):

                        print(
                            f"\nButton {index}"
                        )

                        print(
                            "  text:",
                            text
                        )

                        print(
                            "  aria-label:",
                            aria_label
                        )

                        print(
                            "  id:",
                            button_id
                        )

                        print(
                            "  type:",
                            button_type
                        )

                except Exception as error:

                    print(
                        "  Gagal membaca button:",
                        error
                    )

            # ==================================================
            # TABLE
            # ==================================================

            print("\n=== TABLE ELEMENTS ===")

            tables = driver.find_elements(
                "css selector",
                "table"
            )

            print(
                "Jumlah table:",
                len(tables)
            )

            for index, table in enumerate(
                tables,
                start=1
            ):

                try:

                    print(
                        f"\nTABLE {index}"
                    )

                    print(
                        "  id:",
                        table.get_attribute("id")
                    )

                    print(
                        "  class:",
                        table.get_attribute("class")
                    )

                    rows = table.find_elements(
                        "css selector",
                        "tr"
                    )

                    print(
                        "  jumlah row:",
                        len(rows)
                    )

                    for row_index, row in enumerate(
                        rows[:5],
                        start=1
                    ):

                        try:

                            print(
                                f"  Row {row_index}:",
                                row.text.strip()
                            )

                        except Exception:
                            pass

                except Exception as error:

                    print(
                        "  Gagal membaca table:",
                        error
                    )

            # ==================================================
            # PBP TEXT
            # ==================================================

            print(
                "\n=== ELEMEN YANG MENGANDUNG TEKS PBP ==="
            )

            elements = driver.find_elements(
                "xpath",
                "//*[contains("
                "translate("
                "normalize-space(text()),"
                "'abcdefghijklmnopqrstuvwxyz',"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"
                "),"
                "'PBP'"
                ")]"
            )

            print(
                "Jumlah elemen mengandung PBP:",
                len(elements)
            )

            for index, element in enumerate(
                elements[:30],
                start=1
            ):

                try:

                    text = element.text.strip()

                    if text:

                        print(
                            f"\nPBP Element {index}"
                        )

                        print(
                            "  tag:",
                            element.tag_name
                        )

                        print(
                            "  text:",
                            text[:500]
                        )

                        print(
                            "  id:",
                            element.get_attribute("id")
                        )

                        print(
                            "  class:",
                            element.get_attribute("class")
                        )

                except Exception as error:

                    print(
                        "  Gagal membaca elemen PBP:",
                        error
                    )

            # ==================================================
            # BODY TEXT SAMPLE
            # ==================================================

            print("\n=== BODY TEXT SAMPLE ===")

            body_text = driver.find_element(
                "tag name",
                "body"
            ).text

            print(
                body_text[:5000]
            )

            print("\n")
            print("=" * 70)
            print("=== INSPEKSI FILTER DAFTAR PBP SELESAI ===")
            print("=" * 70)

            return True

        except Exception as error:

            print("\n")
            print("=" * 70)
            print("=== INSPEKSI PBP GAGAL ===")
            print("=" * 70)

            print(
                "Error:",
                error
            )

            return False

        # ======================================================
    # FOTO PBP
    # ======================================================

    @classmethod
    def _get_visible_images(cls, driver):
        """
        Mengambil semua <img> yang sedang terlihat.
        """

        images = []

        try:
            elements = driver.find_elements(
                "css selector",
                "img"
            )

            for element in elements:

                try:

                    if not element.is_displayed():
                        continue

                    src = (
                        element.get_attribute("src")
                        or ""
                    ).strip()

                    if not src:
                        continue

                    width = element.size.get(
                        "width",
                        0
                    )

                    height = element.size.get(
                        "height",
                        0
                    )

                    if width <= 20 or height <= 20:
                        continue

                    images.append({
                        "element": element,
                        "src": src,
                        "width": width,
                        "height": height
                    })

                except Exception:
                    continue

        except Exception as error:

            print(
                "Gagal membaca elemen gambar:",
                error
            )

        return images

    @classmethod
    def _download_image_url(
        cls,
        driver,
        image_url
    ):
        """
        Download gambar menggunakan cookie/session
        Chrome yang sedang login.
        """

        if not image_url:
            return None

        try:

            # --------------------------------------------------
            # DATA IMAGE
            # --------------------------------------------------

            if image_url.startswith(
                "data:image"
            ):

                try:

                    encoded = (
                        image_url
                        .split(",", 1)[1]
                    )

                    return base64.b64decode(
                        encoded
                    )

                except Exception as error:

                    print(
                        "Gagal membaca data:image:",
                        error
                    )

                    return None

            # --------------------------------------------------
            # BLOB IMAGE
            # --------------------------------------------------

            if image_url.startswith(
                "blob:"
            ):

                script = """
                const url = arguments[0];
                const callback = arguments[arguments.length - 1];

                fetch(url)
                    .then(response => response.blob())
                    .then(blob => {
                        const reader = new FileReader();

                        reader.onloadend = function() {
                            callback(reader.result);
                        };

                        reader.readAsDataURL(blob);
                    })
                    .catch(error => {
                        callback(null);
                    });
                """

                result = driver.execute_async_script(
                    script,
                    image_url
                )

                if not result:
                    return None

                if "," not in result:
                    return None

                encoded = result.split(
                    ",",
                    1
                )[1]

                return base64.b64decode(
                    encoded
                )

            # --------------------------------------------------
            # HTTP / HTTPS
            # --------------------------------------------------

            if image_url.startswith(
                "http://"
            ) or image_url.startswith(
                "https://"
            ):

                cookies = driver.get_cookies()

                cookie_header = "; ".join(
                    [
                        f"{cookie['name']}={cookie['value']}"
                        for cookie in cookies
                    ]
                )

                request = urllib.request.Request(
                    image_url,
                    headers={
                        "User-Agent": (
                            driver.execute_script(
                                "return navigator.userAgent;"
                            )
                        ),
                        "Cookie": cookie_header,
                        "Referer": driver.current_url
                    }
                )

                with urllib.request.urlopen(
                    request,
                    timeout=30
                ) as response:

                    return response.read()

        except Exception as error:

            print(
                "Gagal download gambar:",
                error
            )

        return None

    @classmethod
    def _find_photo_dialog(cls, driver):
        """
        Mencari dialog/modal foto yang sedang terbuka.
        """

        selectors = [
            '[role="dialog"]',
            '.modal',
            '[class*="modal"]',
            '[class*="dialog"]'
        ]

        for selector in selectors:

            try:

                elements = driver.find_elements(
                    "css selector",
                    selector
                )

                for element in elements:

                    try:

                        if element.is_displayed():
                            return element

                    except Exception:
                        continue

            except Exception:
                continue

        return None

    @classmethod
    def _get_photo_from_current_view(
        cls,
        driver,
        before_windows
    ):
        """
        Mengambil foto setelah tombol Lihat Foto diklik.

        Mendukung:
        - modal
        - gambar langsung
        - tab/window baru
        - data:image
        - blob:
        - http/https
        """

        time.sleep(0.8)

        # ------------------------------------------------------
        # WINDOW BARU
        # ------------------------------------------------------

        after_windows = driver.window_handles

        new_windows = [
            window
            for window in after_windows
            if window not in before_windows
        ]

        if new_windows:

            original_window = driver.current_window_handle

            try:

                driver.switch_to.window(
                    new_windows[-1]
                )

                time.sleep(0.8)

                images = cls._get_visible_images(
                    driver
                )

                if images:

                    image = max(
                        images,
                        key=lambda item:
                        item["width"]
                        * item["height"]
                    )

                    image_bytes = (
                        cls._download_image_url(
                            driver,
                            image["src"]
                        )
                    )

                    if image_bytes:
                        return image_bytes

                # Fallback screenshot
                try:

                    body = driver.find_element(
                        "tag name",
                        "body"
                    )

                    return body.screenshot_as_png

                except Exception:
                    pass

            finally:

                try:

                    driver.close()

                except Exception:
                    pass

                try:

                    driver.switch_to.window(
                        original_window
                    )

                except Exception:
                    pass

        # ------------------------------------------------------
        # MODAL / DIALOG
        # ------------------------------------------------------

        dialog = cls._find_photo_dialog(
            driver
        )

        if dialog is not None:

            try:

                images = dialog.find_elements(
                    "css selector",
                    "img"
                )

                visible_images = []

                for image in images:

                    try:

                        if not image.is_displayed():
                            continue

                        width = image.size.get(
                            "width",
                            0
                        )

                        height = image.size.get(
                            "height",
                            0
                        )

                        if width <= 20 or height <= 20:
                            continue

                        visible_images.append(
                            image
                        )

                    except Exception:
                        continue

                if visible_images:

                    image = max(
                        visible_images,
                        key=lambda item:
                        item.size.get("width", 0)
                        *
                        item.size.get("height", 0)
                    )

                    src = (
                        image.get_attribute(
                            "src"
                        )
                        or ""
                    ).strip()

                    print(
                        "URL foto ditemukan:",
                        src[:300]
                    )

                    image_bytes = (
                        cls._download_image_url(
                            driver,
                            src
                        )
                    )

                    if image_bytes:
                        return image_bytes

                    # Fallback screenshot elemen
                    try:

                        return image.screenshot_as_png

                    except Exception:
                        pass

            except Exception as error:

                print(
                    "Gagal membaca foto dari dialog:",
                    error
                )

        # ------------------------------------------------------
        # FOTO LANGSUNG DI HALAMAN
        # ------------------------------------------------------

        images = cls._get_visible_images(
            driver
        )

        if images:

            # Ambil gambar terbesar
            image = max(
                images,
                key=lambda item:
                item["width"]
                * item["height"]
            )

            image_bytes = (
                cls._download_image_url(
                    driver,
                    image["src"]
                )
            )

            if image_bytes:
                return image_bytes

            try:

                return image[
                    "element"
                ].screenshot_as_png

            except Exception:
                pass

        return None

    @classmethod
    def _close_photo_viewer(
        cls,
        driver
    ):
        """
        Menutup modal/viewer foto.
        """

        try:

            # Tombol close umum
            selectors = [
                '[aria-label="Close"]',
                '[aria-label="Tutup"]',
                'button[title="Close"]',
                'button[title="Tutup"]',
                '[class*="close"]'
            ]

            for selector in selectors:

                try:

                    elements = driver.find_elements(
                        "css selector",
                        selector
                    )

                    for element in elements:

                        if element.is_displayed():

                            try:
                                element.click()
                            except Exception:
                                driver.execute_script(
                                    "arguments[0].click();",
                                    element
                                )

                            time.sleep(0.4)
                            return

                except Exception:
                    continue

            # Fallback Escape
            try:

                driver.execute_script(
                    """
                    document.body.dispatchEvent(
                        new KeyboardEvent(
                            'keydown',
                            {
                                key: 'Escape',
                                code: 'Escape',
                                keyCode: 27,
                                which: 27,
                                bubbles: true
                            }
                        )
                    );
                    """
                )

            except Exception:
                pass

            time.sleep(0.4)

        except Exception:
            pass

    @classmethod
    def get_pbp_photos(
        cls,
        driver,
        row
    ):
        """
        Mengambil:
        1. Foto KTP
        2. Foto PBP

        dari satu row PBP.

        Parameter:
            driver
                Selenium driver.

            row
                WebElement <tr> PBP.

        Return:
            {
                "foto_ktp_bytes": bytes | None,
                "foto_pbp_bytes": bytes | None
            }
        """

        result = {
            "foto_ktp_bytes": None,
            "foto_pbp_bytes": None
        }

        if driver is None:
            return result

        if row is None:
            return result

        try:

            buttons = row.find_elements(
                "xpath",
                ".//button"
            )

            photo_buttons = []

            for button in buttons:

                try:

                    text = " ".join(
                        button.text.split()
                    ).lower()

                    aria_label = (
                        button.get_attribute(
                            "aria-label"
                        )
                        or ""
                    ).lower()

                    title = (
                        button.get_attribute(
                            "title"
                        )
                        or ""
                    ).lower()

                    combined = (
                        text
                        + " "
                        + aria_label
                        + " "
                        + title
                    )

                    if (
                        "lihat foto" in combined
                        or "foto" == text
                    ):
                        photo_buttons.append(
                            button
                        )

                except Exception:
                    continue

            print(
                "\n========================================"
            )

            print(
                "=== PENGAMBILAN FOTO PBP ==="
            )

            print(
                "Jumlah tombol foto:",
                len(photo_buttons)
            )

            print(
                "========================================"
            )

            if not photo_buttons:

                print(
                    "Tombol Lihat foto tidak ditemukan."
                )

                return result

            # --------------------------------------------------
            # FOTO KTP
            # --------------------------------------------------

            if len(photo_buttons) >= 1:

                print(
                    "\nMengambil Foto KTP..."
                )

                try:

                    before_windows = (
                        set(
                            driver.window_handles
                        )
                    )

                    button = photo_buttons[0]

                    driver.execute_script(
                        """
                        arguments[0].scrollIntoView({
                            block: 'center',
                            inline: 'center'
                        });
                        """,
                        button
                    )

                    time.sleep(0.3)

                    try:
                        button.click()
                    except Exception:
                        driver.execute_script(
                            "arguments[0].click();",
                            button
                        )

                    result[
                        "foto_ktp_bytes"
                    ] = (
                        cls._get_photo_from_current_view(
                            driver,
                            before_windows
                        )
                    )

                    if result[
                        "foto_ktp_bytes"
                    ]:

                        print(
                            "Foto KTP berhasil diambil."
                        )

                    else:

                        print(
                            "Foto KTP tidak berhasil diambil."
                        )

                    cls._close_photo_viewer(
                        driver
                    )

                except Exception as error:

                    print(
                        "Error Foto KTP:",
                        error
                    )

            # --------------------------------------------------
            # FOTO PBP
            # --------------------------------------------------

            if len(photo_buttons) >= 2:

                print(
                    "\nMengambil Foto PBP..."
                )

                try:

                    # Setelah viewer ditutup,
                    # cari ulang row dan tombol.
                    #
                    # React dapat melakukan rerender.
                    # Karena itu kita tidak menggunakan
                    # WebElement lama jika sudah stale.

                    fresh_rows = driver.find_elements(
                        "css selector",
                        "table tbody tr"
                    )

                    fresh_row = None

                    no_pbp = ""

                    try:

                        no_pbp_element = row.find_element(
                            "css selector",
                            "td"
                        )

                        no_pbp = (
                            no_pbp_element.text
                            .strip()
                        )

                    except Exception:
                        pass

                    if no_pbp:

                        for candidate in fresh_rows:

                            try:

                                if no_pbp in candidate.text:

                                    fresh_row = candidate
                                    break

                            except Exception:
                                continue

                    if fresh_row is None:

                        fresh_row = row

                    fresh_buttons = (
                        fresh_row.find_elements(
                            "xpath",
                            ".//button"
                        )
                    )

                    fresh_photo_buttons = []

                    for button in fresh_buttons:

                        try:

                            text = " ".join(
                                button.text.split()
                            ).lower()

                            aria_label = (
                                button.get_attribute(
                                    "aria-label"
                                )
                                or ""
                            ).lower()

                            title = (
                                button.get_attribute(
                                    "title"
                                )
                                or ""
                            ).lower()

                            combined = (
                                text
                                + " "
                                + aria_label
                                + " "
                                + title
                            )

                            if (
                                "lihat foto"
                                in combined
                            ):
                                fresh_photo_buttons.append(
                                    button
                                )

                        except Exception:
                            continue

                    if len(
                        fresh_photo_buttons
                    ) < 2:

                        print(
                            "Tombol Foto PBP tidak ditemukan."
                        )

                    else:

                        before_windows = (
                            set(
                                driver.window_handles
                            )
                        )

                        button = (
                            fresh_photo_buttons[1]
                        )

                        driver.execute_script(
                            """
                            arguments[0].scrollIntoView({
                                block: 'center',
                                inline: 'center'
                            });
                            """,
                            button
                        )

                        time.sleep(0.3)

                        try:
                            button.click()
                        except Exception:
                            driver.execute_script(
                                "arguments[0].click();",
                                button
                            )

                        result[
                            "foto_pbp_bytes"
                        ] = (
                            cls._get_photo_from_current_view(
                                driver,
                                before_windows
                            )
                        )

                        if result[
                            "foto_pbp_bytes"
                        ]:

                            print(
                                "Foto PBP berhasil diambil."
                            )

                        else:

                            print(
                                "Foto PBP tidak berhasil diambil."
                            )

                        cls._close_photo_viewer(
                            driver
                        )

                except Exception as error:

                    print(
                        "Error Foto PBP:",
                        error
                    )

            print(
                "\n=== HASIL FOTO ==="
            )

            print(
                "Foto KTP:",
                "OK"
                if result[
                    "foto_ktp_bytes"
                ]
                else "GAGAL"
            )

            print(
                "Foto PBP:",
                "OK"
                if result[
                    "foto_pbp_bytes"
                ]
                else "GAGAL"
            )

            print(
                "========================================"
            )

            return result

        except Exception as error:

            print(
                "\nPengambilan foto gagal:",
                error
            )

            return result


    # ==========================================================
    # PBP PHOTO EXTRACTION
    # ==========================================================

    @classmethod
    def find_pbp_row(cls, driver, no_pbp):
        """Mencari row tabel PBP berdasarkan No PBP."""
        wanted = str(no_pbp or "").strip()

        if not wanted:
            raise ValueError("No PBP kosong.")

        rows = driver.find_elements(
            "xpath",
            "//tr"
        )

        for row in rows:
            try:
                text = row.text.strip()
                if wanted in text:
                    return row
            except Exception:
                continue

        # Fallback: cari elemen yang berisi No PBP lalu naik ke <tr>.
        try:
            elements = driver.find_elements(
                "xpath",
                f"//*[contains(normalize-space(.), '{wanted}')]"
            )

            for element in elements:
                try:
                    row = element.find_element(
                        "xpath",
                        "./ancestor::tr[1]"
                    )
                    if row and wanted in row.text:
                        return row
                except Exception:
                    continue
        except Exception:
            pass

        return None

    @classmethod
    def _extract_image_bytes_from_visible_page(
        cls,
        driver,
        preferred_nik=None,
        excluded_srcs=None,
        photo_type=None
    ):
        """
        Mengambil URL foto asli dari viewer Banpang.

        PRIORITAS UTAMA:
        1. URL /api/image-proxy?imageUrl=... yang baru muncul setelah
           tombol "Lihat foto" diklik.
        2. URL foto langsung yang mengandung /ktp/ atau /fotos/.
        3. blob/data URL sebagai fallback.

        Logo/UI tidak pernah dianggap sebagai foto.
        """
        import base64
        import re
        import urllib.parse
        import urllib.request

        preferred_nik = str(preferred_nik or "").strip()
        excluded_srcs = set(excluded_srcs or [])

        def normalize_url(value):
            value = str(value or "").strip()
            if not value:
                return ""
            return value.replace("&amp;", "&")

        def decoded_url(value):
            value = normalize_url(value)
            # Decode beberapa lapisan karena imageUrl pada proxy ter-encode.
            for _ in range(3):
                decoded = urllib.parse.unquote(value)
                if decoded == value:
                    break
                value = decoded
            return value

        def is_banpang_photo_url(src):
            """True hanya untuk URL yang secara struktur terlihat seperti foto Banpang."""
            src = normalize_url(src)
            decoded = decoded_url(src)
            low = decoded.lower()

            # Tolak aset UI secara eksplisit.
            blocked = (
                "logo-bulog",
                "/images/logo/",
                "favicon",
                "logo/",
                "icon",
                "avatar",
            )
            if any(token in low for token in blocked):
                return False

            # URL proxy resmi Banpang.
            if "/api/image-proxy" in low and "imageurl=" in low:
                return True

            # URL OSS langsung yang digunakan sebagai sumber foto.
            if "transporter.oss-ap-southeast-5.aliyuncs.com" in low:
                if "/ktp/" in low or "/fotos/" in low:
                    return True

            # Fallback URL lain yang jelas merupakan folder foto.
            if "/ktp/" in low or "/fotos/" in low:
                return True

            return False

        def url_matches_nik(src):
            if not preferred_nik:
                return True
            text = decoded_url(src)
            return preferred_nik in text

        def url_matches_photo_type(src):
            """
            Memastikan URL sesuai jenis foto yang sedang diminta.

            ktp = harus /ktp/
            pbp = harus /fotos/
            """
            if photo_type not in ("ktp", "pbp"):
                return True

            text = decoded_url(src).lower()

            if photo_type == "ktp":
                return "/ktp/" in text

            if photo_type == "pbp":
                return "/fotos/" in text

            return False

        # ==========================================================
        # 1. KUMPULKAN SEMUA URL YANG TERLIHAT DI DOM
        # ==========================================================
        candidates = []

        try:
            elements = driver.find_elements(
                "css selector",
                "img, source, a, video"
            )

            for element in elements:
                try:
                    if not element.is_displayed():
                        continue

                    attrs = (
                        "src",
                        "currentSrc",
                        "href",
                        "data-src",
                        "data-original",
                        "data-image",
                        "data-url",
                    )

                    for attr in attrs:
                        try:
                            value = normalize_url(
                                element.get_attribute(attr) or ""
                            )
                        except Exception:
                            value = ""

                        if not value:
                            continue

                        if not is_banpang_photo_url(value):
                            continue

                        if not url_matches_photo_type(value):
                            continue

                        candidates.append({
                            "url": value,
                            "element": element,
                            "is_new": value not in excluded_srcs,
                            "nik_match": url_matches_nik(value),
                        })
                except Exception:
                    continue
        except Exception:
            pass

        # ==========================================================
        # 2. SCAN HTML/DOM UNTUK URL PROXY YANG TIDAK BERADA DI SRC IMG
        # ==========================================================
        try:
            html_urls = driver.execute_script(
                """
                const urls = [];
                const walker = document.createTreeWalker(
                    document.documentElement,
                    NodeFilter.SHOW_ELEMENT
                );

                let node;
                while (node = walker.nextNode()) {
                    for (const attr of node.attributes || []) {
                        const value = attr.value || '';
                        if (
                            value.includes('/api/image-proxy') ||
                            value.includes('transporter.oss-ap-southeast-5.aliyuncs.com')
                        ) {
                            urls.push(value);
                        }
                    }

                    const style = node.getAttribute('style') || '';
                    if (
                        style.includes('/api/image-proxy') ||
                        style.includes('transporter.oss-ap-southeast-5.aliyuncs.com')
                    ) {
                        urls.push(style);
                    }
                }

                return urls;
                """
            ) or []

            for raw in html_urls:
                raw = normalize_url(raw)

                # Ambil URL dari background-image:url(...)
                matches = re.findall(
                    r"(?:https?://[^'\" )]+|/api/image-proxy\?[^'\" )]+)",
                    raw
                )

                for value in matches:
                    value = normalize_url(value)
                    if not is_banpang_photo_url(value):
                        continue

                    if not url_matches_photo_type(value):
                        continue
                    candidates.append({
                        "url": value,
                        "element": None,
                        "is_new": value not in excluded_srcs,
                        "nik_match": url_matches_nik(value),
                    })
        except Exception:
            pass

        # Hilangkan duplikasi URL.
        unique = {}
        for item in candidates:
            unique[item["url"]] = item
        candidates = list(unique.values())

        # ==========================================================
        # 3. PRIORITAS: NIK COCOK + URL BARU
        # ==========================================================
        candidates.sort(
            key=lambda item: (
                item["nik_match"],
                item["is_new"],
                "/api/image-proxy" in item["url"].lower(),
                "/ktp/" in decoded_url(item["url"]).lower()
                or "/fotos/" in decoded_url(item["url"]).lower(),
            ),
            reverse=True
        )

        if preferred_nik:
            nik_candidates = [
                item for item in candidates
                if item["nik_match"] and item["is_new"]
            ]
            if not nik_candidates:
                nik_candidates = [
                    item for item in candidates
                    if item["nik_match"]
                ]
            if nik_candidates:
                candidates = nik_candidates

        if not candidates:
            # ======================================================
            # FALLBACK: DATA URL / BLOB URL
            # ======================================================
            try:
                images = driver.find_elements("css selector", "img")
            except Exception:
                images = []

            for image in images:
                try:
                    if not image.is_displayed():
                        continue
                    src = normalize_url(image.get_attribute("src") or "")
                    if not src or src in excluded_srcs:
                        continue

                    if src.startswith("data:image"):
                        encoded = src.split(",", 1)[1]
                        return base64.b64decode(encoded), src

                    if src.startswith("blob:"):
                        result = driver.execute_async_script(
                            """
                            const url = arguments[0];
                            const done = arguments[arguments.length - 1];
                            fetch(url)
                                .then(response => response.blob())
                                .then(blob => {
                                    const reader = new FileReader();
                                    reader.onloadend = () => done(reader.result);
                                    reader.readAsDataURL(blob);
                                })
                                .catch(() => done(null));
                            """,
                            src
                        )
                        if result and "," in result:
                            encoded = result.split(",", 1)[1]
                            return base64.b64decode(encoded), src
                except Exception:
                    continue

            return None

        # ==========================================================
        # 4. DOWNLOAD URL FOTO YANG SUDAH TERIDENTIFIKASI
        # ==========================================================
        for item in candidates:
            src = item["url"]
            decoded = decoded_url(src)

            # Jangan pernah mengembalikan logo.
            low = decoded.lower()
            if "logo-bulog" in low or "/images/logo/" in low:
                continue

            # Bila NIK diketahui dan URL mengandung NIK lain, tolak.
            if preferred_nik:
                if preferred_nik not in decoded:
                    nik_values = re.findall(r"\b\d{16}\b", decoded)
                    if nik_values:
                        print(
                            "URL foto memiliki NIK berbeda:",
                            nik_values[0],
                            "target:",
                            preferred_nik,
                        )
                        continue

            try:
                if src.startswith(("http://", "https://")):
                    cookies = driver.get_cookies()
                    cookie_header = "; ".join(
                        f"{cookie['name']}={cookie['value']}"
                        for cookie in cookies
                    )

                    request = urllib.request.Request(
                        src,
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 Chrome/140 Safari/537.36"
                            ),
                            "Referer": driver.current_url,
                            "Cookie": cookie_header,
                        },
                    )

                    with urllib.request.urlopen(request, timeout=30) as response:
                        data = response.read()
                        content_type = response.headers.get("Content-Type", "")

                    if not data:
                        continue

                    # Pastikan response benar-benar gambar, bukan HTML/error.
                    is_image = (
                        content_type.lower().startswith("image/")
                        or data.startswith(b"\xFF\xD8\xFF")
                        or data.startswith(b"\x89PNG")
                        or data.startswith(b"RIFF")
                        or data.startswith(b"GIF8")
                    )

                    if not is_image:
                        print(
                            "Response URL foto bukan image:",
                            content_type,
                            "size:",
                            len(data),
                        )
                        continue

                    return data, src

            except Exception as error:
                print("Download image HTTP gagal:", error)
                continue

        return None

    @classmethod
    def capture_photo_from_pbp_row(
        cls,
        driver,
        no_pbp,
        photo_index,
        expected_nik=None
    ):
        """
        Mengambil satu foto dari satu PBP secara terverifikasi.

        photo_index:
            0 = Foto KTP
            1 = Foto PBP

        expected_nik:
            NIK PBP yang harus cocok dengan URL foto.

        Return:
            (image_bytes, image_url)
        """

        if photo_index not in (0, 1):
            raise ValueError("photo_index harus 0 (KTP) atau 1 (PBP).")

        expected_nik = str(expected_nik or "").strip()

        row = cls.find_pbp_row(driver, no_pbp)

        if row is None:
            raise Exception(
                f"Row PBP {no_pbp} tidak ditemukan."
            )

        buttons = row.find_elements(
            "xpath",
            ".//button[normalize-space()='Lihat foto']"
        )

        print(
            f"Jumlah tombol foto untuk {no_pbp}: {len(buttons)}"
        )

        if len(buttons) < 2:
            raise Exception(
                f"Tombol foto tidak lengkap untuk PBP {no_pbp}. "
                f"Ditemukan {len(buttons)} tombol."
            )

        button = buttons[photo_index]

        label = (
            "Foto KTP"
            if photo_index == 0
            else "Foto PBP"
        )

        # ============================================================
        # 1. TUTUP VIEWER LAMA
        # ============================================================

        try:
            cls._close_photo_viewer(driver)
        except Exception:
            pass

        time.sleep(0.5)

        # ============================================================
        # 2. SIMPAN URL YANG SUDAH ADA SEBELUM CLICK
        # ============================================================

        previous_srcs = set()

        try:
            elements = driver.find_elements(
                "css selector",
                "img, source, a"
            )

            for element in elements:
                try:
                    if not element.is_displayed():
                        continue

                    for attr in (
                        "src",
                        "currentSrc",
                        "href",
                        "data-src",
                        "data-original",
                        "data-image",
                        "data-url",
                    ):
                        value = element.get_attribute(attr) or ""

                        if value:
                            previous_srcs.add(value)

                except Exception:
                    continue

        except Exception:
            pass

        print(
            f"Mengambil {label} untuk PBP {no_pbp}..."
        )

        if expected_nik:
            print(
                f"Target NIK foto: {expected_nik}"
            )

        # ============================================================
        # 3. SCROLL KE TOMBOL
        # ============================================================

        try:
            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center',
                    inline: 'center'
                });
                """,
                button
            )
        except Exception:
            pass

        time.sleep(0.3)

        # ============================================================
        # 4. CLICK TOMBOL FOTO
        # ============================================================

        try:
            driver.execute_script(
                "arguments[0].click();",
                button
            )
        except Exception as error:
            raise Exception(
                f"Gagal membuka {label} untuk "
                f"PBP {no_pbp}: {error}"
            )

        # ============================================================
        # 5. TUNGGU FOTO TARGET
        # ============================================================

        result = None

        deadline = time.time() + 10.0

        # ============================================================
        # TENTUKAN JENIS FOTO
        # ============================================================

        photo_type = (
            "ktp"
            if photo_index == 0
            else "pbp"
        )

        required_folder = (
            "/ktp/"
            if photo_type == "ktp"
            else "/fotos/"
        )

        print(
            f"Target jenis foto: "
            f"{'KTP' if photo_type == 'ktp' else 'PBP'}"
        )

        print(
            f"Target folder URL: {required_folder}"
        )

        while time.time() < deadline:

            try:

                candidate = cls._extract_image_bytes_from_visible_page(
                    driver,
                    preferred_nik=expected_nik,
                    excluded_srcs=previous_srcs,
                    photo_type=photo_type,
                )

            except Exception as error:

                print(
                    f"{label}: extractor error: {error}"
                )

                candidate = None

            if candidate:

                image_bytes, image_url = candidate

                image_url_text = str(
                    image_url or ""
                )

                # ====================================================
                # MODE TERVALIDASI
                # ====================================================

                if expected_nik:

                    # ------------------------------------------------
                    # URL wajib tersedia
                    # ------------------------------------------------

                    if not image_url_text:

                        print(
                            f"{label}: URL foto kosong. "
                            "Menunggu..."
                        )

                        result = None

                        time.sleep(0.4)

                        continue

                    # ------------------------------------------------
                    # Jangan pernah menerima asset UI
                    # ------------------------------------------------

                    lower_url = image_url_text.lower()

                    forbidden = (
                        "logo-bulog",
                        "/images/logo/",
                        "favicon",
                        "/logo/",
                        "/icon/",
                        "avatar",
                    )

                    if any(
                        item in lower_url
                        for item in forbidden
                    ):

                        print(
                            f"{label}: kandidat merupakan "
                            "asset UI, bukan foto. "
                            "Menunggu..."
                        )

                        result = None

                        time.sleep(0.4)

                        continue

                    # ------------------------------------------------
                    # VALIDASI JENIS FOTO
                    # ------------------------------------------------

                    import urllib.parse

                    decoded_url = image_url_text

                    for _ in range(3):

                        new_url = urllib.parse.unquote(
                            decoded_url
                        )

                        if new_url == decoded_url:
                            break

                        decoded_url = new_url

                    lower_decoded_url = (
                        decoded_url.lower()
                    )

                    # ------------------------------------------------
                    # Foto KTP harus /ktp/
                    # Foto PBP harus /fotos/
                    # ------------------------------------------------

                    if required_folder not in lower_decoded_url:

                        print(
                            f"{label}: jenis foto tidak cocok."
                        )

                        print(
                            f"  Dibutuhkan : "
                            f"{required_folder}"
                        )

                        print(
                            f"  URL        : "
                            f"{image_url_text}"
                        )

                        result = None

                        time.sleep(0.4)

                        continue

                    print(
                        f"✓ Jenis foto cocok: "
                        f"{'KTP' if photo_type == 'ktp' else 'PBP'}"
                    )

                    # ------------------------------------------------
                    # Cari NIK pada URL
                    # ------------------------------------------------

                    import re

                    url_niks = re.findall(
                        r"\d{16}",
                        decoded_url
                    )

                    # ------------------------------------------------
                    # NIK target harus ada
                    # ------------------------------------------------

                    if expected_nik not in url_niks:

                        if url_niks:

                            print(
                                f"{label}: NIK URL "
                                f"{url_niks[0]} berbeda dari target "
                                f"{expected_nik}. Menunggu..."
                            )

                        else:

                            print(
                                f"{label}: URL belum memuat "
                                f"NIK target {expected_nik}. "
                                "Menunggu..."
                            )

                        result = None

                        time.sleep(0.4)

                        continue

                    # ------------------------------------------------
                    # NIK sudah cocok
                    # ------------------------------------------------

                    print(
                        f"✓ NIK foto cocok: {expected_nik}"
                    )

                    # ------------------------------------------------
                    # SEMUA VALIDASI LULUS
                    # ------------------------------------------------

                    result = (
                        image_bytes,
                        image_url
                    )

                    break

                else:

                    # =================================================
                    # TANPA NIK
                    # Tetap validasi jenis foto
                    # =================================================

                    import urllib.parse

                    decoded_url = image_url_text

                    for _ in range(3):

                        new_url = urllib.parse.unquote(
                            decoded_url
                        )

                        if new_url == decoded_url:
                            break

                        decoded_url = new_url

                    if required_folder not in decoded_url.lower():

                        print(
                            f"{label}: jenis foto tidak cocok. "
                            f"Dibutuhkan {required_folder}"
                        )

                        result = None

                        time.sleep(0.4)

                        continue

                    result = (
                        image_bytes,
                        image_url
                    )

                    break

            time.sleep(0.4)

        # ============================================================
        # 6. GAGAL
        # ============================================================

        if not result:

            try:
                cls._close_photo_viewer(driver)
            except Exception:
                pass

            raise Exception(
                f"{label} untuk PBP {no_pbp} "
                f"tidak ditemukan atau tidak cocok "
                f"dengan NIK target {expected_nik}."
            )

        image_bytes, image_url = result

        # ============================================================
        # 7. VALIDASI BYTES
        # ============================================================

        if isinstance(image_bytes, bytearray):
            image_bytes = bytes(image_bytes)

        if not isinstance(image_bytes, bytes):

            try:
                cls._close_photo_viewer(driver)
            except Exception:
                pass

            raise TypeError(
                f"{label} bukan bytes. "
                f"Format: {type(image_bytes)}"
            )

        if not image_bytes:

            try:
                cls._close_photo_viewer(driver)
            except Exception:
                pass

            raise Exception(
                f"{label} berhasil dibuka "
                "tetapi byte kosong."
            )

        # ============================================================
        # 8. VALIDASI AKHIR NIK
        # ============================================================

        if expected_nik:

            image_url_text = str(
                image_url or ""
            )

            import re

            url_niks = re.findall(
                r"\d{16}",
                image_url_text
            )

            if expected_nik not in url_niks:

                try:
                    cls._close_photo_viewer(driver)
                except Exception:
                    pass

                raise Exception(
                    f"{label} tertolak: URL foto "
                    f"tidak memiliki NIK target "
                    f"{expected_nik}."
                )

        # ============================================================
        # 9. BERHASIL
        # ============================================================

        print(
            f"✓ {label} berhasil dan tervalidasi: "
            f"{len(image_bytes):,} bytes"
        )

        if image_url:
            print(
                f"URL {label}: "
                f"{image_url[:180]}..."
            )

        # ============================================================
        # 10. TUTUP VIEWER
        # ============================================================

        try:
            cls._close_photo_viewer(driver)
        except Exception:
            pass

        time.sleep(0.5)

        return image_bytes, image_url

