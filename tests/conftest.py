"""Scoped inputs for legacy HTTP fixtures; historical test bytes stay frozen."""

import sys

import pytest

from tests.publish_workflow_fixtures import install_publish_fixture_isolation

from tests.admin_http_fixtures import (
    institution_public_inputs,
    isolated_metadata_server,
    mapping_registration_inputs,
)


@pytest.fixture(autouse=True)
def isolated_admin_http_inputs(request, monkeypatch):
    module = request.module.__name__.rsplit(".", 1)[-1]
    if module == "test_admin_publish_workflow_reliability":
        install_publish_fixture_isolation(request.module, monkeypatch)
    if module in {
        "test_paper_metadata_editing",
        "test_publication_venue_audit",
        "test_workshop_venue_audit",
        "test_admin_http_fixture_isolation",
    }:
        from tests import test_paper_metadata_editing as metadata_tests

        # Pytest may collect the top-level module while other tests import its
        # namespace-package name. Preserve and wrap each actual factory once.
        modules = (metadata_tests, request.module, sys.modules.get("test_paper_metadata_editing"))
        classes = {
            candidate.PaperMetadataEditingTests for candidate in modules
            if candidate is not None and hasattr(candidate, "PaperMetadataEditingTests")
        }
        for cls in classes:
            monkeypatch.setattr(
                cls, "metadata_server", isolated_metadata_server(cls.metadata_server),
            )
    if (
        module == "test_mapping_institution_registration"
        and request.node.name == "test_create_endpoint_reports_provisional_registration"
    ):
        with mapping_registration_inputs(request.getfixturevalue("tmp_path"), request.module):
            yield
    elif (
        module == "test_institution_cleanup_queue"
        and request.node.name == "test_visible_open_confirmed_change_resolves_through_admin_http"
    ):
        with institution_public_inputs(request.getfixturevalue("tmp_path")):
            yield
    else:
        yield
