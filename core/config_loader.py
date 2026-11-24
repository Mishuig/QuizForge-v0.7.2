"""
Завантаження та валідація конфігурації SecureTest.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Шлях до config.json відносно кореня проєкту (або поруч із .exe після збірки)
DEFAULT_CONFIG_NAME = "config.json"


class ConfigError(Exception):
    """Помилка завантаження або валідації конфігурації."""


def _find_config_path() -> Path:
    """Знаходить config.json: поруч із виконуваним файлом або в корені проєкту."""
    import sys

    # Після PyInstaller
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        # Під час розробки: core/ -> securetest/
        base = Path(__file__).resolve().parent.parent

    candidate = base / DEFAULT_CONFIG_NAME
    if candidate.is_file():
        return candidate

    # Спроба в поточній робочій директорії
    cwd_candidate = Path.cwd() / DEFAULT_CONFIG_NAME
    if cwd_candidate.is_file():
        return cwd_candidate

    raise ConfigError(
        f"Файл конфігурації '{DEFAULT_CONFIG_NAME}' не знайдено. "
        f"Очікуваний шлях: {candidate}"
    )


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """
    Завантажує config.json і повертає словник.

    Args:
        config_path: явний шлях до файлу (опційно).

    Returns:
        Словник конфігурації.

    Raises:
        ConfigError: якщо файл відсутній або містить невалідний JSON.
    """
    path = Path(config_path) if config_path else _find_config_path()

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise ConfigError(f"Файл конфігурації не знайдено: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Невалідний JSON у {path}: {exc}") from exc

    _validate_config(data)
    logger.info("Конфігурацію завантажено з %s", path)
    return data


def _validate_config(data: dict[str, Any]) -> None:
    """Базова перевірка та заповнення дефолтів для відсутніх ключів."""
    defaults = {
        "db_path": "securetest.db",
        "otp_ttl_minutes": 10,
        "otp_max_failed": 10,
        "otp_resend_cooldown_sec": 60,
        "otp_max_requests_per_hour": 5,
        "partial_credit": False,
        "show_score_to_student": False,
        "screenshot_interval_sec": 45,
        "screenshot_quality": 70,
        "process_blacklist": [
            "AnyDesk.exe", "TeamViewer.exe", "TeamViewer_Service.exe",
            "tv_w32.exe", "tv_x64.exe", "RustDesk.exe",
            "chrome_remote_desktop_host.exe",
        ],
        "allowed_domains": [],
        "report_recipients": [],
        "send_copy_to_student": False,
    }
    for key, default in defaults.items():
        data.setdefault(key, default)

    if "organization" not in data or not isinstance(data["organization"], dict):
        data["organization"] = {}
    org = data["organization"]
    org.setdefault("name", "QuizForge")
    org.setdefault("accent_color", "#3b82f6")
    org.setdefault("logo", "assets/logo.png")

    if "smtp" not in data or not isinstance(data["smtp"], dict):
        data["smtp"] = {}
    smtp = data["smtp"]
    smtp.setdefault("host", "smtp.example.com")
    smtp.setdefault("port", 587)
    smtp.setdefault("security", "starttls")
    smtp.setdefault("username", "")
    smtp.setdefault("password", "")
    smtp.setdefault("from_address", "noreply@example.com")
    smtp.setdefault("from_name", "QuizForge")

    # Мінімальна перевірка після дефолтів
    if not org.get("name"):
        raise ConfigError("organization.name обов'язковий")


def get_db_path(config: dict[str, Any] | None = None) -> Path:
    """Повертає абсолютний шлях до файлу БД."""
    if config is None:
        config = load_config()
    db_path = Path(config["db_path"])
    if not db_path.is_absolute():
        # Відносно директорії config.json
        config_dir = _find_config_path().parent
        db_path = config_dir / db_path
    return db_path.resolve()


def save_config(data: dict[str, Any], config_path: str | Path | None = None) -> None:
    """Зберігає конфігурацію назад у файл (наприклад, після встановлення пароля адміна)."""
    path = Path(config_path) if config_path else _find_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("Конфігурацію збережено в %s", path)
