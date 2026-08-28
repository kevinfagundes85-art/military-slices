#!/usr/bin/env python3
"""NND T1 non-generative hidden-authority oracle.

Operated ONLY by the sealed-artifact custodian, on a machine BHE cannot read.
No model participates. Exact 4-tuple match or null. No repair, no interpolation.

Usage:
  python3 nnd_t1_authority_oracle.py SEALED_NND_T1_authority_schedule_2026-08-28.json requests.json

requests.json  : JSON array of request objects, each with exactly the four key fields:
                 task_id, gate_or_candidate_id, governed_snapshot_sha256, request_event_type
Writes         : responses.json  (one response per request, same order)
                 oracle_request_log.jsonl  (append-only audit trail)

Any request that is malformed, has extra/missing key fields, or does not match a
preregistered entry byte-for-byte returns {"authority_event": null}. That null is a
valid governed result: runtime then follows frozen HELM behavior for absent authority.
"""
import json, sys, hashlib, datetime

KEY_FIELDS = ("task_id", "gate_or_candidate_id",
              "governed_snapshot_sha256", "request_event_type")
EXPECTED_SCHEDULE_SHA256 = (
    "375fe496e267e2478562b676d851111ee3b81963e7108b9403b45dd61c94b71f")


def keytuple(o):
    return tuple(o[f] for f in KEY_FIELDS)


def main(schedule_path, requests_path):
    raw = open(schedule_path, "rb").read()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SCHEDULE_SHA256:
        sys.exit(f"ABORT: schedule hash mismatch\n  expected {EXPECTED_SCHEDULE_SHA256}"
                 f"\n  actual   {actual}")

    sched = json.loads(raw)
    table = {keytuple(e["key"]): e["value"] for e in sched["entries"]}

    requests = json.load(open(requests_path))
    if not isinstance(requests, list):
        sys.exit("ABORT: requests file must be a JSON array")

    responses = []
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open("oracle_request_log.jsonl", "a") as log:
        for req in requests:
            # strict: exactly the four key fields, nothing more, nothing less
            if not isinstance(req, dict) or set(req.keys()) != set(KEY_FIELDS):
                value = None
                matched = False
            else:
                value = table.get(keytuple(req))
                matched = value is not None
            responses.append({"request": req, "authority_event": value})
            log.write(json.dumps({"at": stamp, "request": req,
                                  "matched": matched}, sort_keys=True) + "\n")

    json.dump(responses, open("responses.json", "w"),
              sort_keys=True, separators=(",", ":"))
    hits = sum(1 for r in responses if r["authority_event"] is not None)
    print(f"served {len(responses)} requests; {hits} matched; "
          f"{len(responses) - hits} null")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
