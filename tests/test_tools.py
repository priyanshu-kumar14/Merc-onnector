import pytest
from zoho_inventory_mcp.tools import _page

@pytest.mark.parametrize("page,per_page", [(0, 10), (1, 0), (1, 101), (-1, 1)])
def test_invalid_pagination_rejected(settings, page, per_page):
    with pytest.raises(ValueError):
        _page(page, per_page, settings)

def test_valid_pagination(settings):
    assert _page(2, 50, settings) == (2, 50)
