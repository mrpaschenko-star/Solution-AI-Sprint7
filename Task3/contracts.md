# Выходные контракты и проверки

Примеры синтетические. Версии контрактов и schema validation предшествуют записи recommendation; URL от модели не открываются. Используются source IDs, которые сервер сам разрешает по ACL.

## №1 — Recommendation v1

```json
{
  "schema_version": "1.0",
  "recommendation_id": "rec-demo-001",
  "operation_ref": {"source": "rb-core", "id": "op-demo-1"},
  "case_id": "case-demo-1",
  "as_of": "2026-11-01T10:00:00Z",
  "generated_at": "2026-11-01T10:08:00Z",
  "feature_snapshot_id": "fs-demo-1",
  "feature_schema_version": "f1",
  "model_version": "iforest-candidate-1",
  "policy_version": "queue-1",
  "segment_id": "sme-established",
  "status": "ranked",
  "score": {"kind": "anomaly_percentile", "value": 0.91},
  "reason_codes": ["HIGH_TRANSIT_RATIO_7D"],
  "evidence_refs": ["fact-demo-1"],
  "data_quality": {"missing_required": [], "max_feature_age_seconds": 480},
  "fallback_reason": null,
  "action": "recommend_review_order_only"
}
```

Обязательны все поля, включая nulls. Допустимые status: `ranked`, `abstained`, `fallback`; score допускает null только в двух последних случаях. Percentile конечен и в [0,1], **не** fraud confidence. Внешние URL, HTML и свободная инструкция не входят в контракт. `fallback_reason` — enum: MISSING_FEATURES, STALE_FEATURES, COLD_START, OOD_SEGMENT, RULE_CONFLICT, MODEL_UNAVAILABLE, INVALID_OUTPUT, CAPACITY_LIMIT. Missing/invalid status не принимается.

Сервер проверяет: source operation существует и принадлежит доступному scope, feature cutoff ≤as_of, обязательные поля свежи по feature contract, evidence соответствует snapshot, bundle signed/approved, отсутствуют NaN/Inf и неизвестные enum. Ошибка → quarantine с техническим кодом + обычный deterministic queue path. Никаких команд `block`/`allow` в payload; due date, mandatory flag, control assignment устанавливает отдельная policy из authoritative источника.

Человек выбирает действие в case workflow с собственной ролью и обоснованием. Сохраняются reviewer, event_time, label_version, available_at, evidence и policy; исходы `escalated`, `investigation_closed_*`, `confirmed_*` раздельны. Исправление label — новая версия, не overwrite. Idempotency бизнес-действия задаёт case system, а не model recommendation ID.

## №2 — OCRResult v1

Обязательные поля: `document_id`, `document_sha256`, `version`, `page_id`, `page_count`, `engine_version`, `status`, `tokens[]`, `warnings[]`. Token: `text`, `bbox[x1,y1,x2,y2]` в нормированных координатах [0,1], `engine_confidence`, `source_page_ref`. `unreadable` не содержит выдуманного текста, reviewer correction хранится отдельно.

Проверки: полное число страниц, geometry bounds/order, лимиты длины, валидный Unicode, исходный hash и tenant/application ACL; confidence сравнивается только внутри выбранной версии engine. Метрика low CER не отменяет верификацию критичных цифр. Чтение embedded instruction/URL ничего не исполняет.

## №18 — FinancialFields v1

```json
{
  "schema_version": "1.0",
  "application_id": "app-demo-1",
  "model_version": "local-extractor-candidate",
  "context_manifest_id": "ctx-demo-1",
  "status": "needs_review",
  "fields": [{
    "metric_code": "REVENUE",
    "value_decimal": "1250000.00",
    "currency": "RUB",
    "source_scale": "THOUSAND",
    "period": {"from": "2025-01-01", "to": "2025-12-31"},
    "source_value": "1250",
    "evidence": {"document_id": "doc-demo-1", "page": 2, "token_ids": ["t1", "t2"]},
    "status": "candidate"
  }],
  "conflicts": [],
  "human_approval": null
}
```

`value_decimal` — строка с точным decimal в базовой валютной единице, **пересчёт из source_value/scale делает код**, не доверяется арифметике LLM. `source_scale`/currency/period обязательны; неизвестное null + `missing`/`unreadable`, не zero. Conflicting documents сохраняют несколько кандидатов, без автоусреднения. LLM предлагает fields, а server добавляет trusted context/model IDs и проверяет scope.

Перед business use: JSON/schema/type/size → source hash/ACL/evidence token match → metric allowlist → decimal parsing/scale/currency/period → cross-document conflict → арифметические identity checks там, где применимы → ручной sign-off. Schema-valid JSON сам по себе не доказывает корректность. Approved values публикует отдельный application service с least-privilege grant; model runtime не имеет write credentials.
