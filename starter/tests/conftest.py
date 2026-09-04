import pytest

import app as app_module


@pytest.fixture
def app():
    app_module.app.config.update(TESTING=True)
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    return app_module.app


@pytest.fixture
def client(app):
    return app.test_client()
