import json
from pathlib import Path


class ResourceManager:

    # ========================================================
    # GESTOR DE RECURSOS
    # ========================================================
    # Descubre recursos (Tools, Features, Environments,
    # Technologies) buscando archivos JSON de metadata.
    #
    # Cada categoría tiene su propio nombre de archivo:
    #
    # TOOLS/         → tool.json
    # FEATURES/      → feature.json
    # ENVIRONMENTS/  → environment.json
    # TECHNOLOGIES/  → technology.json
    #
    # El ResourceManager es genérico: recibe la carpeta y el
    # nombre del archivo de metadata, y devuelve la lista de
    # recursos encontrados.
    # ========================================================

    def __init__(self, base_dir: Path, metadata_filename: str):
        self.base_dir = base_dir
        self.metadata_filename = metadata_filename

    # ========================================================
    # DESCUBRIR RECURSOS
    # ========================================================
    # Busca recursivamente el archivo de metadata dentro de
    # la carpeta base y devuelve la lista de recursos.
    # ========================================================

    def discover(self) -> list[dict]:

        resources = []

        if not self.base_dir.exists():
            return resources

        for metadata_file in self.base_dir.rglob(self.metadata_filename):

            try:
                with open(metadata_file, "r", encoding="utf-8") as file:
                    metadata = json.load(file)

                metadata["path"] = metadata_file.parent

                resources.append(metadata)

            except (json.JSONDecodeError, OSError):
                continue

        return resources