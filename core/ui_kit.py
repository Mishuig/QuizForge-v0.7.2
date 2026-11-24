"""Спільні будівельні блоки адаптивної верстки (grid + stretch)."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.ui_theme import logo_pixmap


def brand_row(logo: str = "logo-client.svg", size: int = 40, centered: bool = True) -> QWidget:
    """Логотип + назва QuizForge."""
    w = QWidget()
    row = QHBoxLayout(w)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(12)
    if centered:
        row.addStretch(1)
    icon = QLabel()
    pm = logo_pixmap(logo, size)
    if not pm.isNull():
        icon.setPixmap(pm)
    name = QLabel("QuizForge")
    name.setObjectName("logoLabel")
    row.addWidget(icon)
    row.addWidget(name)
    row.addStretch(1)
    return w


def centered_card(screen: QWidget, max_width: int = 520, min_width: int = 300):
    """
    Центрована картка, що стискається разом із вікном.
    Сітка 3×3: бічні/верхні комірки розтягуються, центральна колонка має пріоритет до max_width.
    Повертає (card, card_layout).
    """
    grid = QGridLayout(screen)
    grid.setContentsMargins(24, 24, 24, 24)
    grid.setRowStretch(0, 1)
    grid.setRowStretch(2, 1)
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 1000)
    grid.setColumnStretch(2, 1)
    card = QFrame()
    card.setObjectName("card")
    card.setMinimumWidth(min_width)
    card.setMaximumWidth(max_width)
    card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    lay = QVBoxLayout(card)
    lay.setContentsMargins(36, 32, 36, 32)
    lay.setSpacing(16)
    grid.addWidget(card, 1, 1)
    return card, lay


def field(label: str, widget: QWidget) -> QWidget:
    """Підпис над полем (адаптивніше за QFormLayout)."""
    box = QWidget()
    lay = QVBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)
    cap = QLabel(label)
    cap.setObjectName("fieldLabel")
    lay.addWidget(cap)
    lay.addWidget(widget)
    return box


def divider() -> QFrame:
    line = QFrame()
    line.setObjectName("divider")
    line.setFrameShape(QFrame.Shape.HLine)
    return line


def align_center(label: QLabel) -> QLabel:
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setWordWrap(True)
    return label
