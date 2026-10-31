# B5-01R3 — Additive Fixture Isolation and Preserved Historical Guards

**Status: local regression, validators, export and pre-report preservation passed; remote publication gates remain pending.** R3 restores the protected test and shared historical helper to their exact published bytes. State ownership is supplied by a narrowly selected pytest fixture. This keeps the historical integrity contract literal and confines writable HTTP test inputs to each server instance.

| Restored source | SHA-256 |
|---|---|
| `tests/test_admin_publish_workflow_reliability.py` | `bf7258d1d23df60eb0cf5a342ac0209d629b72703c901ea13b22f5763d8aac63` |
| `tests/public_refinement_snapshot.py` | `7d654ae6a8e606172749a4aadea082ed28a8146bd787168873d71a9258719d26` |

The additive factory replaces only the collected publish-test module’s `RunningServer` binding for the duration of each pytest test. Every instance owns a temporary sync-state directory and passes its path through the handler’s existing explicit API. It retains the real HTTP handler, server, coordinator, response and original test assertions. Original enter/exit behavior, three-second HTTP deadline and event synchronization remain intact. Bind, thread-construction and thread-start failure paths clean acquired resources; ordinary teardown closes the coordinator and owned directory after the original server teardown. Production defaults and stable lock-inode behavior remain unchanged.

The six published HTTP tests continue executing from their unchanged source. The conftest replacement is function-scoped and rolls back automatically. New tests exercise real successful HTTP requests, stable lock-inode reuse, unchanged default-state bytes, independent nested instances, body/bind/thread failure cleanup and module-binding restoration. Running the protected file directly through `unittest.main` bypasses pytest’s conftest fixture; the repository’s supported mandatory runner is pytest. This is a documented non-blocking runner constraint.

R2’s independently reviewed experiment remains fully traceable in an authenticated archival package: complete helper and fixture sources, original 20-case tests, independent authorization receipt, canonical fixture diff, helper diff and boundary review. Its full helper digest is `13c66fe9e9887ae9b7520d3dc65b563fde46a037c2a30e3f4fc63d44a9afbb42`; the archived fixture is `34420cb25c55df54ecb65ff9d7e4dcd2e9e258cc85101fe9806f790203e6b60f`. The pinned archive manifest is `f8ed721670d485bc96f408031a005ef20fea5d3a15a996ccb72a9e4a5748e47b`.

All **20 archival cases, including 18 negative cases**, retain their original functions, parameters and assertions. They load a uniquely named private archival module after exact inventory and byte authentication. They cannot replace the live historical helper or establish a current exemption. Nine archive-tamper cases reject altered package members and unexpected files; three live-guard negatives prove B1G and both Tier2 checks still reject protected-source edits. These form part of **21 new isolation/archive-separation regression cases**.

Independent preapplication reviews approved the live fixture and archival boundary. The original eleven historical transaction failures and subsequent two Tier2 boundary failures remain preserved separately. B1M’s original pending-P034 observation, author-count discrepancy and numerical caveats remain unchanged; the later accepted publication URL has independent current-state coverage. No scientific review or accepted publication decision was repeated.

Verified gates so far are **B1G:1 passed; boundary/HTTP/archive:76 passed; integration:130 passed**. These are separately recorded, overlapping selections and must not be added into a unique full-suite total.

| Mandatory final field | Actual local result |
|---|---|
| Complete regression suite | 2,445 passed;389 subtests passed;zero failures;two existing warnings;all14 earlier failures pass |
| Authoritative/public validators | Zero errors;294 authoritative and62 paper/affiliation warnings retained;zero relationship warnings |
| Deterministic second export | All seven outputs byte-identical to authenticated first export;EXPORT_REPRODUCIBLE=1 |
| Pre-report preservation | 29,140 established +986 additional checks;zero failures;all defined flags0 |
| Data/decisions/accounting | 127 rows;11 accepted;13 holds;120 historical/118 active-public unresolved;674public/557formal/613mapped/1410relationships;taxonomy unchanged |
| Final staged/committed/published preservation | Recorded separately after report creation |
| Commit, remote, Pages, live JSON and hosted CI | PENDING until actual post-commit verification;no publication acceptance inferred |

The exact inventory and local receipt are in the B5 packet. The historical integration manifest remains unchanged; an appended completion manifest records current local acceptance. Independent reviews and the full17-entry protection inventory are copied separately. The preserved first failed checkpoints remain sealed; no failed workflow is automatically retried. The exact published SHA and hosted acceptance are recorded in the external final completion archive after the commit exists.

`7+1 MIGRATION STILL BLOCKED BY OFFICIAL METADATA`
