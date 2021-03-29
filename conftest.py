# Adds tests marked with download won't run without pytest --download
def pytest_addoption(parser):
    parser.addoption('--download', action='store_true', dest="download",
                     default=False, help="enable download-decorated tests")


def pytest_configure(config):
    if not config.option.download:
        setattr(config.option, 'markexpr', 'not download')