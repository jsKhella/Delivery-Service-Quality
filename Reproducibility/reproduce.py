"""Re-compute every number of a CURIOSITY report from its original sources (made by ./cq deliver, v1.14).

Run inside the REPRODUCIBILITY folder:   python reproduce.py

1. Checks that every source file listed in sources.json is in job/raw/ with the same SHA-256 fingerprint.
2. Re-runs every step's final code, in the original order (run_order.json), from a clean start. Earlier
   outputs are moved aside to job/old_runs/ first, never deleted.
3. Compares every output file and every recorded number with expected.json (what the report used).
Ends with REPRODUCED, or lists exactly what differs. Needs only Python and the packages in requirements.txt.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOB = HERE / "job"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def env_for(side: Path) -> dict:
    env = dict(os.environ)
    env.update({"CQ_ROOT": str(HERE), "CQ_JOB_DIR": str(JOB), "CQ_STEP_DIR": str(side),
                "PYTHONPATH": str(HERE) + os.pathsep + env.get("PYTHONPATH", ""),
                "PYTHONHASHSEED": "0", "PYTHONIOENCODING": "utf-8"})
    return env


def run_sql(side: Path, script: str, out: str | None) -> tuple[int, str]:
    import duckdb
    sql = (side / script).read_text(encoding="utf-8")
    sql = sql.replace("{raw}", (JOB / "raw").as_posix()).replace("{job}", JOB.as_posix()) \
             .replace("{step}", side.as_posix()).replace("{steps}", (JOB / "steps").as_posix())
    old = os.getcwd()
    try:
        os.chdir(side)
        con = duckdb.connect()
        if out:
            df = con.execute(sql).df()
            p = side / out
            p.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(p, index=False)
        else:
            con.execute(sql)
        return 0, ""
    except Exception as e:
        return 1, f"SQL error: {e}"
    finally:
        os.chdir(old)


def main() -> int:
    sources = json.loads((HERE / "sources.json").read_text(encoding="utf-8"))["files"]
    expected = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
    print(f"Reproducing report {expected['report_id']}")
    bad = []
    for s in sources:
        p = JOB / "raw" / s["file"]
        if not p.is_file():
            bad.append(f"missing job/raw/{s['file']}: {s['how_to_get']} ({s['url']})")
        elif sha(p) != s["sha256"]:
            bad.append(f"job/raw/{s['file']} is a different version (fingerprint differs from SOURCES.md)")
    if bad:
        print("Source files are not ready:\n- " + "\n- ".join(bad))
        return 2
    print(f"All {len(sources)} source files present, fingerprints match.")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    problems = []
    for st in expected["steps"]:
        sid = st["id"]
        side = JOB / "steps" / sid / "exec"
        outs = side / "outputs"
        if outs.exists():
            dest = JOB / "old_runs" / stamp / sid
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(outs), str(dest))
        outs.mkdir(parents=True)
        runs = json.loads((side / "run_order.json").read_text(encoding="utf-8"))
        for r in runs:
            if r["kind"] == "python":
                p = subprocess.run([sys.executable, r["script"]], cwd=side, env=env_for(side),
                                   capture_output=True, text=True)
                code, log = p.returncode, (p.stdout or "") + (p.stderr or "")
            else:
                code, log = run_sql(side, r["script"], r.get("out"))
            if code != 0:
                problems.append(f"{sid}: {r['script']} failed: {log[-600:]}")
                break
        print(f"  {sid} {st.get('title', '')}: {len(runs)} run(s) done")
    if not problems:
        for key, want in expected["outputs"].items():
            sid, rest = key.split("/", 1)
            p = JOB / "steps" / sid / "exec" / "outputs" / rest
            if not p.is_file():
                problems.append(f"{key} was not produced")
            elif sha(p) != want:
                problems.append(f"{key} differs from the original")
        got = {}
        for st in expected["steps"]:
            rj = JOB / "steps" / st["id"] / "exec" / "outputs" / "results.json"
            if rj.is_file():
                got.update(json.loads(rj.read_text(encoding="utf-8")))
        for rid, want in expected["results"].items():
            v = got.get(rid, {}).get("value")
            if v is None:
                problems.append(f"result {rid} was not recorded")
            elif want["value"] is not None and abs(float(v) - float(want["value"])) > 1e-9 * max(1.0, abs(float(want["value"]))):
                problems.append(f"result {rid}: {v} instead of {want['value']} {want.get('unit') or ''}")
    if problems:
        print("NOT REPRODUCED:\n- " + "\n- ".join(problems))
        return 1
    print(f"REPRODUCED: all {len(expected['outputs'])} output files are identical and all "
          f"{len(expected['results'])} numbers match report {expected['report_id']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
