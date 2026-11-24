"""
Спільна тема QuizForge (адмін-панель і клієнт).

Один QSS-шаблон `client/ui/styles.qss` із плейсхолдерами @ACCENT@ тощо.
Акцентний колір береться з config.json -> organization.accent_color.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QFontDatabase, QPixmap
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QWidget

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
QSS_PATH = ROOT / "client" / "ui" / "styles.qss"
DEFAULT_ACCENT = "#3b82f6"

# Кольори статусів (текст на темному тлі, контраст ≥ 4.5:1)
STATUS_COLORS = {
    "ok": "#6EE7B7",
    "info": "#93C5FD",
    "warn": "#FDE68A",
    "bad": "#FCA5A5",
    "muted": "#B4C0D4",
}


def _shade(hex_color: str, factor: float) -> str:
    c = QColor(hex_color)
    if not c.isValid():
        c = QColor(DEFAULT_ACCENT)
    if factor >= 1:
        c = c.lighter(int(factor * 100))
    else:
        c = c.darker(int(100 / max(factor, 0.01)))
    return c.name()


def _load_fonts(app: QApplication) -> None:
    """Підключає Inter з папки fonts/, якщо файли там є; інакше — системний шрифт."""
    family = None
    for path in sorted((ROOT / "fonts").glob("Inter*.[ot]tf")):
        fid = QFontDatabase.addApplicationFont(str(path))
        if fid != -1 and not family:
            fams = QFontDatabase.applicationFontFamilies(fid)
            family = fams[0] if fams else None
    if family:
        app.setFont(QFont(family, 10))


def _write_icons(accent: str) -> str:
    """Генерує SVG-іконки (радіо, чекбокс, стрілки) з акцентним кольором у тимчасову папку."""
    acc = QColor(accent).name()
    muted, hover, bg = "#5B6B85", acc, "#0F1520"
    icons = {
        "radio-off": f'<circle cx="10" cy="10" r="8" fill="{bg}" stroke="{muted}" stroke-width="2"/>',
        "radio-off-hover": f'<circle cx="10" cy="10" r="8" fill="{bg}" stroke="{hover}" stroke-width="2"/>',
        "radio-on": f'<circle cx="10" cy="10" r="8" fill="{bg}" stroke="{acc}" stroke-width="2"/><circle cx="10" cy="10" r="4.5" fill="{acc}"/>',
        "check-off": f'<rect x="1" y="1" width="18" height="18" rx="5" fill="{bg}" stroke="{muted}" stroke-width="2"/>',
        "check-off-hover": f'<rect x="1" y="1" width="18" height="18" rx="5" fill="{bg}" stroke="{hover}" stroke-width="2"/>',
        "check-on": f'<rect x="1" y="1" width="18" height="18" rx="5" fill="{acc}" stroke="{acc}" stroke-width="2"/>'
                    '<path d="M5.5 10.5l3 3 6-6.5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    }
    folder = Path(tempfile.gettempdir()) / f"quizforge-ui-{acc.lstrip('#')}"
    try:
        folder.mkdir(parents=True, exist_ok=True)
        for name, body in icons.items():
            (folder / f"{name}.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="20" height="20">{body}</svg>',
                encoding="utf-8",
            )
        for name, d in (("chevron-down", "M2 4l4 4 4-4"), ("chevron-up", "M2 8l4-4 4 4")):
            (folder / f"{name}.svg").write_text(
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 12 12" width="12" height="12">'
                f'<path d="{d}" fill="none" stroke="#9AA8BD" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
                encoding="utf-8",
            )
    except OSError:
        logger.exception("Не вдалося створити іконки теми")
    return folder.as_posix()


def apply_theme(app: QApplication, accent: str | None = None) -> None:
    """Застосовує тему до всього застосунку."""
    accent = accent or DEFAULT_ACCENT
    if not QColor(accent).isValid():
        accent = DEFAULT_ACCENT
    _load_fonts(app)
    if not QSS_PATH.is_file():
        logger.warning("Файл стилів не знайдено: %s", QSS_PATH)
        return
    qss = QSS_PATH.read_text(encoding="utf-8")
    tokens = {
        "@ACCENT@": accent,
        "@ACCENT_HOVER@": _shade(accent, 1.12),
        "@ACCENT_PRESSED@": _shade(accent, 0.85),
        "@ICONS@": _write_icons(accent),
    }
    soft = QColor(accent)
    soft.setAlpha(0x2E)
    tokens["@ACCENT_SOFT@"] = f"rgba({soft.red()},{soft.green()},{soft.blue()},{soft.alpha()})"
    for key, val in tokens.items():
        qss = qss.replace(key, val)
    app.setStyleSheet(qss)


def logo_pixmap(name: str, size: int) -> QPixmap:
    """Логотип з assets/ (шлях не залежить від поточної директорії)."""
    pm = QPixmap(str(ASSETS / name))
    if pm.isNull():
        return pm
    return pm.scaled(
        size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    )


def repolish(widget: QWidget) -> None:
    """Перезастосовує QSS після зміни динамічної властивості."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()


def status_item(text: str, kind: str = "muted") -> QTableWidgetItem:
    """Комірка таблиці зі статусом: «● Текст» кольором статусу."""
    item = QTableWidgetItem(f"● {text}")
    item.setForeground(QBrush(QColor(STATUS_COLORS.get(kind, STATUS_COLORS["muted"]))))
    font = item.font()
    font.setWeight(QFont.Weight.DemiBold)
    item.setFont(font)
    return item


def colored_item(text: str, kind: str, bold: bool = True) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setForeground(QBrush(QColor(STATUS_COLORS.get(kind, STATUS_COLORS["muted"]))))
    if bold:
        font = item.font()
        font.setWeight(QFont.Weight.DemiBold)
        item.setFont(font)
    return item
