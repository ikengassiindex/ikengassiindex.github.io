# FINDING — six shards already exceed Convention #79, and the sentinel cannot see it

**Date** 20 September 2026
**Measured on** the deployed tree, file sizes on disk.
**Status** measurement only. Nothing changed.
**Found while** costing the payload of a proposed per-record provenance field.

---

Convention #79 was recalibrated on 18 August 2026 to a **60 MB threshold** and a
**45 MB target** per shard, "for post-v4.24 modifier chain headroom". Measured
today, every sharded country's largest file is over the threshold:

    country     largest shard   records   bytes/record
    poland          66.3 MB      19,546      3,391
    uk              65.1 MB      18,852      3,454
    france          65.0 MB      19,488      3,336
    germany         64.9 MB      19,137      3,394
    italy           64.1 MB      19,206      3,337
    us              60.7 MB      18,319      3,314

Six of six. None is near GitHub's 100 MB hard limit, so nothing is broken today —
but the convention exists to keep headroom, and the headroom is gone.

## Why nobody noticed

`tests/test_r7_cyber_v2_construct.py::TestPostCutoverInvariants::test_sharding_threshold_recalibrated_60_45`
asserts

    SSI_DATA_SHARD_THRESHOLD_MB == 60.0
    SSI_DATA_SHARD_TARGET_MB   == 45.0

It checks that the CONSTANTS hold their recalibrated values. It never stats a
file. The constants are correct and the files exceed them, and the test is green.

**This is the third instance today of the same defect class** — a check that
reads code or config where it should read the artefact:

1. `TestPostCutoverInvariants` asserting versions.json and the registry flags
   while the published records went unread — the R7 cutover was not done and the
   suite was green (`FINDING_r7_cyber_v2_actual_state.md`).
2. The whole 95-test suite staying green after the module's central policy was
   reversed, because nothing covered the write path
   (`PLAN_r7_cutover.md` step 1).
3. This.

`DOCTRINE_a_check_must_read_the_artefact.md` is not a style preference. Three
independent live defects today sat behind green checks that could not have
detected them.

## What follows

- A size assertion that stats the shard files belongs beside the constant
  assertion. Cheap, and it would have caught this whenever it crossed.
- Re-sharding these six to the 45 MB target is a separate operator decision with
  its own payload and cache-bust consequences. Not proposed here.
- For anything that adds a per-record field: the marginal cost is small
  (a 30-byte field is +0.9 per cent at ~3.4 KB per record, taking poland's
  largest shard 66.3 → 66.9 MB) but it is added to files already over. That is a
  reason to state the cost, not a reason to withhold provenance.
