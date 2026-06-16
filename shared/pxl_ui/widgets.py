"""
pxl_ui.widgets - the reusable building blocks every PXLtools tool is made of.

Zoo-inspired: a tool is a vertical stack of icon-headed collapsible sections,
so the workflow reads visually top-to-bottom. All styling comes from theme.py;
all icons from icons.py. Pure compat-shim Qt - identical in Maya / Nuke.
"""

import os

from .compat import QtCore, QtGui, QtWidgets, Signal
from . import theme
from . import icons

Qt = QtCore.Qt


# --------------------------------------------------------------------------- #
def _font(size, weight=QtGui.QFont.Normal):
    f = QtGui.QFont(theme.m("font_family"), size)
    f.setWeight(weight)
    return f


# --------------------------------------------------------------------------- #
#  LABELS                                                                      #
# --------------------------------------------------------------------------- #
class FieldLabel(QtWidgets.QLabel):
    """Small uppercase muted caption above a control group."""
    def __init__(self, text, parent=None):
        super(FieldLabel, self).__init__(text.upper(), parent)
        self.setFont(_font(theme.m("fs_small")))
        self.setStyleSheet(
            "color: %s; letter-spacing: 1px;" % theme.c("text_dim"))


class Hint(QtWidgets.QLabel):
    """Muted helper paragraph."""
    def __init__(self, text, parent=None):
        super(Hint, self).__init__(text, parent)
        self.setWordWrap(True)
        self.setFont(_font(theme.m("fs_small")))
        self.setStyleSheet("color: %s;" % theme.c("text_muted"))


class Divider(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Divider, self).__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet("background: %s;" % theme.c("hairline"))


# --------------------------------------------------------------------------- #
#  BUTTONS                                                                     #
# --------------------------------------------------------------------------- #
class _IconMixin(object):
    def set_icon(self, name, size=None, color=None):
        size = size or theme.m("icon_btn")
        color = color or theme.c("text")
        self.setIcon(icons.icon(name, size, color))
        self.setIconSize(QtCore.QSize(size, size))


class PrimaryButton(QtWidgets.QPushButton, _IconMixin):
    def __init__(self, text, icon_name=None, parent=None):
        super(PrimaryButton, self).__init__(text, parent)
        self.setObjectName("PxlPrimary")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(32)
        if icon_name:
            self.set_icon(icon_name, color=theme.c("on_accent"))


class GhostButton(QtWidgets.QPushButton, _IconMixin):
    def __init__(self, text, icon_name=None, parent=None):
        super(GhostButton, self).__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(28)
        if icon_name:
            self.set_icon(icon_name)


class DangerButton(QtWidgets.QPushButton, _IconMixin):
    def __init__(self, text, icon_name=None, parent=None):
        super(DangerButton, self).__init__(text, parent)
        self.setObjectName("PxlDanger")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(28)
        if icon_name:
            self.set_icon(icon_name, color=theme.c("error"))


class IconButton(QtWidgets.QPushButton, _IconMixin):
    def __init__(self, icon_name, tooltip="", size=28, parent=None):
        super(IconButton, self).__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(size, size)
        self.set_icon(icon_name, size=int(size * 0.55))
        if tooltip:
            self.setToolTip(tooltip)


class SegmentedRow(QtWidgets.QWidget):
    """Mutually-exclusive toggle buttons (e.g. SHADER BALL / YOUR MODEL)."""
    changed = Signal(int)

    def __init__(self, options, parent=None):
        super(SegmentedRow, self).__init__(parent)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(theme.m("gap"))
        self._group = QtWidgets.QButtonGroup(self)
        self._group.setExclusive(True)
        for i, opt in enumerate(options):
            b = QtWidgets.QPushButton(opt)
            b.setObjectName("PxlSeg")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumHeight(28)
            if i == 0:
                b.setChecked(True)
            self._group.addButton(b, i)
            lay.addWidget(b, 1)
        self._group.idClicked.connect(self.changed.emit) \
            if hasattr(self._group, "idClicked") else \
            self._group.buttonClicked.connect(
                lambda b: self.changed.emit(self._group.id(b)))


# --------------------------------------------------------------------------- #
#  ROWS (label + control)                                                      #
# --------------------------------------------------------------------------- #
class PathRow(QtWidgets.QWidget):
    """Caption + line edit + Browse button - the folder picker pattern."""
    def __init__(self, caption, placeholder="", parent=None):
        super(PathRow, self).__init__(parent)
        v = QtWidgets.QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(FieldLabel(caption))
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(theme.m("gap"))
        self.field = QtWidgets.QLineEdit()
        self.field.setPlaceholderText(placeholder)
        self.browse = GhostButton("Browse", "folder")
        row.addWidget(self.field, 1)
        row.addWidget(self.browse)
        v.addLayout(row)


class SliderRow(QtWidgets.QWidget):
    """Caption + slider + numeric box, kept in sync."""
    def __init__(self, caption, lo=0, hi=100, val=0, decimals=0,
                 suffix="", parent=None):
        super(SliderRow, self).__init__(parent)
        self._decimals = decimals
        self._scale = 10 ** decimals
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(theme.m("gap"))

        cap = QtWidgets.QLabel(caption)
        cap.setMinimumWidth(86)
        cap.setStyleSheet("color: %s;" % theme.c("text_muted"))

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setRange(int(lo * self._scale), int(hi * self._scale))
        self.slider.setValue(int(val * self._scale))

        if decimals > 0:
            self.spin = QtWidgets.QDoubleSpinBox()
            self.spin.setDecimals(decimals)
        else:
            self.spin = QtWidgets.QSpinBox()
        self.spin.setRange(lo, hi)
        self.spin.setValue(val)
        self.spin.setFixedWidth(86 if suffix else 64)
        if suffix:
            self.spin.setSuffix(suffix)

        row.addWidget(cap)
        row.addWidget(self.slider, 1)
        row.addWidget(self.spin)

        self.slider.valueChanged.connect(self._from_slider)
        self.spin.valueChanged.connect(self._from_spin)

    def _from_slider(self, v):
        self.spin.blockSignals(True)
        self.spin.setValue(v / self._scale if self._decimals else int(v))
        self.spin.blockSignals(False)

    def _from_spin(self, v):
        self.slider.blockSignals(True)
        self.slider.setValue(int(v * self._scale))
        self.slider.blockSignals(False)


class ComboRow(QtWidgets.QWidget):
    def __init__(self, caption, items, parent=None):
        super(ComboRow, self).__init__(parent)
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(theme.m("gap"))
        cap = QtWidgets.QLabel(caption)
        cap.setMinimumWidth(86)
        cap.setStyleSheet("color: %s;" % theme.c("text_muted"))
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(items)
        row.addWidget(cap)
        row.addWidget(self.combo, 1)


# --------------------------------------------------------------------------- #
#  STATUS PILL                                                                 #
# --------------------------------------------------------------------------- #
class StatusPill(QtWidgets.QLabel):
    def __init__(self, text="", kind="muted", parent=None):
        super(StatusPill, self).__init__(parent)
        self.set_status(text, kind)

    def set_status(self, text, kind="muted"):
        col = {
            "ok": theme.c("ok"), "warn": theme.c("warn"),
            "error": theme.c("error"), "muted": theme.c("text_dim"),
        }.get(kind, theme.c("text_dim"))
        self.setText("  " + text)
        self.setFont(_font(theme.m("fs_small")))
        self.setStyleSheet(
            "color: %s; background: %s; border: 1px solid %s;"
            "border-radius: %dpx; padding: 3px 10px;"
            % (col, theme.c("input"), theme.c("hairline"), theme.m("r_pill")))


# --------------------------------------------------------------------------- #
#  COLLAPSIBLE SECTION  (the centrepiece)                                      #
# --------------------------------------------------------------------------- #
class CollapsibleSection(QtWidgets.QWidget):
    """Icon-headed, accordion-style section.

    +--------------------------------------------------+
    | |  [icon]  TITLE                        [chevron]|   <- header (click)
    +--------------------------------------------------+
    |   ... body widgets ...                           |   <- body (toggles)
    +--------------------------------------------------+
    The 3px accent bar on the left of the header is the Zoo-style visual cue.
    """
    toggled = Signal(bool)

    def __init__(self, title, icon_name=None, collapsed=False, accent=None,
                 parent=None):
        super(CollapsibleSection, self).__init__(parent)
        self._collapsed = collapsed
        self._icon_name = icon_name
        # per-section identity colour (accent bar + icon); brand orange default
        self._accent_col = accent or theme.c("accent")

        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ---- header ----
        self.header = QtWidgets.QFrame()
        self.header.setObjectName("PxlSectionHeader")
        self.header.setCursor(Qt.PointingHandCursor)
        self.header.setFixedHeight(theme.m("section_h"))
        h = QtWidgets.QHBoxLayout(self.header)
        h.setContentsMargins(0, 0, 8, 0)
        h.setSpacing(8)

        self._accent = QtWidgets.QFrame()
        self._accent.setFixedWidth(3)
        self._accent.setStyleSheet("background: %s;" % self._accent_col)
        h.addWidget(self._accent)

        self._icon_lbl = QtWidgets.QLabel()
        self._icon_lbl.setFixedWidth(theme.m("icon"))
        # transparent bg so the global QWidget{background:#333} rule doesn't paint
        # an opaque block over the header bar (would break it into segments).
        self._icon_lbl.setStyleSheet("background: transparent;")
        if icon_name:
            self._icon_lbl.setPixmap(
                icons.pixmap(icon_name, theme.m("icon"), self._accent_col))
        h.addWidget(self._icon_lbl)

        self._title = QtWidgets.QLabel(title)
        self._title.setFont(_font(theme.m("fs_section"), QtGui.QFont.DemiBold))
        self._title.setStyleSheet("background: transparent; color: %s;" % theme.c("text"))
        h.addWidget(self._title)
        h.addStretch(1)

        self._chevron = QtWidgets.QLabel()
        self._chevron.setFixedWidth(16)
        self._chevron.setStyleSheet("background: transparent;")
        h.addWidget(self._chevron)

        outer.addWidget(self.header)

        # ---- body ----
        self.body = QtWidgets.QFrame()
        self.body.setObjectName("PxlSectionBody")
        self._body_lay = QtWidgets.QVBoxLayout(self.body)
        self._body_lay.setContentsMargins(
            theme.m("pad") + 3, theme.m("pad"),
            theme.m("pad"), theme.m("pad"))
        self._body_lay.setSpacing(theme.m("gap"))
        outer.addWidget(self.body)

        self.header.mousePressEvent = self._on_click
        self._apply_state()

    # -- public API --
    def add_widget(self, w):
        self._body_lay.addWidget(w)
        return w

    def add_layout(self, lay):
        self._body_lay.addLayout(lay)
        return lay

    def add_spacing(self, px):
        self._body_lay.addSpacing(px)

    def set_collapsed(self, state):
        self._collapsed = state
        self._apply_state()

    # -- internals --
    def _on_click(self, event):
        self._collapsed = not self._collapsed
        self._apply_state()
        self.toggled.emit(not self._collapsed)

    def _apply_state(self):
        self.body.setVisible(not self._collapsed)
        chev = "collapsed" if self._collapsed else "expanded"
        self._chevron.setPixmap(
            icons.pixmap(chev, 14, theme.c("text_dim")))
        bottom_radius = 0 if self._collapsed else 0
        # header style: rounded top always; rounded bottom only when collapsed
        br = theme.m("r_section") if self._collapsed else 0
        self.header.setStyleSheet(
            "QFrame#PxlSectionHeader {"
            "  background: %s;"
            "  border: none;"
            "  border-top-left-radius: %dpx;"
            "  border-top-right-radius: %dpx;"
            "  border-bottom-left-radius: %dpx;"
            "  border-bottom-right-radius: %dpx;"
            "}"
            "QFrame#PxlSectionHeader:hover { background: %s; }"
            % (theme.c("section_head"),
               theme.m("r_section"), theme.m("r_section"),
               br, br, theme.c("section_hover")))


# --------------------------------------------------------------------------- #
#  APP HEADER (branding bar)                                                   #
# --------------------------------------------------------------------------- #
class AppHeader(QtWidgets.QFrame):
    """Standard PXLtools tool header - exact port of the original tool header.

    96x96 tool icon on the left; centred PXLtools wordmark in the original
    262x48 slot; thin divider; tool name (11px bold) + version (9px) beneath.
    Same layout and sizes as the shipped tools - only the logo changed
    (PixelMentor -> PXLtools). Used by EVERY tool for one shared identity.
    """
    def __init__(self, tool_name, version="", icon_name="render",
                 icon_path=None, parent=None):
        super(AppHeader, self).__init__(parent)
        self.setObjectName("PxlHeader")
        self.setFixedHeight(146)
        # flat header — the same dark grey as the interface body (no two-tone,
        # no transparency, no extra dividers)
        self.setStyleSheet(
            "QFrame#PxlHeader { background: %s; }" % theme.c("window"))
        root = QtWidgets.QHBoxLayout(self)
        root.setContentsMargins(10, 5, 10, 5)
        root.setSpacing(0)
        dpr = icons._dpr()

        # ---- left: 96x96 tool icon ----
        left = QtWidgets.QLabel()
        left.setFixedSize(96, 96)
        left.setAlignment(Qt.AlignCenter)
        if icon_path and os.path.isfile(icon_path):
            src = QtGui.QPixmap(icon_path)
            pm = src.scaled(int(round(96 * dpr)), int(round(96 * dpr)),
                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            left.setPixmap(pm)
        else:
            left.setPixmap(icons.pixmap(icon_name, 72, theme.c("accent")))
        root.addWidget(left)

        # ---- centre: logo + name + version ----
        cv = QtWidgets.QVBoxLayout()
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(2)
        cv.setAlignment(Qt.AlignVCenter)

        # logo scaled to a fixed WIDTH (not a fixed box) so it never overflows
        # its column — it centres cleanly and the name sits directly under it.
        logo_lbl = QtWidgets.QLabel()
        logo_lbl.setAlignment(Qt.AlignCenter)
        lp = os.path.join(icons.ICON_DIR, "PXLtools_logo.png")
        if os.path.isfile(lp):
            src = QtGui.QPixmap(lp)
            pm = src.scaledToWidth(int(round(400 * dpr)), Qt.SmoothTransformation)
            pm.setDevicePixelRatio(dpr)
            logo_lbl.setPixmap(pm)
        else:
            logo_lbl.setText("PXLtools")
            logo_lbl.setStyleSheet(
                "color:#D7005A; font-weight:bold; font-size:26px;")

        lhbox = QtWidgets.QHBoxLayout()
        lhbox.setContentsMargins(0, 0, 0, 0)
        lhbox.addStretch()
        lhbox.addWidget(logo_lbl)
        lhbox.addStretch()

        div_lbl = QtWidgets.QFrame()
        div_lbl.setFixedSize(320, 1)
        div_lbl.setStyleSheet("background: %s;" % theme.c("hairline"))

        # tool name + version on ONE centred line, version in orange
        nrow = QtWidgets.QHBoxLayout()
        nrow.setContentsMargins(0, 0, 0, 0)
        nrow.setSpacing(8)
        nrow.addStretch(1)
        name_lbl = QtWidgets.QLabel(tool_name)
        name_lbl.setStyleSheet(
            "color:%s; font-weight:bold; font-size:12px;" % theme.c("text"))
        nrow.addWidget(name_lbl)
        if version:
            ver_lbl = QtWidgets.QLabel(version)
            ver_lbl.setStyleSheet(
                "color:%s; font-weight:bold; font-size:12px;"
                % theme.c("accent"))
            nrow.addWidget(ver_lbl)
        nrow.addStretch(1)

        cv.addLayout(lhbox)
        cv.addWidget(div_lbl, 0, Qt.AlignCenter)
        cv.addLayout(nrow)
        # logo + name centre within the space BETWEEN the tool icon and the
        # right edge of the tool (not the full viewport). No right spacer.
        root.addLayout(cv, 1)
