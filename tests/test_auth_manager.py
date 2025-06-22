from security.auth_manager import authenticate_user


def test_authenticate_admin_success():
    success, role = authenticate_user("admin", "admin123")
    assert success and role == "admin"


def test_authenticate_fail():
    success, role = authenticate_user("unknown", "bad")
    assert not success and role is None
