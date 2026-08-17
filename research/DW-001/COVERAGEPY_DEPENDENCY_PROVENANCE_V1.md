# DW-001 Coverage.py Dependency and Provenance Review v1

**Decision:** `GO` under the exact research-only boundary below.

**Reviewed package:** `coverage==7.15.2`.

**Selected distribution artifact:** `coverage-7.15.2-py3-none-any.whl`.

**Selected artifact SHA-256:** `eb6bcae8d1a9d305351ecb108232441d11c5cfe9de840a04388ba5d2db8d735c`.

**Upstream source commit:** `coveragepy/coveragepy@50d865908dfeb21a0bf1e6f05db578c11662f8dd`.

This review authorizes one development-only direct baseline over fixed project-owned synthetic bytes. It does not authorize a base runtime dependency, external repository execution, a holdout, network access during measurement, plug-ins, auto-start, concurrency adapters, subprocess coverage, publication of raw `.coverage` data, a merge blocker, or a coverage-adequacy claim.

## 1. Authoritative evidence reviewed

The review used:

- the exact PyPI release and file metadata for Coverage.py `7.15.2`;
- the exact upstream commit and annotated `7.15.2` tag;
- the exact upstream `LICENSE.txt`;
- the exact upstream publication workflow;
- the Coverage.py `7.15.2` public API documentation;
- exact upstream source where documentation did not fully determine startup or storage behavior.

Primary upstream locations:

- <https://pypi.org/project/coverage/7.15.2/>
- <https://coverage.readthedocs.io/en/latest/api_coverage.html>
- <https://coverage.readthedocs.io/en/latest/api_coveragedata.html>
- <https://coverage.readthedocs.io/en/latest/branch.html>
- <https://github.com/coveragepy/coveragepy/tree/50d865908dfeb21a0bf1e6f05db578c11662f8dd>
- <https://github.com/coveragepy/coveragepy/blob/50d865908dfeb21a0bf1e6f05db578c11662f8dd/LICENSE.txt>
- <https://github.com/coveragepy/coveragepy/blob/50d865908dfeb21a0bf1e6f05db578c11662f8dd/.github/workflows/publish.yml>

## 2. Package and source identity

The exact release metadata records:

```text
package          = coverage
version          = 7.15.2
requires_python  = >=3.10
license          = Apache-2.0
source commit    = 50d865908dfeb21a0bf1e6f05db578c11662f8dd
release tag      = 7.15.2
```

The annotated upstream tag resolves to the reviewed source commit. The reviewed source declares version `7.15.2` and Apache-2.0 licensing.

## 3. Published artifacts

### Selected universal wheel

```text
filename                     = coverage-7.15.2-py3-none-any.whl
sha256                       = eb6bcae8d1a9d305351ecb108232441d11c5cfe9de840a04388ba5d2db8d735c
Trusted Publishing           = true
Sigstore transparency entry  = 2174723144
```

The universal wheel is selected because one exact artifact can be installed across DeltaWitness Python 3.11–3.14 jobs without compiling an extension or selecting interpreter- and platform-specific wheel bytes. The baseline additionally requests the documented `timid=True` tracer so that the research contract uses the simpler Python trace function rather than an optional faster tracer.

### Reviewed but unselected source distribution

```text
filename                     = coverage-7.15.2.tar.gz
sha256                       = 3df60dc267f0a2ca23cb7a9ab1109c62b9335ffbf519fcfe167157c28c09b81d
Trusted Publishing           = true
Sigstore transparency entry  = 2174713616
selected                     = false
```

The source distribution remains recorded because it was the candidate named in issue #43 and is part of the upstream provenance evidence. It is not selected for baseline execution because building it would add build-toolchain and platform variance that is unnecessary for this fixed public-API experiment.

The machine-readable record is:

```text
research/DW-001/coveragepy-7.15.2-artifact.v1.json
```

Its manifest digest is:

```text
28f6430e45fcfda973a1fcd57157e2317f096cc2774e8281244eaf18a9d0dd3f
```

## 4. Dependency boundary

Coverage.py is permitted only as an optional research dependency:

```text
[project.optional-dependencies]
research = ["coverage==7.15.2"]
```

The base package retains:

```text
dependencies = []
```

Importing DeltaWitness, verifying existing artifacts, running the current CLI, building the base wheel, and executing existing DW-001 products must not require or import Coverage.py.

The optional extra communicates scope and version. It does not by itself prove which published artifact was installed. Exact reproduction therefore uses the hashed research requirements file and the explicit artifact verifier rather than treating ordinary resolver output as provenance evidence.

## 5. Clean and offline reproduction strategy

The supported research CI path is:

1. start from a clean Python 3.11, 3.12, 3.13, or 3.14 job;
2. install the DeltaWitness base package without dependencies;
3. download only the universal wheel into a disposable wheelhouse using the hash-locked requirements file;
4. reject every filename or digest other than the selected artifact;
5. install the already verified wheel with `--no-index --no-deps`;
6. run an exact package/version identity smoke;
7. execute measurement without a package-manager or network operation;
8. repeat result generation after force-reinstalling the built DeltaWitness base wheel;
9. compare the stable semantic digest;
10. uninstall Coverage.py and rerun base-product smokes.

Canonical requirements file:

```text
research/requirements-coveragepy-v1.txt
```

The artifact verifier performs no network operation and rejects symbolic links, non-regular files, unexpected filenames, oversized files, and digest mismatches.

## 6. Public API and fixed configuration

The baseline may use only documented public Coverage.py interfaces. The fixed constructor contract is:

```python
coverage.Coverage(
    data_file=None,
    auto_data=False,
    timid=True,
    branch=True,
    config_file=False,
    source_dirs=[explicit_source_directory],
    concurrency=None,
    check_preimported=False,
    context=exact_selector_context,
    messages=False,
    plugins=(),
)
```

The baseline may use documented methods including:

```text
Coverage.collect
Coverage.current
Coverage.get_data
Coverage.analysis2
Coverage.branch_stats
CoverageData.has_arcs
CoverageData.measured_files
CoverageData.measured_contexts
CoverageData.contexts_by_lineno
CoverageData.set_query_context
CoverageData.lines
CoverageData.arcs
```

Names beginning with an underscore are outside the Coverage.py public API and are forbidden in the baseline implementation.

## 7. Ambient configuration, plug-ins, and startup

`config_file=False` disables Coverage.py configuration-file discovery. `plugins=()` fixes an empty programmatic plug-in set. The measurement child uses a reduced environment and rejects active Coverage.py measurement or Coverage-related auto-start variables.

The reviewed wheel installs an `a1_coverage.pth` startup file. Its upstream implementation calls `coverage.process_startup()` only when Coverage auto-start environment variables are present. DeltaWitness does not treat this as harmless ambient state:

- measurement receives no Coverage.py auto-start variables;
- active measurement before baseline construction is rejected;
- ambient `.coveragerc`, `setup.cfg`, and `tox.ini` files are not discovered;
- plug-in registration from tested-repository configuration is forbidden;
- subprocess and concurrency measurement are forbidden.

## 8. Data-file and SQLite behavior

`data_file=None` prevents persistent Coverage.py data-file writes. Coverage.py still uses its SQLite-backed data model internally; in the selected no-disk configuration the database is in memory.

The baseline must never publish a raw `.coverage` database. It extracts only the reviewed bounded relations required by the result contract, then discards the disposable process and directory.

## 9. Privacy boundary

Coverage.py can retain absolute measured filenames, context strings, executed line identities, and arc identities in its data model. These values are treated as sensitive publication metadata even for owned-synthetic work.

The public result may retain only:

- the fixed relative path `src/access.py`;
- fixed public selector and context identities;
- exact source/test/distribution digests;
- executable, executed, missing, context, target, arc, and branch-stat evidence;
- stable diagnostics and finite nonnegative costs.

The result and verifier reject:

- absolute source or data paths;
- raw `.coverage` bytes;
- source or test bodies;
- raw stdout, stderr, or tracebacks;
- usernames, credentials, environment values, and private endpoints.

## 10. Missing optional dependency and identity mismatch

The base package must remain importable and usable without Coverage.py. Research generation with a missing optional package, an active ambient collector, a wrong version, unavailable data, or ambiguous contexts must produce typed indeterminate measurement evidence or fail closed at the provenance boundary. It must never substitute empty measurement for unavailable evidence.

A package/version check is not an attestation of installed file bytes. The exact wheel digest is verified before offline installation by the clean research workflow. The runtime result binds the canonical distribution manifest and records observed package/module version identity, but it does not claim a cryptographic linkage between a loaded module and the pre-install wheel after an adversary can modify the environment.

## 11. Network and execution surface

Coverage.py adds tracing, static source analysis, and an in-memory SQLite data path to the research child. It does not add an authorized network path. The baseline code contains no download, upload, telemetry, remote execution, plug-in, subprocess coverage, or package-manager operation.

The runner is not a sandbox. Fixed project-owned synthetic source and tests remain the only authorized measurement target.

## 12. Decision rationale

`GO` is justified only because:

- one exact upstream release, source commit, license, publication workflow, and published artifact are pinned;
- the selected universal wheel avoids unnecessary native/build variance across the supported Python matrix;
- the base package remains dependency-free;
- ambient configuration, plug-ins, auto-start, concurrency, subprocess coverage, persistent data, and measurement-time network are disabled;
- public APIs expose the statement, arc, branch-stat, and explicit-context evidence needed by issue #43;
- unavailable data can remain indeterminate;
- the output can be reduced to reviewed public-safe relations.

The decision becomes `NO_GO` or `REDESIGN_REQUIRED` if the exact artifact cannot be reproduced, public APIs cannot preserve the required context and missing-versus-empty distinctions, the dependency leaks into the base runtime path, or the baseline requires relaxing the execution or publication boundary.

## 13. Claim boundary

This review establishes only that Coverage.py `7.15.2` is acceptable for one exact optional owned-synthetic research baseline under the recorded controls.

It does not establish:

- Coverage.py adequacy or security;
- authenticity of the loaded runtime after arbitrary environment compromise;
- a DeltaWitness signed-attestation chain;
- containment of tested code;
- safety for external repositories;
- coverage, mutation, or oracle adequacy;
- ecological effectiveness;
- a merge policy, release decision, Gate 0 or Gate 1 completion;
- production readiness or scientific novelty.
