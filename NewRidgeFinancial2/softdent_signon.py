"""SoftDent GUI Sign On credentials + optional UI assist (read-only; no SoftDent write-back).

Credentials come from environment / local .env only — never invent defaults in source.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Env names shared by NR2, SoftDent ops scripts, and scheduled tasks.
ENV_USER = "SOFTDENT_SIGNON_USER"
ENV_PASSWORD = "SOFTDENT_SIGNON_PASSWORD"
ENV_USER_ALT = "SOFTDENT_GUI_USER"
ENV_PASSWORD_ALT = "SOFTDENT_GUI_PASSWORD"

_DEFAULT_USER_HINT = "Dr"  # SoftDent Sign On user id for provider/owner login


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
    """Password for SoftDent Sign On only — do not log or put in HAL replies."""
    load_softdent_signon_env_files()
    return str(os.environ.get(ENV_PASSWORD) or os.environ.get(ENV_PASSWORD_ALT) or "").strip()


def softdent_signon_status() -> dict[str, Any]:
    """Safe status for HAL / refresh steps (no secret material)."""
    creds = resolve_softdent_signon_credentials()
    return {
        "ok": bool(creds.get("ok")),
        "user": creds.get("user"),
        "passwordConfigured": bool(creds.get("passwordConfigured")),
        "envUserKey": ENV_USER,
        "envPasswordKey": ENV_PASSWORD,
        "hint": creds.get("hint"),
    }


def ensure_softdent_signed_on(*, timeout_s: float = 25.0) -> dict[str, Any]:
    """If SoftDent Sign On / Change Login dialog is present, fill Dr credentials.

    SoftDent read-only assist — does not post clinical/financial data.
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
    except ImportError as exc:
        result["error"] = f"pywinauto missing: {exc}"
        return result

    result["attempted"] = True
    exe = Path(r"C:\SoftDent\SDWIN.EXE")
    try:
        app = Application(backend="uia").connect(path=str(exe), timeout=8)
    except Exception:
        if exe.is_file():
            try:
                app = Application(backend="uia").start(str(exe), timeout=20)
                result["steps"].append("launched_sdwin")
                time.sleep(3.0)
            except Exception as exc:  # noqa: BLE001
                result["error"] = f"could not start SoftDent: {type(exc).__name__}"
                return result
        else:
            result["error"] = "SoftDent SDWIN.EXE not found"
            return result

    deadline = time.time() + max(5.0, float(timeout_s))
    dialog = None
    while time.time() < deadline and dialog is None:
        for win in Desktop(backend="uia").windows():
            title = (win.window_text() or "").strip()
            lower = title.lower()
            if "sign on" in lower or "sign-on" in lower or "change login" in lower:
                dialog = win
                break
            # SoftDent sometimes titles the login dialog "SoftDent" with password edit.
            if title == "SoftDent" or lower.startswith("softdent"):
                try:
                    edits = [c for c in win.descendants() if c.element_info.control_type == "Edit"]
                    if len(edits) >= 2:
                        dialog = win
                        break
                except Exception:
                    pass
        if dialog is None:
            # Open Change Login from main window toolbar if present.
            try:
                main = app.window(title_re=".*SoftDent.*")
                btn = main.child_window(title="Change Login", control_type="Button")
                if btn.exists(timeout=0.5):
                    btn.click_input()
                    result["steps"].append("clicked_change_login")
                    time.sleep(1.0)
            except Exception:
                pass
            time.sleep(0.4)

    if dialog is None:
        # Already signed in — SoftDent main UI is up without a Sign On dialog.
        try:
            main = app.window(title_re=".*SoftDent.*")
            if main.exists(timeout=1):
                result["ok"] = True
                result["signedOn"] = True
                result["steps"].append("already_signed_on_or_no_dialog")
                return result
        except Exception:
            pass
        result["error"] = "Sign On dialog not found"
        return result

    try:
        edits = [c for c in dialog.descendants() if c.element_info.control_type == "Edit"]
        if not edits:
            result["error"] = "Sign On dialog has no edit fields"
            return result
        # SoftDent Sign On: first edit = user, last edit = password (typical).
        user_edit = edits[0]
        pass_edit = edits[-1] if len(edits) > 1 else edits[0]
        user_edit.set_focus()
        user_edit.type_keys("^a{BACKSPACE}" + user, with_spaces=True)
        time.sleep(0.2)
        pass_edit.set_focus()
        pass_edit.type_keys("^a{BACKSPACE}" + password, with_spaces=True)
        result["steps"].append("filled_user_password")
        # Prefer OK / Sign On button
        clicked = False
        for title in ("OK", "Sign On", "Login", "&OK"):
            try:
                btn = dialog.child_window(title=title, control_type="Button")
                if btn.exists(timeout=0.3):
                    btn.click_input()
                    clicked = True
                    result["steps"].append(f"clicked_{title.replace(' ', '_').lower()}")
                    break
            except Exception:
                continue
        if not clicked:
            pass_edit.type_keys("{ENTER}")
            result["steps"].append("pressed_enter")
        time.sleep(1.5)
        result["ok"] = True
        result["signedOn"] = True
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"sign_on_ui_{type(exc).__name__}"
        logger.warning("SoftDent Sign On UI assist failed: %s", type(exc).__name__)
    return result


if __name__ == "__main__":
    import json as _json

    print(_json.dumps({"status": softdent_signon_status(), "ensure": ensure_softdent_signed_on()}, indent=2))
