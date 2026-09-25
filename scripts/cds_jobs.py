#!/usr/bin/env python3
"""
List CDS jobs, and cancel the ones no live plan is waiting for.

    python3 scripts/cds_jobs.py --env <.env> --list
    python3 scripts/cds_jobs.py --env <.env> --plan <merged.json> --cancel-orphans

WHY
    Killing a fetch process does NOT cancel the jobs it submitted. They stay
    queued server-side and keep consuming the per-user concurrency budget — the
    same budget the killed process was consuming, so nothing is freed and the
    live fetch is starved by a run that no longer exists.

    This estate has been bitten by it once already: six orphans were found and
    five cancelled during the previous attempt.

WHAT COUNTS AS AN ORPHAN
    A job whose request does not match any region of the plan given by --plan.
    Matching is on the area box, which is what distinguishes the merged-region
    requests from the 59-box ones. A job that IS in the plan is never touched,
    whatever its age.

    With no --plan, nothing is cancellable and the tool only lists.

CONVENTION #56
    Every job is printed with its status and age before anything is cancelled,
    and --cancel-orphans reports what it cancelled and what it refused to.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys
from datetime import datetime, timezone


def load_env(p):
    env = {}
    with open(p, encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$", ln)
            if m:
                env[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    if not env.get("CDS_API_KEY"):
        sys.exit("CDS_API_KEY not found in the .env")
    return env


def age(js):
    for k in ("created_at", "started_at"):
        v = js.get(k)
        if not v:
            continue
        try:
            t = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - t).total_seconds() / 3600
        except Exception:
            pass
    return None


def boxes_of(plan):
    return {(round(r["north"], 2), round(r["west"], 2),
             round(r["south"], 2), round(r["east"], 2)) for r in plan["regions"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", required=True)
    ap.add_argument("--plan", default=None)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--cancel-orphans", action="store_true")
    a = ap.parse_args()

    import ecmwf.datastores as ds
    env = load_env(a.env)
    client = ds.Client(url=env.get("CDS_API_URL"), key=env["CDS_API_KEY"],
                       progress=False)

    keep = boxes_of(json.loads(pathlib.Path(a.plan).read_text())) if a.plan else set()
    if a.plan:
        print(f"\n  plan regions kept: {len(keep)}")
        for b in sorted(keep):
            print(f"    {b}")

    try:
        jobs = client.get_jobs(limit=200)
        entries = list(jobs.json.get("jobs", [])) if hasattr(jobs, "json") else list(jobs)
    except Exception as ex:
        print(f"  could not list jobs: {type(ex).__name__}: {ex}")
        return 1

    print(f"\n  {len(entries)} job(s) on the account")
    print("  fetching each live job's request — the listing does not carry it\n")
    print(f"  {'job id':<38}{'status':<12}{'age h':>7}  area / verdict")
    orphans, unknown = [], []
    for j in entries:
        jid = j.get("jobID") or j.get("job_id") or j.get("id") or "?"
        st = j.get("status", "?")
        if st not in ("accepted", "running"):
            continue
        ar, h = None, None
        try:
            rem = client.get_remote(str(jid))
            req = rem.request or {}
            if isinstance(req, dict):
                req = req.get("inputs", req)
            ar = req.get("area")
            h = age(rem.json if isinstance(getattr(rem, "json", None), dict) else j)
        except Exception as ex:
            print(f"  {str(jid):<38}{st:<12}{'      ?'}  DETAIL FAILED "
                  f"{type(ex).__name__}: {str(ex)[:60]}")
            unknown.append((jid, st))
            continue
        key = (tuple(round(float(x), 2) for x in ar)
               if isinstance(ar, (list, tuple)) and len(ar) == 4 else None)
        agestr = f"{h:7.1f}" if h is not None else "      ?"
        if key is None:
            # UNKNOWN IS NOT ORPHAN. A job whose area cannot be read is never
            # cancelled: the first version of this tool read area as None for
            # every job and would have cancelled the live fetch.
            print(f"  {str(jid):<38}{st:<12}{agestr}  area unreadable -> KEPT")
            unknown.append((jid, st))
        elif key in keep:
            print(f"  {str(jid):<38}{st:<12}{agestr}  {ar}  <- IN PLAN, kept")
        else:
            print(f"  {str(jid):<38}{st:<12}{agestr}  {ar}  <- orphan")
            orphans.append((jid, st, ar))

    print(f"\n  live jobs: {len(orphans)} orphan · "
          f"{len(unknown)} unclassifiable (kept) · "
          f"{len([j for j in entries if j.get('status') in ('accepted','running')]) - len(orphans) - len(unknown)} in plan")
    if unknown:
        print(f"  {len(unknown)} job(s) could not be classified and will NOT be")
        print("  cancelled. Unknown is not orphan.")
    if not a.cancel_orphans:
        if orphans:
            print("  re-run with --cancel-orphans to cancel the orphans only")
        return 0
    if not a.plan:
        sys.exit("  refusing to cancel without --plan: nothing defines what to keep")

    done = failed = 0
    for jid, st, ar in orphans:
        try:
            client.get_remote(jid).delete()
            done += 1
            print(f"    cancelled {jid}  ({st})  {ar}")
        except Exception as ex:
            failed += 1
            print(f"    FAILED    {jid}  {type(ex).__name__}: {str(ex)[:120]}")
    print(f"\n  cancelled {done} · failed {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
