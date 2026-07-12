"""SoftDent GUI Sign On credentials + optional UI assist (read-only; no SoftDent write-back).

Credentials come from environment / local .env only — never invent defaults in source.

Program doctrine: prefer SoftDent database / ODBC / Sensei extract when the data is
there. The only way to obtain SoftDent data that cannot be reached via the database
is SoftDent Sign On + SoftDent UI (Reports / Accounting export), then file ingest.
"""

from __future__ import annotations

import logging
import os
import re
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Env names shared by NR2, SoftDent ops scripts, and scheduled tasks.
ENV_USER = "SOFTDENT_SIGNON_USER"
ENV_PASSWORD = "SOFTDENT_SIGNON_PASSWORD"
ENV_USER_ALT = "SOFTDENT_GUI_USER"
ENV_PASSWORD_ALT = "SOFTDENT_GUI_PASSWORD"

_DEFAULT_USER_HINT = "COMPUTE"  # SoftDent Sign On user id (workstation/computer login)

# Whole-program SoftDent data-access rule (HAL + refresh + playbook).
SOFTDENT_DATA_ACCESS_DOCTRINE = (
    "Prefer SoftDent database / ODBC / Sensei DataSync / sd_* SQLite when the needed "
    "rows are available there. The only way to get SoftDent data that cannot be reached "
    "by the database is SoftDent Sign On (env credentials) and use the SoftDent UI "
    "(Reports / Accounting → export Register, Collections, daysheet, etc.), then place "
    "the file for NR2 ingest/Sync. No invented dollars, no SoftDent write-back, and no "
    "fictional vendor CLI when the DB lane cannot supply the report."
)


def _candidate_env_files() -> list[Path]:
    roots = [
        Path(r"C:\New folder") / ".env",
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parents[1] / ".env",
    ]
    extra = str(os.environ.get("NEWRIDGE_PROJECT_ROOT") or "").strip()
    if extra:
        roots.insert(0, Path(extra) / ".env")
    seen: set[str] = set()
    out: list[Path] = []
    for path in roots:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def load_softdent_signon_env_files() -> list[str]:
    """Load SoftDent Sign On keys from local .env files into os.environ (no overwrite of set vars)."""
    loaded: list[str] = []
    wanted = {ENV_USER, ENV_PASSWORD, ENV_USER_ALT, ENV_PASSWORD_ALT}
    for path in _candidate_env_files():
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="ignore")
        except OSError:
            continue
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().strip('"').strip("'")
            if name not in wanted:
                continue
            if not str(os.environ.get(name) or "").strip():
                os.environ[name] = value
                loaded.append(f"{path.name}:{name}")
    return loaded


def resolve_softdent_signon_credentials() -> dict[str, Any]:
    """Return Sign On user/password for SoftDent GUI (empty password → not configured)."""
    load_softdent_signon_env_files()
    user = (
        str(os.environ.get(ENV_USER) or os.environ.get(ENV_USER_ALT) or "").strip()
        or _DEFAULT_USER_HINT
    )
    password = str(
        os.environ.get(ENV_PASSWORD) or os.environ.get(ENV_PASSWORD_ALT) or ""
    ).strip()
    return {
        "ok": bool(password),
        "user": user,
        "passwordConfigured": bool(password),
        # Never return password in API payloads — callers that need it use get_password().
        "source": (
            ENV_PASSWORD
            if str(os.environ.get(ENV_PASSWORD) or "").strip()
            else ENV_PASSWORD_ALT
            if str(os.environ.get(ENV_PASSWORD_ALT) or "").strip()
            else None
        ),
        "hint": (
            None
            if password
            else f"Set {ENV_USER}=Dr and {ENV_PASSWORD}=… in C:\\New folder\\.env (gitignored)."
        ),
    }


def get_softdent_signon_password() -> str:
    """Password for SoftDent Sign On only — do not log or put in HAL replies.

    SoftDent passwords are case-sensitive; this practice uses lowercase.
    """
    load_softdent_signon_env_files()
    return str(os.environ.get(ENV_PASSWORD) or os.environ.get(ENV_PASSWORD_ALT) or "").strip().lower()


def softdent_signon_status() -> dict[str, Any]:
    """Safe status for HAL / refresh steps (no secret material)."""
    creds = resolve_softdent_signon_credentials()
    return {
        "ok": bool(creds.get("ok")),
        "user": creds.get("user"),
        "passwordConfigured": bool(creds.get("passwordConfigured")),
        "envUserKey": ENV_USER,
        "envPasswordKey": ENV_PASSWORD,
        "envUserAltKey": ENV_USER_ALT,
        "envPasswordAltKey": ENV_PASSWORD_ALT,
        "hint": creds.get("hint"),
        "dataAccessDoctrine": SOFTDENT_DATA_ACCESS_DOCTRINE,
        "knowledge": (
            f"SoftDent GUI Sign On credentials live in environment variables "
            f"{ENV_USER} / {ENV_PASSWORD} (or {ENV_USER_ALT} / {ENV_PASSWORD_ALT}), "
            r"also loadable from C:\New folder\.env and NewRidgeFinancial2\.env. "
            "HAL and refresh never echo the password. "
            "Launch SoftDent only from the desktop or Start Menu shortcut "
            "('CS SoftDent Software.lnk' — includes WorkingDirectory C:\\SoftDent and -sus); "
            "never start SDWIN.EXE bare. "
            + SOFTDENT_DATA_ACCESS_DOCTRINE
        ),
    }


def format_softdent_data_access_hal_reply() -> str:
    """HAL-facing SoftDent data-access rule (DB first; else Sign On + UI only)."""
    return SOFTDENT_DATA_ACCESS_DOCTRINE


def format_softdent_signon_hal_reply(status: dict[str, Any] | None = None) -> str:
    """HAL-facing answer: where Sign On lives (env vars) — never includes the password."""
    st = status if isinstance(status, dict) else softdent_signon_status()
    user = str(st.get("user") or _DEFAULT_USER_HINT)
    configured = bool(st.get("passwordConfigured"))
    lines = [
        "SoftDent GUI Sign On (Change Login / Sign On dialog) uses environment variables — "
        f"`{ENV_USER}` and `{ENV_PASSWORD}` "
        f"(aliases `{ENV_USER_ALT}` / `{ENV_PASSWORD_ALT}`).",
        r"Also loaded from local gitignored `.env` (`C:\New folder\.env`, `NewRidgeFinancial2\.env`) "
        "and Windows User env when set.",
        f"Configured Sign On user id: `{user}`.",
        (
            "Password is configured in the environment (HAL will not print it)."
            if configured
            else f"Password is NOT configured yet — set `{ENV_PASSWORD}` in local `.env` / User env."
        ),
        SOFTDENT_DATA_ACCESS_DOCTRINE,
        "Ask HAL: Refresh SoftDent period — step `softdent_signon` uses these env vars for UI assist. "
        "HAL still will not write clinical/financial SoftDent data.",
    ]
    return " ".join(lines)


def _query_touches_softdent_signon_or_ui_data(query: str) -> bool:
    q = str(query or "").lower()
    if re.search(
        r"\b(sign\s*on|sign-on|change login|softdent\s+(login|password|credential)|"
        r"log\s*in\s+to\s+softdent|softdent\s+gui)\b",
        q,
    ):
        return True
    if "softdent" in q and re.search(r"\b(password|credential|login|sign\s*on|env)\b", q):
        return True
    # Data that cannot be reached by DB → Sign On + UI
    if re.search(
        r"\b("
        r"cannot be reached|can'?t (be )?reach|not in (the )?(database|db|odbc|sqlite)|"
        r"outside (the )?(database|db|odbc)|only (way|via|through).{0,20}(ui|gui|sign\s*on)|"
        r"(ui|gui).{0,20}(export|report)|register for (a )?period|collections (report|export)|"
        r"how (do i |to )?(get|pull|export).{0,40}(softdent|register|collections)"
        r")\b",
        q,
    ):
        return True
    if "softdent" in q and re.search(
        r"\b(database|odbc|sqlite|ui|gui|export|report|daysheet|register)\b",
        q,
    ):
        return True
    return False


def compile_softdent_signon_guidance(query: str, system_prompt: str = "") -> str:
    """Inject Sign On + UI-only data-path knowledge into HAL LLM context when relevant."""
    prompt = str(system_prompt or "")
    if "SOFTDENT_SIGNON_USER" in prompt and "cannot be reached by the database" in prompt:
        return ""
    if not _query_touches_softdent_signon_or_ui_data(query):
        return ""
    if "SOFTDENT_SIGNON_USER" in prompt:
        return "SOFTDENT DATA ACCESS: " + format_softdent_data_access_hal_reply()
    return (
        "SOFTDENT SIGN ON + DATA ACCESS: "
        + format_softdent_signon_hal_reply()
    )


# Preferred SoftDent launchers (desktop / Start Menu shortcuts — NOT bare SDWIN.EXE).
# Desktop shortcut includes WorkingDirectory=C:\SoftDent and Arguments=-sus.
SOFTDENT_SHORTCUT_CANDIDATES = (
    Path(r"C:\Users\Public\Desktop\CS SoftDent Software.lnk"),
    Path(os.path.expandvars(r"%PUBLIC%\Desktop\CS SoftDent Software.lnk")),
    Path(os.path.expandvars(r"%USERPROFILE%\Desktop\CS SoftDent Software.lnk")),
    Path(
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
        r"\CS SoftDent Software\CS SoftDent Software.lnk"
    ),
)


def resolve_softdent_launch_shortcut() -> Path | None:
    """Return desktop or Programs SoftDent .lnk (never invent a bare EXE launch)."""
    seen: set[str] = set()
    for path in SOFTDENT_SHORTCUT_CANDIDATES:
        try:
            resolved = path.resolve() if path.exists() else path
        except OSError:
            resolved = path
        key = str(resolved).lower()
        if key in seen:
            continue
        seen.add(key)
        if path.is_file():
            return path
    return None


def launch_softdent_via_shortcut() -> dict[str, Any]:
    """Start SoftDent from desktop/Programs shortcut only (os.startfile on .lnk)."""
    out: dict[str, Any] = {"ok": False, "shortcut": None, "method": None}
    shortcut = resolve_softdent_launch_shortcut()
    if shortcut is None:
        out["error"] = (
            "SoftDent desktop/Programs shortcut not found "
            "(expected 'CS SoftDent Software.lnk' on Public Desktop or Start Menu)."
        )
        return out
    out["shortcut"] = str(shortcut)
    try:
        # startfile on .lnk preserves Target, WorkingDirectory, and Arguments (-sus).
        os.startfile(str(shortcut))  # noqa: S606 — intentional SoftDent launch
        out["ok"] = True
        out["method"] = "os.startfile_shortcut"
    except OSError as exc:
        out["error"] = f"startfile_failed:{type(exc).__name__}"
        try:
            import subprocess

            subprocess.Popen(  # noqa: S603
                ["cmd", "/c", "start", "", str(shortcut)],
                cwd=str(shortcut.parent),
                shell=False,
            )
            out["ok"] = True
            out["method"] = "cmd_start_shortcut"
            out.pop("error", None)
        except Exception as exc2:  # noqa: BLE001
            out["error"] = f"launch_failed:{type(exc).__name__}/{type(exc2).__name__}"
    return out


def ensure_softdent_signed_on(
    *,
    timeout_s: float = 25.0,
    force_change_login: bool = False,
) -> dict[str, Any]:
    """If SoftDent Sign On / Change Login dialog is present, fill Dr credentials.

    SoftDent read-only assist — does not post clinical/financial data.
    Never logs the password. By default does not open Change Login when already
    signed in (main SoftDent Software window present).

    Launch rule: SoftDent is started only via desktop / Programs shortcut
    (CS SoftDent Software.lnk), never by invoking SDWIN.EXE bare.
    """
    status = softdent_signon_status()
    password = get_softdent_signon_password()
    user = str(status.get("user") or _DEFAULT_USER_HINT)
    result: dict[str, Any] = {
        "ok": False,
        "attempted": False,
        "signedOn": False,
        "user": user,
        "passwordConfigured": bool(password),
        "steps": [],
    }
    if not password:
        result["error"] = status.get("hint") or "SoftDent Sign On password not configured"
        return result

    try:
        from pywinauto import Application, Desktop
        from pywinauto.findwindows import find_windows
        import win32gui
    except ImportError as exc:
        result["error"] = f"pywinauto missing: {exc}"
        return result

    result["attempted"] = True

    def _main_hwnd() -> int | None:
        try:
            hwnds = find_windows(title_re=r".*SoftDent.*", backend="win32")
        except Exception:
            return None
        for h in hwnds:
            try:
                cls = win32gui.GetClassName(h)
                title = win32gui.GetWindowText(h)
            except Exception:
                continue
            # Prefer the SoftDent Software main frame (not Login / message boxes).
            if "SoftDent Software" in title or (
                "SOFTDENT" in cls.upper() and "login" not in title.lower()
            ):
                return int(h)
        for h in hwnds:
            try:
                title = win32gui.GetWindowText(h)
            except Exception:
                continue
            if "login" in title.lower() or title.strip() in {"SoftDent", "Sign On"}:
                continue
            return int(h)
        return None

    def _find_login_dialog():
        """Locate SoftDent Login / Sign On / Change Login (UIA then win32)."""
        for backend in ("uia", "win32"):
            try:
                desk = Desktop(backend=backend)
            except Exception:
                continue
            for win in desk.windows():
                try:
                    title = (win.window_text() or "").strip()
                except Exception:
                    continue
                lower = title.lower()
                if (
                    "sign on" in lower
                    or "sign-on" in lower
                    or "change login" in lower
                    or lower == "softdent login"
                    or (lower.startswith("softdent") and "login" in lower)
                ):
                    return win
                if title == "SoftDent" or lower.startswith("softdent"):
                    try:
                        edits = [
                            c
                            for c in win.descendants()
                            if getattr(getattr(c, "element_info", None), "control_type", None) == "Edit"
                            or c.class_name() == "Edit"
                        ]
                        if len(edits) >= 2:
                            return win
                    except Exception:
                        pass
        return None

    # If Login is open, do NOT treat main frame as already signed on.
    login_open = _find_login_dialog()
    main_hwnd = _main_hwnd()
    if main_hwnd and login_open is None and not force_change_login:
        result["ok"] = True
        result["signedOn"] = True
        result["steps"].append("already_signed_on_main_window")
        return result

    app = None
    try:
        if main_hwnd:
            app = Application(backend="uia").connect(handle=main_hwnd)
        else:
            app = Application(backend="uia").connect(path=r"C:\SoftDent\SDWIN.EXE", timeout=3)
    except Exception:
        launch = launch_softdent_via_shortcut()
        result["steps"].append(
            f"launched_via_shortcut:{launch.get('method') or launch.get('error')}"
        )
        result["launchShortcut"] = launch.get("shortcut")
        if not launch.get("ok"):
            result["error"] = launch.get("error") or "SoftDent shortcut launch failed"
            return result
        time.sleep(4.0)
        try:
            app = Application(backend="uia").connect(path=r"C:\SoftDent\SDWIN.EXE", timeout=30)
        except Exception as exc:  # noqa: BLE001
            result["steps"].append(f"connect_after_shortcut:{type(exc).__name__}")
            app = None

    deadline = time.time() + max(5.0, float(timeout_s))
    dialog = login_open
    change_login_clicked = False
    while time.time() < deadline and dialog is None:
        dialog = _find_login_dialog()
        if dialog is not None:
            break
        if force_change_login and not change_login_clicked and app is not None:
            try:
                main = app.window(title_re=".*SoftDent.*")
                btn = main.child_window(title="Change Login", control_type="Button")
                if btn.exists(timeout=0.5):
                    # Keyboard only — focus + Enter/Space (no mouse)
                    btn.set_focus()
                    time.sleep(0.1)
                    from pywinauto.keyboard import send_keys

                    send_keys("{ENTER}")
                    change_login_clicked = True
                    result["steps"].append("keyboard_change_login")
                    time.sleep(1.0)
            except Exception:
                pass
            time.sleep(0.4)
        else:
            time.sleep(0.4)

    if dialog is None:
        if _main_hwnd():
            result["ok"] = True
            result["signedOn"] = True
            result["steps"].append("already_signed_on_or_no_dialog")
            return result
        result["error"] = "Sign On dialog not found"
        return result

    try:
        # SoftDent Login is often win32 Edit (no UIA control_type).
        edits = []
        try:
            edits = [
                c
                for c in dialog.descendants()
                if getattr(getattr(c, "element_info", None), "control_type", None) == "Edit"
            ]
        except Exception:
            edits = []
        if not edits:
            try:
                edits = list(dialog.descendants(class_name="Edit"))
            except Exception:
                edits = []
        if not edits:
            result["error"] = "Sign On dialog has no edit fields"
            return result
        # SoftDent Login: keyboard only — type user, Tab, type password, Enter.
        # Never mouse click_input / never Escape.
        password = password.lower()
        from pywinauto.keyboard import send_keys
        from softdent_gui_export import _force_foreground

        _force_foreground(int(dialog.handle))
        time.sleep(0.2)
        # Focus first edit if possible without mouse
        try:
            edits[0].set_focus()
        except Exception:
            pass
        time.sleep(0.1)
        send_keys("^a{BACKSPACE}")
        send_keys(user, with_spaces=True, pause=0.04)
        time.sleep(0.15)
        send_keys("{TAB}")
        time.sleep(0.15)
        send_keys("^a{BACKSPACE}")
        send_keys(password, with_spaces=True, pause=0.04)
        result["steps"].append("filled_user_password_keyboard")
        time.sleep(0.2)
        send_keys("{ENTER}")
        result["steps"].append("pressed_enter_ok")
        time.sleep(1.5)
        result["ok"] = True
        result["signedOn"] = True
        # SoftDent may immediately prompt for a missing default printer after login.
        try:
            from softdent_gui_export import cancel_printer_dialogs, dismiss_softdent_alerts

            cancel_printer_dialogs()
            dismiss_softdent_alerts()
            result["steps"].append("swept_printer_dialogs_after_signon")
        except Exception:
            pass
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"sign_on_ui_{type(exc).__name__}"
        logger.warning("SoftDent Sign On UI assist failed: %s", type(exc).__name__)
    return result


if __name__ == "__main__":
    import json as _json

    print(_json.dumps({"status": softdent_signon_status(), "ensure": ensure_softdent_signed_on()}, indent=2))
