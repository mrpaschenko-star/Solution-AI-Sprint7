# Угрозы на границах доверия

Номера соответствуют пунктирным рамкам на [C4](README.md). Security controls перечислены здесь, чтобы диаграммы оставались читаемыми. Вложенные зоны — логические trust boundaries, не декларация сертификации.

| Граница | Поток / угроза | Меры и проверка |
|---|---|---|
| **TB1** operational/case systems → analytical service | Лишние ПДн, подмена IDs, утрата provenance, extraction ухудшает OLTP | Allowlist fields, read-only service account, mTLS, namespace, source sequence/hash, quotas; reconciliation counts и negative ACL tests |
| **TB2** UI/человек ↔ review/extraction services | Чужой case, XSS в назначении/документе, несанкционированное действие по model score | SSO/MFA, per-case RBAC/ABAC, HTML escaping/CSP, audit reads/actions, segregation of duties; no action scope у model service |
| **TB3** imported artifacts → registry/runtime | Заражённые веса/pickle/dependency, dynamic remote code, supply-chain rollback | Quarantine import, hashes/SBOM/licence checks, signed approvals, restricted model formats, sandbox loaders, no runtime egress. Pickle/joblib только из доверенной сборки, никогда от клиента |
| **TB4** клиентский файл → intake/sandbox | PDF exploit, zip/decompression bomb, Excel macro/formula injection, hidden text | MIME magic + size/page caps, isolated rendering с CPU/time/memory лимитами, no macros/JS/network, AV, original immutable hash; не открывать CSV формулы в review |
| **TB5** OCR/native context ↔ bounded extraction runtime | Prompt injection, выдуманный evidence URL, чужая заявка в контексте, LLM output как команда | Context allowlist одной заявки, document text только data, no tools/network/secrets; schema + evidence resolver + policy before approval. Prompt alone не считается защитой |

Raw payment purpose — недоверенный текст TB1/TB2, в ranker не поступает, в UI выводится экранированным. OCR ещё не делает текст доверенным; document instructions не могут изменить policy extraction. Model tools для №18 отсутствуют; deterministic orchestration разрешает лишь чтение назначенного контекста и выдачу JSON-кандидатов.

Криптографические ключи/секреты не входят в datasets, prompts, images или logs; production credentials предоставляет банковский secret manager. Логи содержат opaque refs/technical metrics; просмотр evidence — отдельный авторизованный путь. Псевдонимизация не даёт права внешней передачи.

Перед пилотом: data-flow review DPO/Legal/комплаенса, intrusion/ACL tests, backup/restore с permissions, prompt-injection challenge для №18 и malicious-file corpus для №2. Неуспешная атака на тесте не доказывает универсальную безопасность; egress deny и разделение полномочий ограничивают последствия ошибки модели.
