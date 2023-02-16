from os.path import normpath, dirname, join


class Config:
    def __init__(
            self,
            base_directory: str = None,
            import_directory: str = None,
            import_marker_path: str = None,
            header_path: str = None,
            entities_path: str = None,
            dataset_path: str = None,
    ):
        if base_directory is None:
            base_directory = normpath(dirname(dirname(dirname(__file__))))
        self.base_directory = base_directory

        if import_directory is None:
            import_directory = join(base_directory, 'import')
        self.import_directory = import_directory

        if import_marker_path is None:
            import_marker_path = join(import_directory, '__IMPORT_MARKER__')
        self.import_marker_path = import_marker_path

        if header_path is None:
            header_path = join(import_directory, 'header.csv')
        self.header_path = header_path

        if entities_path is None:
            entities_path = join(import_directory, 'entities.csv')
        self.entities_path = entities_path

        if dataset_path is None:
            dataset_path = join(import_directory, 'dataset.csv')
        self.dataset_path = dataset_path


_config = Config()


def get_config() -> Config:
    return _config


def set_config(config: Config):
    global _config
    _config = config
