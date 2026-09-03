# doctrine/ — the documents the published records cite

Every entry in a substation's `meta.metric_derivations` names an amendment by
filename. Until 2026-09-03 those documents lived in a OneDrive folder that was
not a git repository: 620,129 records cited evidence with no history, which
could be edited without trace.

`scripts/check_provenance_citations_resolve.py` proved the files EXISTED. It
could not prove they had not changed since the record cited them.

They live here, in the same repository as the records that cite them, so that a
citation resolves inside one versioned unit and CI can check it on every push.

Adding or amending a document here is a Bible §8 act. The gate fails the build
if any cited filename is missing.
