"""
pxl_ui.theme - single source of truth for the PXLtools UI look.

Every colour, radius, spacing value and the global stylesheet live here. To
retune the brand ("my colours eventually") you only edit COLORS / METRICS and
every tool re-themes. The palette is Maya-native dark grey with the PXLtools
orange accent - clean and custom, but at home docked next to Maya / Nuke panels.
"""

# --------------------------------------------------------------------------- #
#  COLOUR TOKENS                                                               #
# --------------------------------------------------------------------------- #
COLORS = {
    # structural greys (Maya-native, flat)
    "window":        "#333333",   # dialog background
    "header_bar":    "#262626",   # top branding bar (darkest)
    "surface":       "#3a3a3a",   # section body
    "surface_alt":   "#404040",   # nested panels
    "section_head":  "#454545",   # collapsible header rest
    "section_hover": "#4f4f4f",   # collapsible header hover
    "input":         "#2c2c2c",   # line edits / combos / spinboxes
    "input_hover":   "#323232",
    "hairline":      "#262626",   # dividers / borders
    "track":         "#2a2a2a",   # slider groove

    # accent (PXLtools orange)
    "accent":        "#E8820C",
    "accent_hover":  "#FF9A2E",
    "accent_press":  "#C96E08",
    "on_accent":     "#241606",   # text/icon on an orange fill

    # text
    "text":          "#E6E6E6",
    "text_muted":    "#A8A8A8",
    "text_dim":      "#7A7A7A",

    # status
    "ok":            "#5BBF6A",
    "warn":          "#E8B84B",
    "error":         "#E4604A",

    # button (neutral / ghost)
    "btn":           "#4a4a4a",
    "btn_hover":     "#555555",
    "btn_press":     "#414141",
}

# --------------------------------------------------------------------------- #
#  SECTION ACCENT COLOURS                                                      #
#  Per-section identity colour (header bar + icon), Zoo-style, so each stage of #
#  the workflow is visually distinct. All tuned to the same value/saturation   #
#  so they read as one family on the dark grey. Action buttons stay brand      #
#  orange; only the section accents vary.                                      #
# --------------------------------------------------------------------------- #
SECTION_COLORS = {
    "info":       "#46C2D6",   # cyan      - instructions
    "folder":     "#E8820C",   # orange    - folder setup (brand)
    "scene":      "#4F9DE0",   # blue      - scene & frames
    "model":      "#9B7EDE",   # violet    - model
    "lighting":   "#F2C14E",   # amber     - lighting & visibility
    "utilities":  "#34B3A0",   # teal      - utilities
    "hdri":       "#E8694A",   # coral     - hdri environment
    "layers":     "#5FBF6A",   # green     - render layers
    "render":     "#E070A8",   # pink      - render turntable
    "camera":     "#C9A24A",   # gold      - camera (future)
}


def section_color(key):
    """Accent colour for a section by name; falls back to the brand orange."""
    return SECTION_COLORS.get(key, COLORS["accent"])

# --------------------------------------------------------------------------- #
#  METRICS                                                                     #
# --------------------------------------------------------------------------- #
METRICS = {
    "font_family":   "Segoe UI",
    "fs_header":     17,   # tool name in header bar
    "fs_section":    12,   # collapsible header title
    "fs_body":       12,
    "fs_small":      11,
    "fs_tiny":       10,

    "r_section":     6,
    "r_button":      5,
    "r_input":       4,
    "r_pill":        11,

    "pad":           8,
    "gap":           6,
    "icon":          18,   # section-header icon px
    "icon_btn":      16,   # inline icon px

    "toolset_w":     440,  # comfortable tool width (roomy, not cramped)
    "header_h":      52,
    "section_h":     30,   # collapsible header height
}


def c(key):
    return COLORS[key]


def m(key):
    return METRICS[key]


# --------------------------------------------------------------------------- #
#  GLOBAL STYLESHEET                                                           #
# --------------------------------------------------------------------------- #
def build_qss():
    """Return the application stylesheet built from the tokens above."""
    return """
* {{
    font-family: "{font}";
    font-size: {fs_body}px;
    color: {text};
    outline: none;
}}
QWidget#PxlRoot {{ background: {window}; }}
QScrollArea {{ border: 0; background: {window}; }}
QScrollArea > QWidget > QWidget {{ background: {window}; }}

/* ---- scrollbar ---- */
QScrollBar:vertical {{ background: {window}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{
    background: {btn}; border-radius: 5px; min-height: 28px;
}}
QScrollBar::handle:vertical:hover {{ background: {btn_hover}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* ---- section body frame ---- */
QFrame#PxlSectionBody {{
    background: {surface};
    border: none;
    border-bottom-left-radius: {r_section}px;
    border-bottom-right-radius: {r_section}px;
}}

/* ---- generic / ghost button ---- */
QPushButton {{
    background: {btn};
    border: 1px solid {hairline};
    border-radius: {r_button}px;
    padding: 6px 12px;
    color: {text};
}}
QPushButton:hover {{ background: {btn_hover}; }}
QPushButton:pressed {{ background: {btn_press}; }}
QPushButton:disabled {{ color: {text_dim}; background: {surface_alt}; }}

/* ---- primary (accent) button ---- */
QPushButton#PxlPrimary {{
    background: {accent};
    border: 1px solid {accent_press};
    color: {on_accent};
    font-weight: 600;
    padding: 8px 14px;
}}
QPushButton#PxlPrimary:hover {{ background: {accent_hover}; }}
QPushButton#PxlPrimary:pressed {{ background: {accent_press}; }}
QPushButton#PxlPrimary:disabled {{
    background: {surface_alt}; color: {text_dim}; border-color: {hairline};
}}

/* ---- danger button ---- */
QPushButton#PxlDanger {{
    background: {btn}; border: 1px solid {error}; color: {error};
}}
QPushButton#PxlDanger:hover {{ background: #463434; }}

/* ---- segmented toggle ---- */
QPushButton#PxlSeg {{
    background: {input}; border: 1px solid {hairline};
    border-radius: {r_button}px; padding: 6px 10px; color: {text_muted};
}}
QPushButton#PxlSeg:hover {{ background: {input_hover}; color: {text}; }}
QPushButton#PxlSeg:checked {{
    background: {accent}; border-color: {accent_press};
    color: {on_accent}; font-weight: 600;
}}

/* ---- inputs ---- */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: {input};
    border: 1px solid {hairline};
    border-radius: {r_input}px;
    padding: 5px 8px;
    color: {text};
    selection-background-color: {accent};
    selection-color: {on_accent};
}}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
    background: {input_hover};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {accent};
}}
QComboBox::drop-down {{ border: 0; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {surface_alt}; border: 1px solid {hairline};
    selection-background-color: {accent}; selection-color: {on_accent};
    outline: none;
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 14px; border: 0; }}

/* ---- checkbox ---- */
QCheckBox {{ color: {text}; spacing: 7px; }}
QCheckBox::indicator {{
    width: 15px; height: 15px; border-radius: 3px;
    border: 1px solid {text_dim}; background: {input};
}}
QCheckBox::indicator:hover {{ border-color: {accent}; }}
QCheckBox::indicator:checked {{
    background: {accent}; border-color: {accent_press};
    image: url(__CHECK__);
}}

/* ---- slider: fully transparent track, orange fill line, white dot ---- */
QSlider::groove:horizontal {{ height: 4px; background: transparent; border: none; }}
QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; }}
QSlider::add-page:horizontal {{ background: #0a0a0a; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: #ffffff; width: 14px; height: 14px;
    margin: -5px 0; border-radius: 7px; border: none;
}}
QSlider::handle:horizontal:hover {{ background: #ffffff; }}

/* ---- tabs ---- */
QTabWidget::pane {{ border: 0; top: -1px; }}
QTabBar::tab {{
    background: {header_bar}; color: {text_muted};
    padding: 8px 22px; border: 0;
    border-top-left-radius: 4px; border-top-right-radius: 4px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {window}; color: {text};
    border-bottom: 2px solid {accent};
}}
QTabBar::tab:hover:!selected {{ color: {text}; }}

/* ---- tooltip ---- */
QToolTip {{
    background: {header_bar}; color: {text};
    border: 1px solid {accent}; padding: 4px 7px;
}}
""".format(
        font=METRICS["font_family"],
        fs_body=METRICS["fs_body"],
        r_section=METRICS["r_section"],
        r_button=METRICS["r_button"],
        r_input=METRICS["r_input"],
        **COLORS
    )


def tool_qss():
    """Canonical full tool stylesheet shared VERBATIM by Maya & Nuke so
    both DCC tools render identically. Substitute __CHECK__ with a real
    tick-PNG path before applying."""
    return "\nQDialog, QWidget {\n    background: #333333; color: #E6E6E6;\n    font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px;\n}\n\n/* Tabs — folder style (two raised folder tabs) */\nQTabWidget::pane { border: 1px solid #2c2c2c; background: #333333; border-radius: 0 6px 6px 6px; top: -1px; }\nQTabBar { background: transparent; }\nQTabBar::tab {\n    background: #262626; color: #9A9A9A;\n    padding: 9px 26px; font-size: 12px; font-weight: bold; letter-spacing: 1px;\n    border: 1px solid #2c2c2c; border-bottom: none;\n    border-top-left-radius: 9px; border-top-right-radius: 9px;\n    margin-right: 4px; margin-top: 5px;\n}\nQTabBar::tab:selected {\n    background: #383838; color: #ffffff;\n    border-color: #4a4a4a; border-top: 2px solid #E8820C;\n    margin-top: 0px; padding-top: 10px;\n}\nQTabBar::tab:hover:!selected { background: #2f2f2f; color: #D8D8D8; margin-top: 3px; }\n\n/* Collapsible body + section frames */\nQFrame#collapsibleBody {\n    background: #383838; border: none;\n    border-radius: 0 0 6px 6px;\n}\nQFrame#sectionFrame {\n    background: #3a3a3a; border: none; border-radius: 6px;\n}\n\n/* Buttons */\nQPushButton {\n    background: #4a4a4a; color: #E6E6E6; border: 1px solid #262626;\n    border-radius: 5px; font-size: 12px; font-weight: bold;\n    letter-spacing: 0.6px; padding: 0 14px; min-height: 32px; min-width: 84px;\n}\nQPushButton:hover { background: #555555; color: #ffffff; }\nQPushButton:pressed { background: #414141; }\nQPushButton:disabled { background: #404040; color: #7A7A7A; border-color: #262626; }\n\nQPushButton#btnPrimary {\n    background: #E8820C; color: #241606; border: 1px solid #C96E08;\n    font-size: 13px; letter-spacing: 1px; font-weight: 700;\n}\nQPushButton#btnPrimary:hover { background: #FF9A2E; }\nQPushButton#btnPrimary:pressed { background: #C96E08; }\nQPushButton#btnPrimary:disabled { background: #404040; color: #7A7A7A; border-color: #262626; }\n\nQPushButton#btnToggleActive {\n    background: #E8820C; color: #241606; border: 1px solid #C96E08;\n    border-radius: 5px; font-weight: 700; min-height: 28px; max-height: 28px;\n}\nQPushButton#btnToggleActive:hover { background: #FF9A2E; }\nQPushButton#btnToggleInactive {\n    background: #2c2c2c; color: #A8A8A8; border: 1px solid #262626;\n    border-radius: 5px; min-height: 28px; max-height: 28px;\n}\nQPushButton#btnToggleInactive:hover { background: #323232; color: #E6E6E6; }\n\nQPushButton#btnDestruct {\n    background: #4a4a4a; color: #E4604A; border: 1px solid #E4604A;\n}\nQPushButton#btnDestruct:hover { background: #463434; color: #ff6f58; }\n\nQPushButton#btnApply {\n    background: #4a4a4a; color: #E6E6E6; border: 1px solid #262626;\n    border-radius: 5px; min-height: 28px; max-height: 28px;\n    font-size: 12px; font-weight: bold; padding: 0 10px;\n}\nQPushButton#btnApply:hover { background: #555555; }\n\nQPushButton#btnAction {\n    background: #2c2c2c; color: #A8A8A8; border: 1px solid #262626;\n    border-radius: 5px; min-height: 28px; max-height: 28px;\n    font-size: 11px; font-weight: bold; letter-spacing: 0.6px; padding: 0 10px;\n}\nQPushButton#btnAction:hover { background: #323232; color: #E6E6E6; }\nQPushButton#btnAction:disabled { background: #2c2c2c; color: #585858; }\n\nQPushButton#btnStepActive { background: #4a4a4a; color: #ffffff; border: 1px solid #E8820C; }\nQPushButton#btnStepActive:hover { background: #555555; border: 1px solid #FF9A2E; }\nQPushButton#btnStepActive:pressed { background: #414141; }\nQPushButton#btnStepLocked { background: #383838; color: #6A6A6A; border: 1px solid #2c2c2c; }\nQPushButton#btnStepDone { background: #333a33; color: #8FB890; border: 1px solid #3a5a3a; }\nQPushButton#btnStepDone:hover { background: #3a443a; color: #A8CBA8; }\n\n/* Labels / status */\nQLabel#warningBanner {\n    background: #3a2c00; color: #E8B84B; border-left: 3px solid #E8820C;\n    padding: 8px 10px; font-weight: bold; font-size: 12px;\n}\nQLabel#statusOk {\n    background: #24331f; color: #5BBF6A; border: 1px solid #3a5a3a;\n    border-radius: 11px; padding: 4px 10px; font-size: 11px;\n}\nQLabel#statusWarn {\n    background: #3a2c00; color: #E8B84B;\n    border: 1px solid #5a4a1a; border-radius: 11px;\n    padding: 4px 10px; font-size: 11px;\n}\nQLabel#statusErr {\n    background: #3a2020; color: #E4604A;\n    border: 1px solid #5a3030; border-radius: 11px;\n    padding: 4px 10px; font-size: 11px;\n}\nQLabel#statusIdle {\n    background: #2c2c2c; color: #7A7A7A; border: 1px solid #262626;\n    border-radius: 11px; padding: 4px 10px; font-size: 11px;\n}\nQLabel#ctrlLabel { color: #BFBFBF; font-size: 11px; font-weight: bold; letter-spacing: 1.2px; }\nQLabel#hint { color: #B0B0B0; font-size: 11px; }\nQLabel#selLabel {\n    background: #2c2c2c; color: #E6E6E6; border: 1px solid #262626;\n    border-radius: 11px; padding: 4px 10px; font-size: 11px;\n}\nQLabel#frameWarn {\n    background: #3a2c00; color: #E8B84B; border-left: 2px solid #E8820C;\n    padding: 5px 7px; font-size: 11px;\n}\nQLabel#sbExtrasLabel { color: #B0B0B0; font-size: 11px; font-weight: bold; letter-spacing: 1px; }\n\n/* Step circles */\nQLabel#stepDone {\n    background: #24331f; color: #5BBF6A; border: 1px solid #3a5a3a;\n    border-radius: 13px; font-size: 12px; font-weight: bold;\n}\nQLabel#stepReady {\n    background: #E8820C; color: #241606; border: 1px solid #C96E08;\n    border-radius: 13px; font-size: 12px; font-weight: bold;\n}\nQLabel#stepLocked {\n    background: #363636; color: #6A6A6A; border: 1px solid #2c2c2c;\n    border-radius: 13px; font-size: 12px; font-weight: bold;\n}\nQLabel#stepConfirmDone { color: #5BBF6A; font-size: 11px; font-weight: bold; }\nQLabel#stepConfirmEmpty { color: transparent; font-size: 11px; }\nQLabel#stepTitle { color: #D6D6D6; font-size: 11px; font-weight: bold; letter-spacing: 0.5px; background: transparent; }\n\n/* Inputs */\nQLineEdit {\n    background: #2c2c2c; color: #E6E6E6; border: 1px solid #262626;\n    border-radius: 4px; padding: 5px 8px; font-size: 12px;\n    selection-background-color: #E8820C; selection-color: #241606;\n}\nQLineEdit:focus { border: 1px solid #E8820C; }\nQSpinBox, QDoubleSpinBox {\n    background: #2c2c2c; color: #E6E6E6; border: 1px solid #262626;\n    border-radius: 4px; padding: 2px 6px; font-size: 12px; min-height: 28px;\n}\nQSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #E8820C; }\nQSpinBox::up-button, QDoubleSpinBox::up-button {\n    subcontrol-origin: border; subcontrol-position: top right;\n    width: 17px; background: #404040; border-left: 1px solid #262626;\n    border-top-right-radius: 4px;\n}\nQSpinBox::down-button, QDoubleSpinBox::down-button {\n    subcontrol-origin: border; subcontrol-position: bottom right;\n    width: 17px; background: #404040; border-left: 1px solid #262626;\n    border-bottom-right-radius: 4px;\n}\nQSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,\nQSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: #5a5a5a; }\nQSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url(__SPINUP__); width: 9px; height: 9px; }\nQSpinBox::up-arrow:hover, QDoubleSpinBox::up-arrow:hover { image: url(__SPINUPH__); }\nQSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: url(__SPINDOWN__); width: 9px; height: 9px; }\nQSpinBox::down-arrow:hover, QDoubleSpinBox::down-arrow:hover { image: url(__SPINDOWNH__); }\nQComboBox {\n    background: #2c2c2c; color: #E6E6E6; border: 1px solid #262626;\n    border-radius: 4px; padding: 5px 28px 5px 8px; font-size: 12px; min-height: 28px;\n}\nQComboBox:hover { background: #323232; }\nQComboBox:focus { border: 1px solid #E8820C; }\nQComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 22px; border: none; border-left: 1px solid #262626; background: #404040; border-top-right-radius: 4px; border-bottom-right-radius: 4px; }\nQComboBox::drop-down:hover { background: #5a5a5a; }\nQComboBox::down-arrow { image: url(__SPINDOWN__); width: 11px; height: 11px; }\nQComboBox:hover::down-arrow, QComboBox::down-arrow:hover { image: url(__SPINDOWNH__); }\nQComboBox QAbstractItemView {\n    background: #404040; border: 1px solid #262626;\n    selection-background-color: #E8820C; selection-color: #241606; outline: none;\n}\n\n/* Sliders — transparent track, thin orange/dark line, white dot */\nQSlider::groove:horizontal { height: 4px; background: transparent; border: none; }\nQSlider::sub-page:horizontal { background: #E8820C; border-radius: 2px; }\nQSlider::add-page:horizontal { background: #0a0a0a; border-radius: 2px; }\nQSlider::handle:horizontal {\n    image: url(__SLH__); background: transparent; border: none;\n    width: 20px; height: 20px; margin: -8px 0;\n}\nQSlider::handle:horizontal:hover { image: url(__SLHH__); }\nQSlider[hov=true]::sub-page:horizontal { background: #FFA838; }\nQSlider[hov=true]::add-page:horizontal { background: #2c2c2c; }\nQSlider:disabled::sub-page:horizontal { background: #5a4000; }\nQSlider:disabled::add-page:horizontal { background: #0a0a0a; }\nQSlider:disabled::handle:horizontal { background: #888888; }\n\n/* Checkboxes */\nQCheckBox { color: #E6E6E6; font-size: 12px; spacing: 7px; }\nQCheckBox:hover { color: #ffffff; }\nQCheckBox::indicator {\n    width: 15px; height: 15px; border-radius: 3px;\n    background: #2c2c2c; border: 1px solid #7A7A7A;\n}\nQCheckBox::indicator:hover { border-color: #E8820C; }\nQCheckBox::indicator:checked {\n    background: #E8820C; border: 1px solid #C96E08; image: url(__CHECK__);\n}\nQCheckBox::indicator:checked:hover { background: #FF9A2E; border-color: #E8820C; }\nQCheckBox:disabled { color: #7A7A7A; }\nQCheckBox::indicator:disabled { background: #404040; border-color: #262626; }\n\n/* Divider */\nQFrame#divider { background: #262626; border: none; max-height: 1px; min-height: 1px; }\n\n/* HDRI cells */\nQFrame#hdriCellInactive { background: #2c2c2c; border: 2px solid transparent; border-radius: 5px; }\nQFrame#hdriCellActive   { background: #2c2c2c; border: 2px solid #E8820C; border-radius: 5px; }\n\n/* Scrollbar */\nQScrollBar:vertical { background: #333333; width: 10px; margin: 0; }\nQScrollBar::handle:vertical { background: #4a4a4a; border-radius: 5px; min-height: 28px; }\nQScrollBar::handle:vertical:hover { background: #555555; }\nQScrollBar::add-line, QScrollBar::sub-line { height: 0; }\nQScrollBar::add-page, QScrollBar::sub-page { background: transparent; }\n"
