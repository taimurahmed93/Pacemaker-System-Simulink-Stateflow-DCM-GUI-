import pytest
import json
from gui.login_screen import register_user, validate_login

# -----------------------------
# Fixtures
# -----------------------------

# Empty users JSON file
@pytest.fixture
def empty_users_file(tmp_path):
    data_path = tmp_path / "users.json"
    with open(data_path, "w") as f:
        json.dump({"users": []}, f)
    return data_path

# Sample users JSON file
@pytest.fixture
def sample_users_file(tmp_path):
    data_path = tmp_path / "users.json"
    users = [
        {"username": "alice", "password": "1234"},
        {"username": "bob", "password": "abcd"},
    ]
    with open(data_path, "w") as f:
        json.dump({"users": users}, f)
    return data_path

# Helper to read users from JSON
def read_users(data_path):
    with open(data_path, "r") as f:
        return json.load(f)["users"]

# -----------------------------
# Tests for register_user
# -----------------------------
def test_register_user_success(empty_users_file):
    data_path = empty_users_file
    users = read_users(data_path)
    success, message = register_user(users, "charlie", "pass123", data_path)
    
    assert success == True
    assert message == "User registered successfully."
    
    users_after = read_users(data_path)
    assert len(users_after) == 1
    assert users_after[0]["username"] == "charlie"

def test_register_user_duplicate(sample_users_file):
    data_path = sample_users_file
    users = read_users(data_path)
    success, message = register_user(users, "alice", "newpass", data_path)
    
    assert success == False
    assert message == "Sorry this username already exists."
    
    users_after = read_users(data_path)
    assert len(users_after) == 2  # no new user added

def test_register_user_max_limit(tmp_path):
    data_path = tmp_path / "users.json"
    users = [{"username": f"user{i}", "password": "pass"} for i in range(10)]
    with open(data_path, "w") as f:
        json.dump({"users": users}, f)
    
    success, message = register_user(users, "newuser", "pass", data_path)
    assert success == False
    assert message == "Maximum of 10 users allowed."

# -----------------------------
# Tests for validate_login
# -----------------------------
def test_validate_login_success(sample_users_file):
    data_path = sample_users_file
    users = read_users(data_path)
    
    assert validate_login(users, "alice", "1234") == True
    assert validate_login(users, "bob", "abcd") == True

def test_validate_login_failure(sample_users_file):
    data_path = sample_users_file
    users = read_users(data_path)
    
    assert validate_login(users, "alice", "wrong") == False
    assert validate_login(users, "nonexistent", "123") == False
