# Architecture

```mermaid
flowchart LR
  U[Untrusted CSV/JSON] --> V[Validation]
  V --> N[Normalization/Reconciliation]
  P[Versioned YAML policy] --> E[Eligibility/Segmentation/Ask]
  N --> E
  E --> F[Approved FactBundle]
  F --> L[DraftingModel]
  L --> R[Controlled Jinja renderer]
  R --> O[Output validation]
  O --> B[Atomic batch state + review queue]
```

```mermaid
sequenceDiagram
  participant B as Batch
  participant P as Policy engine
  participant L as LLM adapter
  participant V as Validator
  B->>P: typed normalized donor
  P-->>B: eligibility, segment, exact ask, claims
  alt suppressed
    B-->>B: persist reason; never call LLM
  else eligible
    B->>L: bounded FactBundle
    L-->>B: NarrativeDraft only
    B->>V: escaped templates + exact ask/claims
    V-->>B: review-required result
  end
```

```mermaid
stateDiagram-v2
  [*] --> created
  created --> running
  running --> running: atomic donor result
  running --> completed
  running --> completed_with_errors
  running --> running: resume skips idempotency keys
```

```mermaid
flowchart TB
  subgraph Untrusted
    A[Uploads]
    M[Model prose]
  end
  subgraph Trusted deterministic boundary
    T[Typed models]
    P[Policy/calculators]
    X[Escape + validators]
  end
  subgraph Human boundary
    Q[Review queue]
    H[Authorized reviewer]
  end
  A --> T --> P --> M --> X --> Q --> H
```

Modules own one concern; templates contain no policy logic, prompts contain no arithmetic, and no global mutable business state exists. The provider boundary is replaceable and production behavior does not depend on the fake.

