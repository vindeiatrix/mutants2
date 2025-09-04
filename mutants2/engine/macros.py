import json
import os
import re
import time
from pathlib import Path
from typing import Callable, List


class MacroError(Exception):
    """Raised for macro parsing or execution errors."""


class MacroStore:
    """Store and execute command macros."""

    MACRO_DIR = Path(os.path.expanduser("~/.mutants2/macros"))

    def __init__(self) -> None:
        self._macros: dict[str, str] = {}
        self.echo: bool = True
        self._call_depth: int = 0

    # basic management -------------------------------------------------
    def add(self, name: str, script: str) -> None:
        self._macros[name] = script

    def get(self, name: str) -> str:
        return self._macros[name]

    def remove(self, name: str) -> None:
        self._macros.pop(name, None)

    def list(self) -> List[str]:
        return sorted(self._macros)

    def clear(self) -> None:
        self._macros.clear()


    # profile IO -------------------------------------------------------
    def save_profile(self, profile: str) -> None:
        self.MACRO_DIR.mkdir(parents=True, exist_ok=True)
        path = self.MACRO_DIR / f"{profile}.json"
        data = {"macros": self._macros, "echo": self.echo}
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_profile(self, profile: str) -> None:
        self.MACRO_DIR.mkdir(parents=True, exist_ok=True)
        path = self.MACRO_DIR / f"{profile}.json"
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"macros": {}, "echo": True}
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            data = {"macros": {}, "echo": True}
        self._macros.update(data.get("macros", {}))
        if "echo" in data:
            self.echo = bool(data["echo"])

    def list_profiles(self) -> List[str]:
        if not self.MACRO_DIR.is_dir():
            return []
        return sorted(p.stem for p in self.MACRO_DIR.glob("*.json"))

    # expansion --------------------------------------------------------
    def _substitute(self, script: str, args: List[str]) -> str:
        mapping = {str(i + 1): arg for i, arg in enumerate(args)}
        mapping["*"] = " ".join(args)

        def repl(m: re.Match) -> str:
            key = m.group(1)
            return mapping.get(key, "")

        return re.sub(r"\$(\d+|\*)", repl, script)

    def _tokenize(self, script: str) -> List[str]:
        tokens: List[str] = []
        cur = []
        level = 0
        i = 0
        while i < len(script):
            ch = script[i]
            if ch == "#":
                while i < len(script) and script[i] != "\n":
                    i += 1
                continue
            if ch in ";\n" and level == 0:
                token = "".join(cur).strip()
                if token:
                    tokens.append(token)
                cur = []
            else:
                if ch == "(":
                    level += 1
                elif ch == ")" and level > 0:
                    level -= 1
                cur.append(ch)
            i += 1
        token = "".join(cur).strip()
        if token:
            tokens.append(token)
        return tokens

    def expand(self, script: str, args: List[str]) -> List[str]:
        substituted = self._substitute(script, args)
        result: List[str] = []
        step_counter = 0

        def add(cmd: str) -> None:
            nonlocal step_counter
            step_counter += 1
            if step_counter > 1000:
                raise MacroError("macro expansion exceeded step limit")
            result.append(cmd)

        def _expand(text: str, depth: int) -> None:
            if depth > 8:
                raise MacroError("macro recursion too deep")
            for tok in self._tokenize(text):
                m = re.fullmatch(r"\((.*)\)\*(\d+)", tok, re.S)
                if m:
                    inner, count = m.group(1), int(m.group(2))
                    for _ in range(count):
                        _expand(inner, depth + 1)
                    continue
                m = re.fullmatch(r"([^()\s]+)\*(\d+)", tok)
                if m:
                    cmd, count = m.group(1), int(m.group(2))
                    for _ in range(count):
                        add(cmd)
                    continue
                if re.fullmatch(r"(\d*[nsew])+", tok, re.I):
                    for part in re.finditer(r"(\d*)([nsew])", tok, re.I):
                        num = int(part.group(1) or "1")
                        dirc = part.group(2).lower()
                        for _ in range(num):
                            add(dirc)
                    continue
                add(tok)

        _expand(substituted, 0)
        return result

    # execution --------------------------------------------------------
    def run(self, script: str, args: List[str], dispatch: Callable[[str], bool]) -> None:
        try:
            cmds = self.expand(script, args)
        except MacroError as e:
            print(f"Macro error: {e}")
            return
        if self._call_depth >= 8:
            print("Macro recursion too deep")
            return
        self._call_depth += 1
        try:
            for cmd in cmds:
                if self.echo:
                    print(f"> {cmd}")
                if cmd.lower().startswith("wait "):
                    try:
                        ms = int(cmd.split()[1])
                    except Exception:
                        print("Invalid wait")
                        break
                    ms = min(ms, 2000)
                    time.sleep(ms / 1000.0)
                    continue
                if not dispatch(cmd):
                    break
        finally:
            self._call_depth -= 1

    def expand_and_run_script(self, script: str, dispatch: Callable[[str], bool]) -> None:
        self.run(script, [], dispatch)

    def run_named(self, name: str, args: List[str], dispatch: Callable[[str], bool]) -> None:
        script = self._macros.get(name)
        if script is None:
            print("No such macro")
            return
        self.run(script, args, dispatch)

    def run_script(self, script: str, dispatch: Callable[[str], bool]) -> None:
        self.expand_and_run_script(script, dispatch)
