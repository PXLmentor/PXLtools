# Tool Name: PXLmentor MU Bridge - Export Report Dialog (Maya side)
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: PySide6 modal that displays warnings, dropped params, and
#              validation errors collected during a Maya export pass. Mirrors
#              the PXLmentor design tokens used by Arnold PBR Material Creator.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

from pxl_mu_bridge_schema import ExportReport

logger = logging.getLogger(__name__)


_STATUS_OK_STYLE = (
    "background:#2a402a; color:#7acc7a; border:1px solid #3a5a3a; "
    "border-radius:2px; padding:6px 10px; font-size:11px;"
)
_STATUS_ERR_STYLE = (
    "background:#4a3030; color:#e07070; border:1px solid #6a3a3a; "
    "border-radius:2px; padding:6px 10px; font-size:11px;"
)
_HEADER_STYLE = (
    "color:#E8820C; font-family:'Courier New', monospace; "
    "font-size:14px; font-weight:bold; letter-spacing:1.2px;"
)
_TREE_STYLE = (
    "QTreeWidget { background:#3a3a3a; color:#dcdcdc; border:1px solid #2b2b2b; }"
    "QTreeWidget::item { padding:4px; }"
    "QHeaderView::section { background:#393939; color:#aaaaaa; "
    "padding:4px 8px; border:none; font-weight:bold; }"
)


class ExportReportDialog(QtWidgets.QDialog):
    """Modal dialog showing the Maya export report."""

    def __init__(
        self,
        report: ExportReport,
        manifest_path: Path,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._manifest_path = Path(manifest_path)
        self.setWindowTitle("MU Bridge - Export Report")
        self.setMinimumSize(640, 420)
        self.setStyleSheet("QDialog { background:#464646; color:#dcdcdc; }")

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        header = QtWidgets.QLabel("Export complete - {}".format(self._manifest_path.name))
        header.setStyleSheet(_HEADER_STYLE)
        root.addWidget(header)

        status = QtWidgets.QLabel(self._status_text(report))
        status.setStyleSheet(
            _STATUS_ERR_STYLE if report.validation_errors else _STATUS_OK_STYLE
        )
        root.addWidget(status)

        self._tree = QtWidgets.QTreeWidget()
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(["Severity", "Message"])
        self._tree.setRootIsDecorated(False)
        self._tree.setStyleSheet(_TREE_STYLE)
        self._populate(report)
        root.addWidget(self._tree, 1)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch(1)
        btn_open = QtWidgets.QPushButton("Open in Explorer")
        btn_open.clicked.connect(self._open_in_explorer)
        btn_close = QtWidgets.QPushButton("Close")
        btn_close.setDefault(True)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_open)
        btn_row.addWidget(btn_close)
        root.addLayout(btn_row)

    def _status_text(self, report: ExportReport) -> str:
        if report.validation_errors:
            return "{} validation error(s) - manifest may be incomplete".format(
                len(report.validation_errors)
            )
        return "{} warning(s), {} dropped param(s)".format(
            len(report.warnings), len(report.dropped_params),
        )

    def _populate(self, report: ExportReport) -> None:
        for msg in report.validation_errors:
            item = QtWidgets.QTreeWidgetItem(["ERROR", msg])
            item.setForeground(0, QtGui.QBrush(QtGui.QColor("#e07070")))
            self._tree.addTopLevelItem(item)
        for msg in report.warnings:
            item = QtWidgets.QTreeWidgetItem(["WARN", msg])
            item.setForeground(0, QtGui.QBrush(QtGui.QColor("#e8b85c")))
            self._tree.addTopLevelItem(item)
        for attr in report.dropped_params:
            item = QtWidgets.QTreeWidgetItem(["DROP", "Dropped attr: {}".format(attr)])
            item.setForeground(0, QtGui.QBrush(QtGui.QColor("#9090c0")))
            self._tree.addTopLevelItem(item)
        if self._tree.topLevelItemCount() == 0:
            self._tree.addTopLevelItem(QtWidgets.QTreeWidgetItem(
                ["OK", "Clean export - no warnings or dropped params."]
            ))
        for col in range(2):
            self._tree.resizeColumnToContents(col)

    def _open_in_explorer(self) -> None:
        win_path = str(self._manifest_path).replace("/", "\\")
        try:
            subprocess.Popen(["explorer", "/select,", win_path])
        except Exception:
            logger.exception("Failed to open explorer at %s", self._manifest_path)
