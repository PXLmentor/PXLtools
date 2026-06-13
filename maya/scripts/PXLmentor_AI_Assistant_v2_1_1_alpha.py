"""
Tool Name   : Claude for Maya (mAIa) — AI Assistant
Version     : 2.1.1-alpha
Stage       : Alpha
Author      : PXLmentor AI Pipeline TD
Description : Claude AI assistant embedded in Maya. Chat mode (streaming + code review) plus
              Agent Mode — Claude uses MayaMCP tools to directly control the scene autonomously.

HOW TO RUN IN MAYA:
    1. Open Maya Script Editor
    2. Set language to Python
    3. Paste the entire script and hit Ctrl+Enter

REQUIREMENTS:
    - Maya 2025 (Python 3, PySide6)
    - Internet access from Maya
    - Anthropic API key (sk-ant-...)
    - MayaMCP tool files (default: j:/ClaudeCode/mayamcp/src/mayatools/)

AGENT MODE — HOW IT WORKS:
    - Click the "AGENT MODE" button at the top of the UI
    - Claude receives tool definitions matching the MayaMCP server
    - When Claude calls a tool, mAIa executes the function directly in Maya (no socket needed)
    - Each tool call and result is shown as a bubble in the chat
    - The loop continues until Claude is done (stop_reason == "end_turn")

FILES STORED IN:
    ~/Documents/maya/claude_for_maya/
        config.json            -- API key + MCP path
        logs/session_001.json  -- last 5 session logs (rotating)

CHANGELOG:
    v2.1.0-alpha
            - Window width 720px (from 550px) — fixes all horizontal overflow
            - Mode selector: CHAT MODE / AGENT MODE dual-button at the top (orange = active)
            - Quick Prompts row: 5 one-click buttons — List Scene, Sel Meshes, Key Light,
              New Scene, Focus View — inject prompt and auto-send in Agent Mode
            - Agent config frame auto-shows/hides with mode toggle
            - Send button: brand orange BTN_PRIMARY; Clear: danger red
            - Input scrollField height 110px; Send/Clear buttons 50px
            - Image panel collapsed by default
            - _C color token class added — all inline tuples replaced
            - All rowLayout column widths corrected for 720px window
            - Bubble improvements: 24px headers, 5px separators, 50-380px clamp
            - BUG FIX: NoneType guard on AgentLoop content blocks
            - BUG FIX: bounds check on LogViewerDialog._on_exchange_select
    v2.0.0  - Agent Mode with MayaMCP tool_use API integration
            - MayaToolExecutor executes MayaMCP tools directly in Maya
            - AgentLoop: iterative tool-use rounds, TOOL CALL / TOOL RESULT bubbles
    v1.4.1  - Version label corrected. No functional changes.
    v1.4.0  - Live streaming responses, animated thinking indicator
            - Config + logs stored in ~/Documents/maya/claude_for_maya/
            - Session log (last 5 sessions, rotating), Log Viewer
    v1.3.0  - API key saved to disk, auto-loads on startup
    v1.2.0  - Full-width chat bubbles
    v1.1.0  - Multiple image attachments (up to 6 per message)
    v1.0.0  - Initial release
"""

import maya.cmds as cmds
import maya.mel as mel
import os
import json
import base64
import urllib.request
import urllib.error
import threading
import re
import datetime
import time


# ==============================================================================
# CONFIGURATION
# ==============================================================================
VERSION          = "2.1.1-alpha"
CLAUDE_MODEL     = "claude-sonnet-4-20250514"
MAX_TOKENS       = 8192
API_ENDPOINT     = "https://api.anthropic.com/v1/messages"
API_VERSION      = "2023-06-01"
WINDOW_NAME      = "claudeForMayaWin"
MAX_IMAGES       = 6
MAX_LOG_FILES    = 5
MAX_TOOL_ITERS   = 20

DEFAULT_MCP_PATH = "j:/ClaudeCode/mayamcp/src/mayatools"

MAYA_DOCS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "maya", "claude_for_maya")
CONFIG_FILE   = os.path.join(MAYA_DOCS_DIR, "config.json")
LOG_DIR       = os.path.join(MAYA_DOCS_DIR, "logs")


# ==============================================================================
# UI COLOR TOKENS
# ==============================================================================
class _C:
    HEADER_BG    = (0.14, 0.07, 0.06)
    BTN_PRIMARY  = (0.910, 0.510, 0.047)   # E8820C brand orange
    BTN_RESET    = (0.200, 0.200, 0.200)
    BTN_DANGER   = (0.480, 0.160, 0.120)
    STATUS_OK    = (0.140, 0.380, 0.180)
    STATUS_ERR   = (0.500, 0.200, 0.160)
    STATUS_IDLE  = (0.100, 0.100, 0.130)
    CHAT_BG      = (0.100, 0.100, 0.130)
    BUBBLE_USER  = (0.130, 0.190, 0.300)
    BUBBLE_AI    = (0.100, 0.200, 0.140)
    BUBBLE_TOOL  = (0.140, 0.100, 0.220)
    BUBBLE_OK    = (0.100, 0.220, 0.160)
    BUBBLE_ERR   = (0.400, 0.120, 0.120)
    BUBBLE_MAYA  = (0.100, 0.280, 0.160)
    QUICK_BTN    = (0.140, 0.140, 0.200)


# ==============================================================================
# QUICK PROMPTS
# ==============================================================================
QUICK_PROMPTS = [
    ("List Scene",   "List all objects in the scene by type."),
    ("Sel Meshes",   "Select all mesh objects in the scene."),
    ("Key Light",    "Add a directional key light at 45 degrees above and to the left."),
    ("New Scene",    "Create a new empty scene."),
    ("Focus View",   "Fit all objects in the viewport."),
]


# ==============================================================================
# STORAGE SETUP
# ==============================================================================
def ensure_dirs():
    for d in [MAYA_DOCS_DIR, LOG_DIR]:
        if not os.path.exists(d):
            try:
                os.makedirs(d)
            except Exception as e:
                print("Claude for Maya: could not create dir {} -- {}".format(d, e))

ensure_dirs()


# ==============================================================================
# CONFIG
# ==============================================================================
def save_config(api_key, mcp_path=None):
    try:
        existing = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                existing = json.load(f)
        existing["api_key"] = api_key
        existing["model"]   = CLAUDE_MODEL
        if mcp_path is not None:
            existing["mcp_path"] = mcp_path
        with open(CONFIG_FILE, "w") as f:
            json.dump(existing, f, indent=2)
        return True
    except Exception as e:
        print("Claude for Maya: could not save config -- {}".format(e))
        return False


def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            return data.get("api_key", ""), data.get("mcp_path", DEFAULT_MCP_PATH)
    except Exception as e:
        print("Claude for Maya: could not load config -- {}".format(e))
    return "", DEFAULT_MCP_PATH


# ==============================================================================
# SESSION LOG
# ==============================================================================
def _log_path(index):
    return os.path.join(LOG_DIR, "session_{:03d}.json".format(index))


def save_session_log(session):
    try:
        for i in range(MAX_LOG_FILES, 0, -1):
            src = _log_path(i)
            dst = _log_path(i + 1)
            if os.path.exists(src):
                if i >= MAX_LOG_FILES:
                    os.remove(src)
                else:
                    os.rename(src, dst)
        with open(_log_path(1), "w") as f:
            json.dump(session, f, indent=2)
    except Exception as e:
        print("Claude for Maya: could not save session log -- {}".format(e))


def load_all_logs():
    logs = []
    for i in range(1, MAX_LOG_FILES + 1):
        p = _log_path(i)
        if os.path.exists(p):
            try:
                with open(p, "r") as f:
                    data = json.load(f)
                n     = len(data.get("exchanges", []))
                label = "Session {}  --  {}  ({} exchange{})".format(
                    i, data.get("timestamp", "unknown"),
                    n, "s" if n != 1 else "")
                logs.append((label, data, p))
            except Exception:
                pass
    return logs


# ==============================================================================
# SYSTEM PROMPTS
# ==============================================================================
CHAT_SYSTEM_PROMPT = """You are Claude, an AI assistant embedded directly inside Autodesk Maya.
Your job is to help 3D artists by generating Python code that uses maya.cmds (and occasionally maya.mel) to accomplish tasks in Maya.

RULES:
1. When the user asks you to do something in Maya, ALWAYS respond with:
   - A brief explanation of what you will do (1-3 sentences, plain text)
   - A single Python code block using ```python ... ``` markers
2. The code block must be self-contained and runnable via exec() in Maya's Script Editor environment.
3. Always import maya.cmds as cmds at the top of every code block.
4. If the user provides images (reference photos, layout sketches, mood boards), analyze ALL of them.
   Use them together: one image might define layout, another materials, another lighting mood.
5. When recreating a scene from images:
   - Lock in camera framing first (focal length, position, rotation)
   - Place polygon stand-ins for major elements with correct proportions
   - Use real-world scale (1 unit = 1 cm by default in Maya)
   - Add basic lighting that matches the mood
   - Name everything clearly (e.g. GRP_furniture, CAM_main, LIGHT_key)
6. Never use external libraries beyond maya.cmds, maya.mel, math, os, and sys.
7. If you cannot accomplish something in Maya Python, say so clearly.
8. Keep code clean, commented, and production-ready.
9. If no code is needed, just reply in plain text without a code block.
"""

AGENT_SYSTEM_PROMPT = """You are an AI assistant embedded inside Autodesk Maya with direct access to Maya's scene through tools.

Your job is to help 3D artists by using your tools to make changes in Maya directly and autonomously.

RULES:
1. Use your tools to perform all actions in Maya. Do NOT write Python code blocks.
2. Before starting, briefly describe what you will do (1-2 sentences).
3. Use list_objects_by_type to understand the current scene before making significant changes.
4. Always name objects clearly following Maya conventions: GRP_groupName, CAM_cameraName, LIGHT_lightName.
5. After creating objects, call viewport_focus so the artist can see the result.
6. Work methodically: create objects first, set transforms, then apply materials.
7. After completing a task, summarize what was accomplished in plain text.
8. Use real-world scale (1 unit = 1 cm by default in Maya).
9. If a task is beyond what your tools can do, clearly explain the limitation and offer a Chat Mode alternative.
10. Never hallucinate tool results. Always act on what the tools actually return.
"""


# ==============================================================================
# MAYA MCP TOOL DEFINITIONS  (Anthropic tool_use format)
# ==============================================================================
MAYA_MCP_TOOLS = [
    {
        "name": "create_object",
        "description": (
            "Creates a primitive object or light in the Maya scene. "
            "Object types: cube, cone, sphere, cylinder, camera, spotLight, pointLight, directionalLight. "
            "Rotate values are in degrees."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the new object."},
                "object_type": {"type": "string", "description": "Type: cube, cone, sphere, cylinder, camera, spotLight, pointLight, directionalLight."},
                "translate": {"type": "array", "items": {"type": "number"}, "description": "World position [x, y, z]."},
                "rotate": {"type": "array", "items": {"type": "number"}, "description": "Rotation in degrees [x, y, z]."}
            },
            "required": ["name", "object_type"]
        }
    },
    {
        "name": "create_advanced_model",
        "description": "Creates a complex pre-built model. Types: car, tree, building, cup, chair.",
        "input_schema": {
            "type": "object",
            "properties": {
                "model_type": {"type": "string", "description": "Model type: car, tree, building, cup, chair."},
                "name": {"type": "string"},
                "scale": {"type": "number", "description": "Uniform scale. Default 1.0."},
                "translate": {"type": "array", "items": {"type": "number"}},
                "rotate": {"type": "array", "items": {"type": "number"}},
                "color": {"type": "array", "items": {"type": "number"}, "description": "Base color [R,G,B] 0-1."},
                "parameters": {"type": "object"}
            },
            "required": ["model_type"]
        }
    },
    {
        "name": "create_curve",
        "description": "Creates a NURBS curve. Types: custom, line, circle, square, rectangle, spiral, helix, arc, star, gear.",
        "input_schema": {
            "type": "object",
            "properties": {
                "curve_type": {"type": "string"},
                "name": {"type": "string"},
                "points": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                "parameters": {"type": "object"},
                "translate": {"type": "array", "items": {"type": "number"}},
                "rotate": {"type": "array", "items": {"type": "number"}},
                "scale": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["curve_type"]
        }
    },
    {
        "name": "create_material",
        "description": "Creates a material and optionally assigns it. Types: lambert, phong, blinn, metal, wood, marble, chrome, glass, brushed_metal, car_paint.",
        "input_schema": {
            "type": "object",
            "properties": {
                "material_type": {"type": "string"},
                "name": {"type": "string"},
                "color": {"type": "array", "items": {"type": "number"}, "description": "[R,G,B] 0-1."},
                "parameters": {"type": "object"},
                "assign_to": {"type": "string", "description": "Object name to assign material to."}
            },
            "required": ["material_type"]
        }
    },
    {
        "name": "curve_modeling",
        "description": "Creates geometry from curves. Operations: extrude, loft, revolve, sweep, planar, bevel.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string"},
                "curves": {"type": "array", "items": {"type": "string"}},
                "name": {"type": "string"},
                "parameters": {"type": "object"}
            },
            "required": ["operation", "curves"]
        }
    },
    {
        "name": "get_object_attributes",
        "description": "Returns all attributes of a Maya object including transform and shape attributes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"}
            },
            "required": ["object_name"]
        }
    },
    {
        "name": "list_objects_by_type",
        "description": "Returns a list of objects in the scene. filter_by: cameras, lights, materials, shapes, or omit for all.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_by": {"type": "string"}
            },
            "required": []
        }
    },
    {
        "name": "mesh_operations",
        "description": "Polygon mesh modeling. Operations: extrude, bevel, subdivide, smooth, boolean, combine, bridge, split.",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "operation": {"type": "string"},
                "parameters": {"type": "object"},
                "select_components": {
                    "oneOf": [{"type": "string"}, {"type": "array", "items": {"type": "string"}}]
                }
            },
            "required": ["object_name", "operation"]
        }
    },
    {
        "name": "organize_objects",
        "description": "Organize objects via grouping/parenting/layout. Operations: group, parent, layout, center_pivot, align, distribute.",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string"},
                "objects": {"type": "array", "items": {"type": "string"}},
                "name": {"type": "string"},
                "parameters": {"type": "object"}
            },
            "required": ["operation", "objects"]
        }
    },
    {
        "name": "set_object_attribute",
        "description": "Sets a specific attribute on a Maya object.",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "attribute_name": {"type": "string"},
                "attribute_value": {}
            },
            "required": ["object_name", "attribute_name", "attribute_value"]
        }
    },
    {
        "name": "set_object_transform_attributes",
        "description": "Sets translate, rotate, and/or scale on an object. Only specify what needs to change. Rotate in degrees.",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"},
                "translate": {"type": "array", "items": {"type": "number"}},
                "rotate": {"type": "array", "items": {"type": "number"}},
                "scale": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["object_name"]
        }
    },
    {
        "name": "clear_selection_list",
        "description": "Clears the Maya selection (deselects all objects).",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "scene_new",
        "description": "Creates a new empty scene in Maya.",
        "input_schema": {
            "type": "object",
            "properties": {
                "force": {"type": "boolean", "description": "Force new scene even with unsaved changes."}
            },
            "required": []
        }
    },
    {
        "name": "scene_open",
        "description": "Opens a Maya scene file (.ma or .mb). Optionally loads as a reference.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "namespace": {"type": "string"}
            },
            "required": ["filename"]
        }
    },
    {
        "name": "scene_save",
        "description": "Saves the current Maya scene. Uses current name if filename not provided.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"}
            },
            "required": []
        }
    },
    {
        "name": "select_object",
        "description": "Selects an object in the Maya scene by name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string"}
            },
            "required": ["object_name"]
        }
    },
    {
        "name": "viewport_focus",
        "description": "Centers and fits the viewport to focus on an object. Pass null to fit all.",
        "input_schema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Object to focus on, or null to fit all."}
            },
            "required": ["object_name"]
        }
    }
]


# ==============================================================================
# HELPERS
# ==============================================================================
def extract_code_block(text):
    m = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r"```\s*(.*?)```", text, re.DOTALL)
    if m:
        c = m.group(1).strip()
        if "cmds." in c or "import" in c:
            return c
    return None


def strip_code_blocks(text):
    t = re.sub(r"```python\s*.*?```", "", text, flags=re.DOTALL)
    t = re.sub(r"```\s*.*?```", "", t, flags=re.DOTALL)
    return t.strip()


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_media_type(path):
    return {
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png":  "image/png",
        ".gif":  "image/gif",
        ".webp": "image/webp"
    }.get(os.path.splitext(path)[1].lower(), "image/jpeg")


def _safe_json(obj):
    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj)
    except Exception:
        return str(obj)


# ==============================================================================
# MAYA TOOL EXECUTOR
# ==============================================================================
class MayaToolExecutor:
    def __init__(self, tools_root):
        self.tools_root  = tools_root
        self._tool_paths = {}
        self._scan()

    def _scan(self):
        self._tool_paths.clear()
        if not os.path.isdir(self.tools_root):
            print("Claude for Maya [Agent]: MCP tools path not found: {}".format(self.tools_root))
            return
        for root, dirs, files in os.walk(self.tools_root):
            for fname in files:
                if fname.endswith(".py"):
                    name = os.path.splitext(fname)[0]
                    self._tool_paths[name] = os.path.join(root, fname)

    @property
    def available_tools(self):
        return list(self._tool_paths.keys())

    @property
    def is_ready(self):
        return len(self._tool_paths) > 0

    def execute(self, tool_name, tool_input):
        if tool_name not in self._tool_paths:
            raise ValueError("Unknown MayaMCP tool: '{}'. Available: {}".format(
                tool_name, ", ".join(sorted(self._tool_paths.keys()))))
        filepath = self._tool_paths[tool_name]
        try:
            with open(filepath, "r") as f:
                source = f.read()
        except Exception as e:
            raise RuntimeError("Could not read tool file {}: {}".format(filepath, e))

        import maya.cmds as _cmds
        import maya.mel as _mel
        namespace = {
            "__builtins__": __builtins__,
            "cmds": _cmds,
            "mel":  _mel,
        }
        try:
            exec(compile(source, filepath, "exec"), namespace)
        except Exception as e:
            raise RuntimeError("Error loading tool '{}': {}".format(tool_name, e))

        fn = namespace.get(tool_name)
        if fn is None or not callable(fn):
            raise RuntimeError("Function '{}' not found in {}".format(tool_name, filepath))
        return fn(**tool_input)


# ==============================================================================
# CLAUDE API
# ==============================================================================
class ClaudeAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    def send_message_streaming(self, messages, on_delta, on_complete, on_error):
        def _call():
            try:
                payload = {
                    "model":      CLAUDE_MODEL,
                    "max_tokens": MAX_TOKENS,
                    "system":     CHAT_SYSTEM_PROMPT,
                    "stream":     True,
                    "messages":   messages
                }
                data = json.dumps(payload).encode("utf-8")
                req  = urllib.request.Request(
                    API_ENDPOINT, data=data,
                    headers={
                        "x-api-key":         self.api_key,
                        "anthropic-version": API_VERSION,
                        "content-type":      "application/json"
                    },
                    method="POST"
                )
                full_text = ""
                with urllib.request.urlopen(req, timeout=120) as resp:
                    for raw_line in resp:
                        line = raw_line.decode("utf-8").strip()
                        if not line.startswith("data:"):
                            continue
                        payload_str = line[5:].strip()
                        if payload_str == "[DONE]":
                            break
                        try:
                            event = json.loads(payload_str)
                        except Exception:
                            continue
                        if event.get("type") == "content_block_delta":
                            delta = event.get("delta", {}).get("text", "")
                            if delta:
                                full_text += delta
                                on_delta(delta)
                on_complete(full_text)
            except urllib.error.HTTPError as e:
                on_error("HTTP {}: {}".format(e.code, e.read().decode("utf-8")))
            except Exception as e:
                on_error(str(e))

        threading.Thread(target=_call, daemon=True).start()

    def send_message(self, messages, system=None, tools=None):
        payload = {
            "model":      CLAUDE_MODEL,
            "max_tokens": MAX_TOKENS,
            "messages":   messages
        }
        if system:
            payload["system"] = system
        if tools:
            payload["tools"] = tools
        data = json.dumps(payload).encode("utf-8")
        req  = urllib.request.Request(
            API_ENDPOINT, data=data,
            headers={
                "x-api-key":         self.api_key,
                "anthropic-version": API_VERSION,
                "content-type":      "application/json"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError("HTTP {}: {}".format(e.code, e.read().decode("utf-8")))


# ==============================================================================
# AGENT LOOP
# ==============================================================================
class AgentLoop:
    def __init__(self, api, executor):
        self.api      = api
        self.executor = executor

    def run(self, messages, on_tool_call, on_tool_result, on_text, on_complete, on_error):
        def _loop():
            msgs = list(messages)
            try:
                for iteration in range(MAX_TOOL_ITERS):
                    try:
                        resp = self.api.send_message(
                            msgs,
                            system=AGENT_SYSTEM_PROMPT,
                            tools=MAYA_MCP_TOOLS
                        )
                    except Exception as e:
                        on_error(str(e))
                        return

                    stop_reason = resp.get("stop_reason", "end_turn")
                    content     = resp.get("content") or []   # BUG FIX: guard None

                    msgs.append({"role": "assistant", "content": content})

                    for block in content:
                        if block is None:                      # BUG FIX: skip None blocks
                            continue
                        if block.get("type") == "text" and block.get("text", "").strip():
                            on_text(block["text"])

                    tool_uses = [b for b in content
                                 if b is not None and b.get("type") == "tool_use"]  # BUG FIX

                    if not tool_uses or stop_reason == "end_turn":
                        on_complete()
                        return

                    tool_results = []
                    for tu in tool_uses:
                        tool_name  = tu.get("name", "unknown")
                        tool_input = tu.get("input", {})
                        tool_id    = tu.get("id", "")

                        on_tool_call(tool_name, tool_input)

                        try:
                            result     = self.executor.execute(tool_name, tool_input)
                            result_str = _safe_json(result)
                            on_tool_result(tool_name, result_str, True)
                        except Exception as e:
                            result_str = "ERROR: {}".format(str(e))
                            on_tool_result(tool_name, result_str, False)

                        tool_results.append({
                            "type":        "tool_result",
                            "tool_use_id": tool_id,
                            "content":     result_str
                        })

                    msgs.append({"role": "user", "content": tool_results})

                on_error("Agent stopped: exceeded {} tool iterations.".format(MAX_TOOL_ITERS))

            except Exception as e:
                on_error("Agent loop error: {}".format(str(e)))

        threading.Thread(target=_loop, daemon=True).start()


# ==============================================================================
# CODE REVIEW DIALOG
# ==============================================================================
class CodeReviewDialog:
    def __init__(self, code, on_execute):
        self.code       = code
        self.on_execute = on_execute
        self.win        = "claudeCodeReviewWin"
        self._build()

    def _build(self):
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)

        cmds.window(self.win,
                    title="Review Code  --  Claude for Maya v{}".format(VERSION),
                    widthHeight=(760, 580), sizeable=True)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=8,
                          columnAttach=("both", 12))
        cmds.separator(height=10, style="none")
        cmds.text(label="Claude generated the following Maya Python code.",
                  align="left", font="boldLabelFont")
        cmds.text(label="Review and edit if needed, then click Execute to run it in Maya.",
                  align="left")
        cmds.separator(height=8, style="in")

        self.code_field = cmds.scrollField(
            text=self.code, editable=True, wordWrap=False,
            height=430, font="fixedWidthFont",
            backgroundColor=_C.STATUS_IDLE
        )

        cmds.separator(height=8, style="in")
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(370, 370),
                       columnAttach=[(1, "both", 5), (2, "both", 5)])
        cmds.button(label="Execute in Maya", height=44,
                    backgroundColor=_C.STATUS_OK, command=self._execute)
        cmds.button(label="Cancel", height=44,
                    backgroundColor=_C.BTN_DANGER, command=self._cancel)
        cmds.setParent("..")
        cmds.separator(height=10, style="none")
        cmds.showWindow(self.win)

    def _execute(self, *args):
        code = cmds.scrollField(self.code_field, query=True, text=True)
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)
        self.on_execute(code)

    def _cancel(self, *args):
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)


# ==============================================================================
# LOG VIEWER DIALOG
# ==============================================================================
class LogViewerDialog:
    def __init__(self, on_execute):
        self.on_execute      = on_execute
        self.win             = "claudeLogViewerWin"
        self.logs            = load_all_logs()
        self.current_session = None
        self._build()

    def _build(self):
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)

        if not self.logs:
            cmds.confirmDialog(
                title="No Logs Found",
                message="No session logs found in:\n{}\n\nLogs are saved automatically.".format(LOG_DIR),
                button=["OK"]
            )
            return

        cmds.window(self.win,
                    title="Session Logs  --  Claude for Maya v{}".format(VERSION),
                    widthHeight=(820, 700), sizeable=True)

        cmds.columnLayout(adjustableColumn=True, rowSpacing=6,
                          columnAttach=("both", 10))
        cmds.separator(height=8, style="none")
        cmds.text(label="Session Logs  --  last {} sessions".format(MAX_LOG_FILES),
                  font="boldLabelFont", align="left", height=22)
        cmds.text(label="Select a session then an exchange to view the generated code.",
                  align="left", font="smallPlainLabelFont")
        cmds.separator(height=6, style="in")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(300, 490),
                       columnAttach=[(1, "both", 4), (2, "both", 4)],
                       adjustableColumn=2)

        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label="Sessions (newest first):", align="left",
                  font="boldLabelFont", height=20)
        self.session_list = cmds.textScrollList(
            height=190, allowMultiSelection=False,
            selectCommand=self._on_session_select
        )
        for (label, _, __) in self.logs:
            cmds.textScrollList(self.session_list, edit=True, append=label)
        cmds.setParent("..")

        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label="Exchanges in session:", align="left",
                  font="boldLabelFont", height=20)
        self.exchange_list = cmds.textScrollList(
            height=190, allowMultiSelection=False,
            selectCommand=self._on_exchange_select
        )
        cmds.setParent("..")
        cmds.setParent("..")  # rowLayout

        cmds.separator(height=6, style="in")
        cmds.text(label="User prompt:", align="left", font="boldLabelFont", height=18)
        self.prompt_field = cmds.scrollField(
            text="", editable=False, wordWrap=True, height=70,
            backgroundColor=(0.12, 0.18, 0.26)
        )
        cmds.separator(height=4, style="none")
        cmds.text(label="Generated code:", align="left", font="boldLabelFont", height=18)
        self.code_field = cmds.scrollField(
            text="", editable=True, wordWrap=False, height=220,
            font="fixedWidthFont", backgroundColor=_C.STATUS_IDLE
        )
        cmds.separator(height=6, style="in")
        cmds.rowLayout(numberOfColumns=3,
                       columnWidth3=(260, 260, 260),
                       columnAttach=[(1, "both", 5), (2, "both", 5), (3, "both", 5)])
        cmds.button(label="Re-execute Code in Maya", height=40,
                    backgroundColor=_C.STATUS_OK, command=self._reexecute)
        cmds.button(label="Open Log Folder", height=40,
                    backgroundColor=(0.28, 0.28, 0.40), command=self._open_folder)
        cmds.button(label="Close", height=40,
                    backgroundColor=_C.BTN_DANGER, command=self._close)
        cmds.setParent("..")
        cmds.separator(height=8, style="none")
        cmds.showWindow(self.win)

    def _on_session_select(self, *args):
        idx = cmds.textScrollList(self.session_list, query=True, selectIndexedItem=True)
        if not idx:
            return
        self.current_session = self.logs[idx[0] - 1][1]
        cmds.textScrollList(self.exchange_list, edit=True, removeAll=True)
        for i, ex in enumerate(self.current_session.get("exchanges", []), 1):
            preview  = ex.get("user", "")[:55].replace("\n", " ")
            ellipsis = "..." if len(ex.get("user", "")) > 55 else ""
            cmds.textScrollList(self.exchange_list, edit=True,
                                append="#{} -- {}{}".format(i, preview, ellipsis))
        cmds.scrollField(self.prompt_field, edit=True, text="")
        cmds.scrollField(self.code_field, edit=True, text="")

    def _on_exchange_select(self, *args):
        idx = cmds.textScrollList(self.exchange_list, query=True, selectIndexedItem=True)
        if not idx or self.current_session is None:
            return
        exchanges = self.current_session.get("exchanges", [])   # BUG FIX: bounds check
        ex_index  = idx[0] - 1
        if ex_index < 0 or ex_index >= len(exchanges):
            return
        ex = exchanges[ex_index]

        user_text = ex.get("user", "(no prompt recorded)")
        images    = ex.get("images", [])
        if images:
            user_text = "[Images: {}]\n{}".format(", ".join(images), user_text)
        cmds.scrollField(self.prompt_field, edit=True, text=user_text)

        code = ex.get("code", "")
        cmds.scrollField(self.code_field, edit=True,
                         text=code if code else "(no code generated in this exchange)")

    def _reexecute(self, *args):
        code = cmds.scrollField(self.code_field, query=True, text=True).strip()
        if not code or code.startswith("(no code"):
            cmds.confirmDialog(title="No Code", message="No code to execute.", button=["OK"])
            return
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)
        CodeReviewDialog(code, self.on_execute)

    def _open_folder(self, *args):
        try:
            import subprocess
            if os.name == "nt":
                subprocess.Popen(["explorer", LOG_DIR])
            else:
                subprocess.Popen(["open", LOG_DIR])
        except Exception:
            cmds.confirmDialog(title="Log Folder",
                               message="Log folder:\n{}".format(LOG_DIR), button=["OK"])

    def _close(self, *args):
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)


# ==============================================================================
# MAIN WINDOW
# ==============================================================================
class ClaudeForMaya:
    def __init__(self):
        self.win                  = WINDOW_NAME
        self.api                  = None
        self.conversation         = []
        self.pending_imgs         = []
        self.is_thinking          = False
        self.placeholder          = None
        self._img_rows            = {}
        self._saved_key, self._saved_mcp_path = load_config()
        self._stream_field        = None
        self._stream_buf          = ""
        self._dot_stop            = False
        self._current_exchange    = {}
        self._session             = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "exchanges": []
        }
        self._mode                = "chat"   # "chat" or "agent"
        self._agent_config_frame  = None
        self._executor            = None
        self._agent_loop          = None
        self._agent_iter          = 0

        self._build()
        if self._saved_key:
            cmds.evalDeferred(self._auto_connect)

    # --------------------------------------------------------------------------
    # UI BUILD
    # --------------------------------------------------------------------------
    def _build_pxl_header(self, parent_layout):
        from maya import OpenMayaUI as omui
        from PySide6 import QtWidgets, QtGui, QtCore
        import shiboken6

        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"
        header_rgb = tuple(int(v * 255) for v in _C.HEADER_BG)

        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(106)
        header_widget.setStyleSheet("background-color: rgb({},{},{});".format(*header_rgb))

        root_hbox = QtWidgets.QHBoxLayout(header_widget)
        root_hbox.setContentsMargins(10, 5, 10, 5)
        root_hbox.setSpacing(0)

        left_label = QtWidgets.QLabel()
        left_label.setFixedSize(96, 96)
        left_label.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = icon_path + "icon_claude_for_maya.png"
        if os.path.exists(tool_icon):
            pixmap = QtGui.QPixmap(tool_icon).scaled(
                96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            left_label.setPixmap(pixmap)
        else:
            left_label.setText("[Icon]")
            left_label.setStyleSheet("background-color: rgb(51,51,51); color: white;")
        root_hbox.addWidget(left_label)

        center_vbox = QtWidgets.QVBoxLayout()
        center_vbox.setContentsMargins(0, 0, 0, 0)
        center_vbox.setSpacing(2)
        center_vbox.setAlignment(QtCore.Qt.AlignVCenter)

        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(262, 48)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_path = icon_path + "PXLtools_logo.png"
        if os.path.exists(logo_path):
            logo_pixmap = QtGui.QPixmap(logo_path).scaled(
                262, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("PXLmentor")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_hbox = QtWidgets.QHBoxLayout()
        logo_hbox.setContentsMargins(0, 0, 0, 0)
        logo_hbox.addStretch()
        logo_hbox.addWidget(logo_label)
        logo_hbox.addStretch()

        name_label = QtWidgets.QLabel("Claude for Maya  //  mAIa")
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

        version_label = QtWidgets.QLabel("v{}".format(VERSION))
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        version_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")

        center_vbox.addLayout(logo_hbox)
        center_vbox.addWidget(name_label)
        center_vbox.addWidget(version_label)
        root_hbox.addLayout(center_vbox, 1)

        right_spacer = QtWidgets.QLabel()
        right_spacer.setFixedSize(96, 96)
        root_hbox.addWidget(right_spacer)

        layout_ptr = omui.MQtUtil.findLayout(parent_layout)
        if layout_ptr:
            maya_layout_widget = shiboken6.wrapInstance(int(layout_ptr), QtWidgets.QWidget)
            header_widget.setParent(maya_layout_widget)
            maya_layout_widget.layout().addWidget(header_widget)

    def _apply_min_width(self, window_name, min_width=720):
        try:
            from maya import OpenMayaUI as omui
            from PySide6 import QtWidgets
            import shiboken6
            main_ptr = omui.MQtUtil.mainWindow()
            main_win = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)
            title = cmds.window(window_name, query=True, title=True)
            for widget in main_win.findChildren(QtWidgets.QMainWindow):
                if widget.windowTitle() == title:
                    widget.setMinimumWidth(min_width)
                    return
            for widget in main_win.findChildren(QtWidgets.QWidget):
                if widget.windowTitle() == title:
                    widget.setMinimumWidth(min_width)
                    return
        except Exception as e:
            cmds.warning("PXLmentor: Could not set minimum width -- {}".format(e))

    def _build(self):
        if cmds.window(self.win, exists=True):
            cmds.deleteUI(self.win)

        cmds.window(self.win,
                    title="Claude for Maya  v{}  //  AI Scene Assistant".format(VERSION),
                    widthHeight=(720, 980),
                    sizeable=True,
                    resizeToFitChildren=False)

        cmds.columnLayout(adjustableColumn=True)

        # ── HEADER ────────────────────────────────────────────────────────────
        header_layout = cmds.columnLayout(
            adjustableColumn=True,
            backgroundColor=_C.HEADER_BG,
            rowSpacing=0, height=106
        )
        self._build_pxl_header(header_layout)
        cmds.setParent("..")

        # ── API Configuration ─────────────────────────────────────────────────
        cmds.frameLayout(label="API Configuration", collapsable=True,
                         collapse=False, marginWidth=10, marginHeight=6)
        cmds.rowLayout(numberOfColumns=4,
                       columnWidth4=(80, 440, 110, 80),
                       columnAttach=[(1, "both", 4), (2, "both", 4),
                                     (3, "both", 4), (4, "both", 4)])
        cmds.text(label="API Key:", align="right")
        self.api_key_field = cmds.textField(placeholderText="sk-ant-...")
        if self._saved_key:
            cmds.textField(self.api_key_field, edit=True, text=self._saved_key)
        cmds.button(label="Connect", backgroundColor=_C.BTN_RESET,
                    command=self._connect)
        cmds.button(label="Save Key", backgroundColor=_C.BTN_RESET,
                    command=self._save_key)
        cmds.setParent("..")
        self.api_status = cmds.text(
            label="  Not connected  --  config: {}".format(CONFIG_FILE),
            align="left", height=22, backgroundColor=_C.STATUS_ERR
        )
        cmds.setParent("..")  # frameLayout

        cmds.separator(height=6, style="in")

        # ── MODE SELECTOR ─────────────────────────────────────────────────────
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=True,
                       columnAttach=[(1, "both", 4), (2, "both", 4)])
        self.btn_chat_mode = cmds.button(
            label="CHAT MODE",
            height=36,
            backgroundColor=_C.BTN_PRIMARY,
            command=self._set_chat_mode
        )
        self.btn_agent_mode = cmds.button(
            label="AGENT MODE",
            height=36,
            backgroundColor=_C.BTN_RESET,
            command=self._set_agent_mode
        )
        cmds.setParent("..")

        cmds.separator(height=4, style="in")

        # ── Agent Config frame (shown when AGENT MODE active) ─────────────────
        self._agent_config_frame = cmds.frameLayout(
            label="Agent Config  (MayaMCP Path)",
            collapsable=True, collapse=True,
            marginWidth=10, marginHeight=6
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
        cmds.text(label="  MCP Tools Path:", align="left", height=18,
                  font="smallPlainLabelFont")
        self.mcp_path_field = cmds.textField(
            text=self._saved_mcp_path,
            placeholderText="Path to mayatools directory",
            changeCommand=self._on_mcp_path_change
        )
        self.mcp_tools_info = cmds.text(
            label="  Tools: not scanned  --  enable Agent Mode to scan",
            align="left", height=18, font="smallPlainLabelFont",
            backgroundColor=_C.STATUS_IDLE
        )
        cmds.setParent("..")   # columnLayout
        cmds.setParent("..")   # frameLayout

        # Agent status line (always visible when agent mode active)
        self.agent_status = cmds.text(
            label="",
            align="left", height=20,
            backgroundColor=_C.STATUS_IDLE,
            font="smallPlainLabelFont"
        )

        cmds.separator(height=4, style="in")

        # ── Conversation header ───────────────────────────────────────────────
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=1,
                       columnAttach=[(1, "both", 0), (2, "both", 4)])
        cmds.text(label="  Conversation", align="left",
                  font="boldLabelFont", height=22)
        cmds.button(label="View Logs", height=22,
                    backgroundColor=_C.BTN_RESET,
                    command=self._open_logs)
        cmds.setParent("..")

        # ── Chat scroll ───────────────────────────────────────────────────────
        self.chat_scroll = cmds.scrollLayout(
            height=400,
            horizontalScrollBarThickness=0,
            verticalScrollBarThickness=16,
            backgroundColor=_C.CHAT_BG
        )
        self.chat_col = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=6,
            columnAttach=("both", 6)
        )
        cmds.separator(height=8, style="none")
        self.placeholder = cmds.text(
            label="Start a conversation -- describe what you want to build,\n"
                  "or use the quick prompts below.",
            align="center", height=54,
            font="smallPlainLabelFont",
            backgroundColor=_C.CHAT_BG
        )
        cmds.setParent("..")  # chat_col
        cmds.setParent("..")  # chat_scroll

        # ── Thinking bar ──────────────────────────────────────────────────────
        self.thinking_bar = cmds.text(
            label="", align="left", height=20,
            backgroundColor=_C.CHAT_BG,
            font="smallPlainLabelFont"
        )

        cmds.separator(height=4, style="in")

        # ── Reference Images (collapsed by default) ───────────────────────────
        cmds.frameLayout(
            label="Reference Images  (max {})".format(MAX_IMAGES),
            collapsable=True, collapse=True, marginWidth=8, marginHeight=6
        )
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 110),
                       columnAttach=[(1, "both", 4), (2, "both", 4)])
        cmds.button(label="+ Add Image(s)", height=30,
                    backgroundColor=_C.BTN_RESET, command=self._attach_images)
        cmds.button(label="Clear All", height=30,
                    backgroundColor=_C.BTN_DANGER, command=self._clear_all_images)
        cmds.setParent("..")
        cmds.separator(height=4, style="none")
        self.img_scroll = cmds.scrollLayout(
            height=80, horizontalScrollBarThickness=0,
            verticalScrollBarThickness=16, backgroundColor=(0.11, 0.11, 0.14)
        )
        self.img_col = cmds.columnLayout(
            adjustableColumn=True, rowSpacing=2, columnAttach=("both", 4)
        )
        self.img_empty_label = cmds.text(
            label="No images attached", align="left", height=24,
            font="smallPlainLabelFont", backgroundColor=(0.11, 0.11, 0.14)
        )
        cmds.setParent("..")  # img_col
        cmds.setParent("..")  # img_scroll
        cmds.setParent("..")  # frameLayout

        cmds.separator(height=6, style="none")

        # ── Quick Prompts ─────────────────────────────────────────────────────
        cmds.text(label="  Quick Prompts:", align="left",
                  font="boldLabelFont", height=20)
        cmds.rowLayout(
            numberOfColumns=5,
            columnWidth5=(138, 138, 138, 138, 138),
            columnAttach=[(i, "both", 2) for i in range(1, 6)]
        )
        for qlabel, qprompt in QUICK_PROMPTS:
            cmds.button(
                label=qlabel, height=28,
                backgroundColor=_C.QUICK_BTN,
                annotation=qprompt,
                command=lambda x, t=qprompt: self._inject_quick_prompt(t)
            )
        cmds.setParent("..")

        cmds.separator(height=6, style="none")

        # ── Message input ─────────────────────────────────────────────────────
        cmds.text(label="  Your message:", align="left",
                  font="boldLabelFont", height=20)
        self.input_field = cmds.scrollField(
            height=110, wordWrap=True, editable=True, text="",
            backgroundColor=_C.STATUS_IDLE
        )

        cmds.separator(height=6, style="none")

        # ── Action buttons ────────────────────────────────────────────────────
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(550, 160),
                       columnAttach=[(1, "both", 5), (2, "both", 5)])
        self.send_btn = cmds.button(
            label="Send  (Chat Mode)", height=50,
            backgroundColor=_C.BTN_PRIMARY, command=self._send
        )
        cmds.button(label="Clear Chat", height=50,
                    backgroundColor=_C.BTN_DANGER, command=self._clear_chat)
        cmds.setParent("..")

        # ── Status bar ────────────────────────────────────────────────────────
        self.status_bar = cmds.text(
            label="  Ready  --  logs: {}".format(LOG_DIR),
            align="left", height=24,
            backgroundColor=_C.STATUS_IDLE,
            font="smallPlainLabelFont"
        )

        cmds.separator(height=6, style="none")
        cmds.showWindow(self.win)
        self._apply_min_width(self.win, 720)

    # --------------------------------------------------------------------------
    # MODE SELECTOR
    # --------------------------------------------------------------------------
    def _set_chat_mode(self, *args):
        self._mode = "chat"
        cmds.button(self.btn_chat_mode,  edit=True, backgroundColor=_C.BTN_PRIMARY)
        cmds.button(self.btn_agent_mode, edit=True, backgroundColor=_C.BTN_RESET)
        cmds.button(self.send_btn,       edit=True, label="Send  (Chat Mode)")
        cmds.frameLayout(self._agent_config_frame, edit=True, collapse=True)
        cmds.text(self.agent_status, edit=True, label="",
                  backgroundColor=_C.STATUS_IDLE)
        self._set_status("Chat Mode active.")

    def _set_agent_mode(self, *args):
        self._mode = "agent"
        cmds.button(self.btn_agent_mode, edit=True, backgroundColor=_C.BTN_PRIMARY)
        cmds.button(self.btn_chat_mode,  edit=True, backgroundColor=_C.BTN_RESET)
        cmds.button(self.send_btn,       edit=True, label="Send  (Agent Mode)")
        cmds.frameLayout(self._agent_config_frame, edit=True, collapse=False)
        self._on_agent_mode_toggle(True)

    def _is_agent_mode(self):
        return self._mode == "agent"

    # --------------------------------------------------------------------------
    # QUICK PROMPTS
    # --------------------------------------------------------------------------
    def _inject_quick_prompt(self, text):
        cmds.scrollField(self.input_field, edit=True, text=text)
        if self._is_agent_mode() and self.api and not self.is_thinking:
            self._send(None)
        else:
            self._set_status("Quick prompt loaded -- press Send.")

    # --------------------------------------------------------------------------
    # AGENT MODE INIT
    # --------------------------------------------------------------------------
    def _on_agent_mode_toggle(self, value):
        if value:
            self._init_executor()
        else:
            cmds.text(self.agent_status, edit=True,
                      label="  Agent Mode OFF  --  using Chat Mode",
                      backgroundColor=_C.STATUS_IDLE)
            self._set_status("Agent Mode OFF. Using Chat Mode.")

    def _on_mcp_path_change(self, value):
        if self._executor is not None:
            self._executor.tools_root = value
            self._executor._scan()
            self._update_tools_info()

    def _init_executor(self):
        path = cmds.textField(self.mcp_path_field, query=True, text=True).strip()
        self._executor   = MayaToolExecutor(path)
        self._agent_loop = AgentLoop(self.api, self._executor) if self.api else None
        self._update_tools_info()

        if self._executor.is_ready:
            n = len(self._executor.available_tools)
            cmds.text(self.agent_status, edit=True,
                      label="  Agent Mode ON  \u2713  {} tools loaded".format(n),
                      backgroundColor=_C.STATUS_OK)
            self._set_status("Agent Mode ON -- {} MayaMCP tools ready.".format(n))
        else:
            cmds.text(self.agent_status, edit=True,
                      label="  Agent Mode ON -- WARNING: no tools found at path",
                      backgroundColor=(0.45, 0.28, 0.10))
            self._set_status("Agent Mode ON but no tools found. Check MCP Tools Path.")

    def _update_tools_info(self):
        if self._executor:
            n = len(self._executor.available_tools)
            cmds.text(self.mcp_tools_info, edit=True,
                      label="  Tools found: {}  |  {}".format(n, self._executor.tools_root))
        else:
            cmds.text(self.mcp_tools_info, edit=True,
                      label="  Tools: not scanned")

    # --------------------------------------------------------------------------
    # CONNECT / SAVE KEY
    # --------------------------------------------------------------------------
    def _connect(self, *args):
        key = cmds.textField(self.api_key_field, query=True, text=True).strip()
        if not key.startswith("sk-"):
            cmds.text(self.api_status, edit=True,
                      label="  Invalid key -- must start with sk-ant-...",
                      backgroundColor=_C.STATUS_ERR)
            return
        self.api = ClaudeAPI(key)
        cmds.text(self.api_status, edit=True,
                  label="  Connected  \u2713  {}".format(CLAUDE_MODEL),
                  backgroundColor=_C.STATUS_OK)
        if self._executor:
            self._agent_loop = AgentLoop(self.api, self._executor)
        self._set_status("API connected -- ready.")

    def _auto_connect(self, *args):
        key = self._saved_key.strip()
        if key.startswith("sk-"):
            self.api = ClaudeAPI(key)
            cmds.text(self.api_status, edit=True,
                      label="  Connected  \u2713  {}  (auto-loaded)".format(CLAUDE_MODEL),
                      backgroundColor=_C.STATUS_OK)
            if self._executor:
                self._agent_loop = AgentLoop(self.api, self._executor)
            self._set_status("Auto-connected. Logs: {}".format(LOG_DIR))

    def _save_key(self, *args):
        key  = cmds.textField(self.api_key_field, query=True, text=True).strip()
        path = cmds.textField(self.mcp_path_field, query=True, text=True).strip()
        if not key.startswith("sk-"):
            cmds.confirmDialog(title="Invalid Key",
                               message="Key must start with sk-ant-...\nNot saved.",
                               button=["OK"])
            return
        if save_config(key, mcp_path=path):
            self._saved_key      = key
            self._saved_mcp_path = path
            cmds.confirmDialog(
                title="Saved",
                message="API key and MCP path saved to:\n{}".format(CONFIG_FILE),
                button=["OK"]
            )
            self._set_status("Key + MCP path saved.")
        else:
            self._set_status("Failed to save config -- check Script Editor output.")

    # --------------------------------------------------------------------------
    # IMAGE ATTACH
    # --------------------------------------------------------------------------
    def _attach_images(self, *args):
        if len(self.pending_imgs) >= MAX_IMAGES:
            cmds.confirmDialog(title="Image Limit Reached",
                               message="Maximum {} images per message.".format(MAX_IMAGES),
                               button=["OK"])
            return
        result = cmds.fileDialog2(
            fileMode=4,
            caption="Select Reference Image(s)  (Ctrl+click for multiple)",
            fileFilter="Images (*.jpg *.jpeg *.png *.webp *.gif)"
        )
        if not result:
            return
        added = 0
        for path in result:
            if len(self.pending_imgs) >= MAX_IMAGES:
                break
            if path not in self.pending_imgs:
                self.pending_imgs.append(path)
                self._add_image_row(path)
                added += 1
        if added:
            self._set_status("{} image(s) added -- {} total".format(
                added, len(self.pending_imgs)))

    def _add_image_row(self, path):
        if self.img_empty_label and cmds.text(self.img_empty_label, exists=True):
            cmds.text(self.img_empty_label, edit=True, label="", height=1)
        cmds.setParent(self.img_col)
        fname = os.path.basename(path)
        row = cmds.rowLayout(
            numberOfColumns=2, columnWidth2=(640, 72),
            columnAttach=[(1, "both", 4), (2, "both", 2)],
            backgroundColor=(0.15, 0.25, 0.36)
        )
        cmds.text(label="  \u2022  " + fname, align="left", height=24,
                  font="smallPlainLabelFont", backgroundColor=(0.15, 0.25, 0.36))
        cmds.button(label="Remove", height=24, backgroundColor=_C.BTN_DANGER,
                    command=lambda x, p=path, r=row: self._remove_image(p, r))
        cmds.setParent("..")
        self._img_rows[path] = row
        cmds.evalDeferred(
            lambda: cmds.scrollLayout(self.img_scroll, edit=True,
                                      scrollByPixel=("down", 9999))
        )

    def _remove_image(self, path, row_ui):
        if path in self.pending_imgs:
            self.pending_imgs.remove(path)
        if path in self._img_rows:
            del self._img_rows[path]
        try:
            cmds.deleteUI(row_ui)
        except Exception:
            pass
        if not self.pending_imgs:
            cmds.text(self.img_empty_label, edit=True,
                      label="No images attached", height=24)
        self._set_status("{} image(s) attached".format(len(self.pending_imgs)))

    def _clear_all_images(self, *args):
        for row in list(self._img_rows.values()):
            try:
                cmds.deleteUI(row)
            except Exception:
                pass
        self.pending_imgs = []
        self._img_rows    = {}
        cmds.text(self.img_empty_label, edit=True,
                  label="No images attached", height=24)
        self._set_status("All images cleared.")

    # --------------------------------------------------------------------------
    # SEND — dispatcher
    # --------------------------------------------------------------------------
    def _send(self, *args):
        if not self.api:
            cmds.confirmDialog(title="Not Connected",
                               message="Enter your API key and click Connect first.",
                               button=["OK"])
            return
        user_text = cmds.scrollField(self.input_field, query=True, text=True).strip()
        if not user_text:
            self._set_status("Please type a message before sending.")
            return
        if self.is_thinking:
            self._set_status("Claude is still responding -- please wait.")
            return

        if self._is_agent_mode():
            self._send_agent(user_text)
        else:
            self._send_chat(user_text)

    # --------------------------------------------------------------------------
    # SEND — Chat Mode
    # --------------------------------------------------------------------------
    def _send_chat(self, user_text):
        content    = []
        img_labels = []
        for path in self.pending_imgs:
            try:
                content.append({
                    "type": "image",
                    "source": {
                        "type":       "base64",
                        "media_type": get_media_type(path),
                        "data":       image_to_base64(path)
                    }
                })
                img_labels.append(os.path.basename(path))
            except Exception as e:
                self._set_status("Could not load {}: {}".format(os.path.basename(path), str(e)))
                return

        content.append({"type": "text", "text": user_text})
        self.conversation.append({"role": "user", "content": content})

        img_tag = ""
        if img_labels:
            img_tag = "[{} image(s): {}]\n".format(len(img_labels), ", ".join(img_labels))
        self._add_bubble("YOU", img_tag + user_text, bg=_C.BUBBLE_USER)

        self._current_exchange = {
            "user": user_text, "images": img_labels,
            "claude": "", "code": "", "mode": "chat"
        }

        cmds.scrollField(self.input_field, edit=True, text="")
        self._clear_all_images()

        self.is_thinking = True
        self._stream_buf  = ""
        cmds.button(self.send_btn, edit=True, enable=False, label="Streaming...")
        self._set_status("Sending to Claude (Chat Mode)...")

        self._stream_field = self._add_stream_bubble()
        self._start_dots()

        self.api.send_message_streaming(
            self.conversation,
            on_delta    = self._on_delta,
            on_complete = self._on_complete,
            on_error    = self._on_error
        )

    # --------------------------------------------------------------------------
    # SEND — Agent Mode
    # --------------------------------------------------------------------------
    def _send_agent(self, user_text):
        if self._executor is None or not self._executor.is_ready:
            self._init_executor()
            if not self._executor.is_ready:
                cmds.confirmDialog(
                    title="Agent Mode Error",
                    message="No MayaMCP tools found at:\n{}\n\nCheck the MCP Tools Path.".format(
                        self._executor.tools_root if self._executor else "unknown"),
                    button=["OK"]
                )
                return

        if self._agent_loop is None:
            self._agent_loop = AgentLoop(self.api, self._executor)

        # Build content array — same structure as chat mode, supports images
        content    = []
        img_labels = []
        for path in self.pending_imgs:
            try:
                content.append({
                    "type": "image",
                    "source": {
                        "type":       "base64",
                        "media_type": get_media_type(path),
                        "data":       image_to_base64(path)
                    }
                })
                img_labels.append(os.path.basename(path))
            except Exception as e:
                self._set_status("Could not load {}: {}".format(os.path.basename(path), str(e)))
                return
        content.append({"type": "text", "text": user_text})

        img_tag = ""
        if img_labels:
            img_tag = "[{} image(s): {}]\n".format(len(img_labels), ", ".join(img_labels))
        self._add_bubble("YOU", img_tag + user_text, bg=_C.BUBBLE_USER)
        agent_messages = [{"role": "user", "content": content}]

        self._current_exchange = {
            "user": user_text, "images": img_labels,
            "claude": "", "code": "", "mode": "agent"
        }

        cmds.scrollField(self.input_field, edit=True, text="")
        self._clear_all_images()

        self.is_thinking = True
        self._agent_iter = 0
        cmds.button(self.send_btn, edit=True, enable=False, label="Agent Running...")
        self._set_status("Agent Mode: Claude is working...")
        self._start_dots()

        self._agent_loop.run(
            agent_messages,
            on_tool_call   = self._on_agent_tool_call,
            on_tool_result = self._on_agent_tool_result,
            on_text        = self._on_agent_text,
            on_complete    = self._on_agent_complete,
            on_error       = self._on_agent_error
        )

    # --------------------------------------------------------------------------
    # AGENT CALLBACKS
    # --------------------------------------------------------------------------
    def _on_agent_tool_call(self, tool_name, tool_input):
        self._agent_iter += 1
        try:
            input_preview = json.dumps(tool_input, indent=2)
            if len(input_preview) > 400:
                input_preview = input_preview[:400] + "\n  ..."
        except Exception:
            input_preview = str(tool_input)

        label   = "TOOL  {}".format(tool_name)
        display = "{}  [call #{}]\n\n{}".format(tool_name, self._agent_iter, input_preview)
        cmds.evalDeferred(lambda l=label, d=display: self._add_bubble(
            l, d, bg=_C.BUBBLE_TOOL))
        cmds.evalDeferred(lambda: self._set_status(
            "Agent: calling {}  (#{})".format(tool_name, self._agent_iter)))

    def _on_agent_tool_result(self, tool_name, result_str, success):
        display = result_str
        if len(display) > 600:
            display = display[:600] + "\n  ..."
        bg    = _C.BUBBLE_OK if success else _C.BUBBLE_ERR
        label = "RESULT  {}  [{}]".format(tool_name, "OK" if success else "ERROR")
        cmds.evalDeferred(lambda l=label, d=display: self._add_bubble(l, d, bg=bg))

    def _on_agent_text(self, text_str):
        if text_str.strip():
            cmds.evalDeferred(lambda t=text_str: self._add_bubble(
                "CLAUDE", t, bg=_C.BUBBLE_AI))

    def _on_agent_complete(self):
        def _finish():
            self._stop_dots()
            self.is_thinking = False
            cmds.button(self.send_btn, edit=True,
                        enable=True, label="Send  (Agent Mode)")
            self._session["exchanges"].append(self._current_exchange)
            save_session_log(self._session)
            self._set_status("Agent done -- {} tool call(s).".format(self._agent_iter))
        cmds.evalDeferred(_finish)

    def _on_agent_error(self, error_msg):
        def _handle():
            self._stop_dots()
            self.is_thinking = False
            cmds.button(self.send_btn, edit=True,
                        enable=True, label="Send  (Agent Mode)")
            self._add_bubble("AGENT ERROR", error_msg, bg=_C.BUBBLE_ERR)
            self._set_status("Agent error -- see chat log.")
        cmds.evalDeferred(_handle)

    # --------------------------------------------------------------------------
    # CHAT STREAMING CALLBACKS
    # --------------------------------------------------------------------------
    def _on_delta(self, chunk):
        self._stream_buf += chunk
        buf = self._stream_buf
        cmds.evalDeferred(lambda b=buf: self._update_stream(b))

    def _update_stream(self, text):
        self._stop_dots()
        try:
            if self._stream_field and cmds.scrollField(self._stream_field, exists=True):
                cmds.scrollField(self._stream_field, edit=True, text=text)
                lines    = text.count("\n") + 1
                wrap_est = max(lines, len(text) // 72)
                h        = max(80, min(420, wrap_est * 20 + 24))
                cmds.scrollField(self._stream_field, edit=True, height=h)
            cmds.scrollLayout(self.chat_scroll, edit=True, scrollByPixel=("down", 9999))
        except Exception:
            pass

    def _on_complete(self, full_text):
        cmds.evalDeferred(lambda: self._handle_complete(full_text))

    def _handle_complete(self, full_text):
        self._stop_dots()
        self.is_thinking   = False
        self._stream_field = None
        self._stream_buf   = ""
        cmds.button(self.send_btn, edit=True, enable=True, label="Send  (Chat Mode)")
        self.conversation.append({"role": "assistant", "content": full_text})

        code         = extract_code_block(full_text)
        display_text = strip_code_blocks(full_text)

        try:
            children = cmds.columnLayout(self.chat_col, query=True, childArray=True) or []
            if children:
                last          = children[-1]
                grandchildren = cmds.columnLayout(last, query=True, childArray=True) or []
                for gc in grandchildren:
                    try:
                        if cmds.scrollField(gc, exists=True):
                            final = display_text
                            if code:
                                final += "\n\n[Code ready -- Review dialog opening...]"
                            cmds.scrollField(gc, edit=True, text=final)
                            lines    = final.count("\n") + 1
                            wrap_est = max(lines, len(final) // 72)
                            h        = max(60, min(380, wrap_est * 20 + 24))
                            cmds.scrollField(gc, edit=True, height=h)
                            break
                    except Exception:
                        pass
        except Exception:
            pass

        self._current_exchange["claude"] = display_text
        self._current_exchange["code"]   = code or ""
        self._session["exchanges"].append(self._current_exchange)
        save_session_log(self._session)

        if code:
            self._set_status("Code generated -- review before executing.")
            cmds.evalDeferred(lambda c=code: CodeReviewDialog(c, self._execute_code))
        else:
            self._set_status("Claude replied.")

    def _on_error(self, error_msg):
        cmds.evalDeferred(lambda: self._handle_error(error_msg))

    def _handle_error(self, error_msg):
        self._stop_dots()
        self.is_thinking   = False
        self._stream_field = None
        cmds.button(self.send_btn, edit=True, enable=True, label="Send  (Chat Mode)")
        self._add_bubble("ERROR", error_msg, bg=_C.BUBBLE_ERR)
        self._set_status("API error -- see chat log.")

    # --------------------------------------------------------------------------
    # THINKING DOTS
    # --------------------------------------------------------------------------
    def _start_dots(self):
        self._dot_stop = False

        def _dots():
            frames = [
                "  Claude is thinking  .",
                "  Claude is thinking  ..",
                "  Claude is thinking  ...",
                "  Claude is thinking     "
            ]
            i = 0
            while not self._dot_stop:
                label = frames[i % len(frames)]
                cmds.evalDeferred(lambda l=label: self._set_thinking_bar(l))
                time.sleep(0.45)
                i += 1

        threading.Thread(target=_dots, daemon=True).start()

    def _stop_dots(self):
        self._dot_stop = True
        try:
            cmds.evalDeferred(lambda: self._set_thinking_bar(""))
        except Exception:
            pass

    def _set_thinking_bar(self, label):
        try:
            cmds.text(self.thinking_bar, edit=True, label=label)
        except Exception:
            pass

    # --------------------------------------------------------------------------
    # EXECUTE CODE
    # --------------------------------------------------------------------------
    def _execute_code(self, code):
        try:
            exec(code, {"__builtins__": __builtins__})
            self._add_bubble("MAYA", "Code executed successfully.", bg=_C.BUBBLE_MAYA)
            self._set_status("Done -- code executed in Maya.")
        except Exception as e:
            self._add_bubble("MAYA ERROR", str(e), bg=_C.BUBBLE_ERR)
            self._set_status("Execution failed -- see chat log.")

    # --------------------------------------------------------------------------
    # CHAT BUBBLES
    # --------------------------------------------------------------------------
    def _add_stream_bubble(self):
        if self.placeholder and cmds.text(self.placeholder, exists=True):
            cmds.deleteUI(self.placeholder)
            self.placeholder = None

        cmds.setParent(self.chat_col)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=0)
        cmds.text(label="  CLAUDE  (streaming...)", align="left", height=24,
                  font="boldLabelFont", backgroundColor=(0.10, 0.28, 0.18))
        field = cmds.scrollField(
            text="", editable=False, wordWrap=True, height=80,
            backgroundColor=_C.BUBBLE_AI, font="plainLabelFont"
        )
        cmds.separator(height=5, style="none")
        cmds.setParent("..")

        cmds.evalDeferred(
            lambda: cmds.scrollLayout(self.chat_scroll, edit=True,
                                      scrollByPixel=("down", 9999))
        )
        return field

    def _add_bubble(self, role, text, bg=(0.15, 0.15, 0.19)):
        if self.placeholder and cmds.text(self.placeholder, exists=True):
            cmds.deleteUI(self.placeholder)
            self.placeholder = None

        cmds.setParent(self.chat_col)

        label_colors = {
            "YOU":         (0.18, 0.30, 0.50),
            "CLAUDE":      (0.10, 0.30, 0.20),
            "MAYA":        (0.10, 0.32, 0.18),
            "MAYA ERROR":  (0.52, 0.14, 0.14),
            "ERROR":       (0.52, 0.14, 0.14),
            "AGENT ERROR": (0.52, 0.14, 0.14),
        }
        if role.startswith("TOOL"):
            label_bg = (0.26, 0.14, 0.40)
        elif role.startswith("RESULT"):
            label_bg = (0.10, 0.30, 0.22) if "OK" in role else (0.50, 0.14, 0.14)
        else:
            label_bg = label_colors.get(role, (0.25, 0.25, 0.30))

        cmds.columnLayout(adjustableColumn=True, rowSpacing=0)
        cmds.text(label="  {}".format(role), align="left", height=24,
                  font="boldLabelFont", backgroundColor=label_bg)

        lines_count = text.count("\n") + 1
        wrap_est    = max(lines_count, len(text) // 72)
        h           = max(50, min(380, wrap_est * 20 + 24))

        use_fixed = role in ("MAYA", "MAYA ERROR", "ERROR", "AGENT ERROR") \
                    or role.startswith("TOOL") or role.startswith("RESULT")
        cmds.scrollField(
            text=text if text else "(empty)",
            editable=False, wordWrap=True, height=h,
            backgroundColor=bg,
            font="fixedWidthFont" if use_fixed else "plainLabelFont"
        )
        cmds.separator(height=5, style="none")
        cmds.setParent("..")

        cmds.evalDeferred(
            lambda: cmds.scrollLayout(self.chat_scroll, edit=True,
                                      scrollByPixel=("down", 9999))
        )

    # --------------------------------------------------------------------------
    # LOG VIEWER
    # --------------------------------------------------------------------------
    def _open_logs(self, *args):
        LogViewerDialog(self._execute_code)

    # --------------------------------------------------------------------------
    # CLEAR CHAT
    # --------------------------------------------------------------------------
    def _clear_chat(self, *args):
        if self._session["exchanges"]:
            save_session_log(self._session)
        self.conversation = []
        self._session = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "exchanges": []
        }
        children = cmds.columnLayout(self.chat_col, query=True, childArray=True) or []
        for child in children:
            try:
                cmds.deleteUI(child)
            except Exception:
                pass
        cmds.setParent(self.chat_col)
        self.placeholder = cmds.text(
            label="Conversation cleared -- start a new session.",
            align="center", height=54,
            font="smallPlainLabelFont",
            backgroundColor=_C.CHAT_BG
        )
        self._set_status("Chat cleared. New session started.")

    # --------------------------------------------------------------------------
    # STATUS
    # --------------------------------------------------------------------------
    def _set_status(self, msg):
        try:
            cmds.text(self.status_bar, edit=True, label="  " + msg)
        except Exception:
            pass


# ==============================================================================
# ENTRY POINT
# ==============================================================================
def run():
    ClaudeForMaya()


run()
