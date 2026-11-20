"""Helpers that step code imports. The only way a number becomes a 'result' is through
record(), called from code, which stamps it with the code file that produced it.

    from engine.results import record, path, out
    df = pd.read_csv(path("raw:eurostat_unemployment.csv"))
    df.to_csv(out("clean.csv"), index=False)
    record("italy_unemp_2023", 7.7, unit="%", description="Italy unemployment rate, 2023 annual")
"""
from __future__ import annotations

import inspect
import json
import math
import os
import re
from pathlib import Path

_ID = re.compile(r"^[a-z][a-z0-9_]{1,60}$")


def _step_dir() -> Path:
    d = os.environ.get("CQ_STEP_DIR")
    if not d:
        raise RuntimeError("run this script with ./cq run (CQ_STEP_DIR is not set)")
    return Path(d)


def _job_dir() -> Path:
    return Path(os.environ["CQ_JOB_DIR"])


def path(ref: str) -> str:
    """'raw:file.csv' or 'S01:outputs/clean.csv' -> absolute path (read-only use)."""
    head, tail = ref.split(":", 1)
    if head == "raw":
        return str(_job_dir() / "raw" / tail)
    return str(_job_dir() / "steps" / head / "exec" / tail)


def out(name: str) -> str:
    """Path for an output file of the current step. Takes the bare file name ("t8.csv") and
    adds outputs/ itself; a name already starting with outputs/ (as ./cq sql --out and the plan
    write it) is accepted too, so it never becomes outputs/outputs/."""
    norm = name.replace("\\", "/")
    if norm.startswith("outputs/"):
        name = norm[len("outputs/"):]
        print(f"note: out() adds outputs/ itself; using outputs/{name}")
    p = _step_dir() / "outputs" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.suffix:
        # a warning, not an error: the step check decides (it needs the exact name in the plan)
        print(f"warning: output '{name}' has no file extension; the plan's outputs usually end in "
              f".csv (e.g. out(\"{name}.csv\")). The step check looks for the exact name in the plan.")
    return str(p)


_MAX_PATH_SAFE = 250  # Windows refuses most paths of 260 characters or more (MAX_PATH)


def unzip(ref: str, members: list[str] | None = None, into: str = "unz") -> dict[str, str]:
    """Unpack a zip (a sealed raw file or an earlier step's output) into outputs/<into>/, FLAT,
    under short names, so Windows' 260-character path limit is not hit. Don't call extractall():
    zip archives often hold deep folders with long names that Windows refuses (C0001 G12).

        files = unzip("raw:eea_losses.zip", ["data.csv"])   # {member name: written path}

    `members` are full member names or just their file names; None means every file. Each file is
    written as its base name, cut to 60 characters plus its extension, with _2, _3 ... when two
    names clash. The zip itself is only read."""
    import zipfile
    if not re.match(r"^[A-Za-z0-9_-]{1,20}$", into):
        raise ValueError(f"unzip: folder name '{into}' must be a short plain name (letters, digits, _ or -), "
                         f"for example 'unz'")
    src = path(ref)
    dest = _step_dir() / "outputs" / into
    written: dict[str, str] = {}
    with zipfile.ZipFile(src) as z:
        files = [i for i in z.infolist() if not i.is_dir()]
        if members is not None:
            want = [m.replace("\\", "/") for m in members]
            chosen, missing = [], []
            for m in want:
                hit = [i for i in files if i.filename == m] or \
                      [i for i in files if i.filename.rsplit("/", 1)[-1] == m]
                if not hit:
                    missing.append(m)
                for i in hit:
                    if i not in chosen:
                        chosen.append(i)
            if missing:
                names = ", ".join(i.filename for i in files[:10])
                raise KeyError(f"unzip: not found in {ref}: {missing}. The zip holds (first 10): {names}")
            files = chosen
        used: set[str] = set()
        plan = []
        for i in files:
            base = i.filename.rsplit("/", 1)[-1]
            stem, dot, ext = base.rpartition(".")
            if not dot or len(ext) > 10:
                stem, ext = base, ""
            stem = stem[:60] or "file"
            name = stem + ("." + ext if ext else "")
            n = 2
            while name.lower() in used:
                name = f"{stem}_{n}" + ("." + ext if ext else "")
                n += 1
            used.add(name.lower())
            target = dest / name
            if len(str(target.resolve())) >= _MAX_PATH_SAFE:
                raise OSError(f"unzip: path too long for Windows ({len(str(target.resolve()))} characters, "
                              f"limit {_MAX_PATH_SAFE}): {target}. Choose fewer or shorter members.")
            plan.append((i, target))
        dest.mkdir(parents=True, exist_ok=True)
        for i, target in plan:
            with z.open(i) as fin, open(target, "wb") as fout:
                while True:
                    chunk = fin.read(1 << 20)
                    if not chunk:
                        break
                    fout.write(chunk)
            written[i.filename] = str(target)
    print(f"unzipped {len(written)} file(s) from {ref} into outputs/{into}/ (flat, short names)")
    return written


def record(result_id: str, value, unit: str = "", description: str = "") -> None:
    if not _ID.match(result_id):
        raise ValueError(f"result id '{result_id}' must be lower_snake_case")
    if isinstance(value, bool) or not isinstance(value, (int, float)) and not hasattr(value, "__float__"):
        raise TypeError(f"result '{result_id}' must be a number, got {type(value).__name__}")
    v = float(value)
    if not math.isfinite(v):
        raise ValueError(f"result '{result_id}' is not a finite number: {value}")
    caller = Path(inspect.stack()[1].filename).resolve()
    sd = _step_dir().resolve()
    try:
        code = caller.relative_to(sd).as_posix()
    except ValueError:
        code = str(caller)
    f = sd / "outputs" / "results.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    data[result_id] = {"value": v, "unit": unit, "description": description, "code": code}
    f.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"recorded result {result_id} = {v} {unit}".rstrip())
