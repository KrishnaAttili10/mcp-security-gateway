import sqlite3
import pytest
import consent


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    # Use a temporary database instead of the real consent.db
    db_path = tmp_path / "test_consent.db"

    monkeypatch.setattr(consent, "DB_PATH", db_path)

    consent.init_db()

    return db_path


def test_consent_granted(test_database):
    assert consent.has_consent("Krishna", "hospital_a") is True


def test_consent_revoked(test_database):
    consent.revoke_consent("Krishna", "hospital_a")

    assert consent.has_consent("Krishna", "hospital_a") is False


def test_consent_restored(test_database):
    consent.revoke_consent("Krishna", "hospital_a")

    assert consent.has_consent("Krishna", "hospital_a") is False

    consent.grant_consent("Krishna", "hospital_a")

    assert consent.has_consent("Krishna", "hospital_a") is True


def test_unauthorized_hospital(test_database):
    assert consent.has_consent("Krishna", "hospital_b") is False