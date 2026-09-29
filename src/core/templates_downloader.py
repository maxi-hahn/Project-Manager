import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable

from src.template_manager import TemplateManager

TEMPLATES_REPO_URL = (
    "https://github.com/maxi-hahn/project-manager-templates"
)
TEMPLATES_ZIP_URL = (
    "https://github.com/maxi-hahn/project-manager-templates/"
    "archive/refs/heads/main.zip"
)


def download_templates(
    destination: Path,
    logger: Callable[[str], None] | None = None,
    overwrite: bool = False,
) -> bool:
    """
    Downloads the templates zip and extracts it into `destination`.

    Steps:
    1. If destination already contains a "TEMPLATES" folder and
       overwrite is False, log a message and return False.
    2. Create destination if it doesn't exist.
    3. Download the zip to a temporary file
       (using urllib.request.urlopen).
    4. Extract the zip contents.
    5. The zip contains a top-level folder
       "project-manager-templates-main/". Move its contents up to
       destination (so destination/TEMPLATES/, destination/TOOLS/,
       etc.).
    6. Clean up the temporary zip and empty top-level folder.
    7. Log progress lines via logger (Callable[[str], None]).
    8. Return True on success, False on failure.

    Handle:
    - Network errors (URLError).
    - Zip extraction errors (BadZipFile).
    - Permission errors (OSError).

    Never raise.
    """

    def log(msg: str):
        if logger:
            try:
                logger(msg)
            except Exception:
                pass

    destination = Path(destination)
    templates_dir = destination / "TEMPLATES"

    if templates_dir.exists() and not overwrite:
        log("✗ La carpeta ya contiene templates.")
        return False

    temp_zip_path = None
    temp_extract_dir = None

    try:
        destination.mkdir(parents=True, exist_ok=True)

        log("→ Descargando templates desde GitHub...")

        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
            temp_zip_path = Path(tmp_file.name)

        req = urllib.request.Request(
            TEMPLATES_ZIP_URL,
            headers={"User-Agent": "ProjectManagerApp/1.0"},
        )
        with urllib.request.urlopen(req) as response, open(
            temp_zip_path, "wb"
        ) as out_file:
            downloaded = 0
            block_size = 8192
            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                downloaded += len(buffer)
                out_file.write(buffer)

        size_mb = f"{downloaded / (1024 * 1024):.1f}"
        log(f"  ✓ Descarga completa ({size_mb} MB).")

        log("→ Extrayendo archivos...")
        temp_extract_dir = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        log("  ✓ Extracción completa.")

        log("→ Moviendo archivos a la carpeta de recursos...")
        extracted_top = temp_extract_dir / "project-manager-templates-main"
        if not extracted_top.exists():
            dirs = [d for d in temp_extract_dir.iterdir() if d.is_dir()]
            if dirs:
                extracted_top = dirs[0]

        for item in extracted_top.iterdir():
            target = destination / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(target))

        count = 0
        if templates_dir.exists():
            try:
                manager = TemplateManager(templates_dir)
                count = len(manager.discover_templates())
            except Exception:
                count = 0

        log(f"  ✓ Listo. {count} templates encontrados.")
        log("✓ Templates descargados correctamente.")
        return True

    except urllib.error.URLError as e:
        log(
            f"✗ No se pudo descargar los templates: Error de red ({e.reason if hasattr(e, 'reason') else e})"
        )
        return False
    except zipfile.BadZipFile as e:
        log(f"✗ No se pudo descargar los templates: Archivo ZIP corrupto ({e})")
        return False
    except OSError as e:
        log(
            f"✗ No se pudo descargar los templates: Error de sistema de archivos ({e})"
        )
        return False
    except Exception as e:
        log(f"✗ No se pudo descargar los templates: {e}")
        return False
    finally:
        if temp_zip_path and temp_zip_path.exists():
            try:
                temp_zip_path.unlink()
            except Exception:
                pass
        if temp_extract_dir and temp_extract_dir.exists():
            try:
                shutil.rmtree(temp_extract_dir)
            except Exception:
                pass
