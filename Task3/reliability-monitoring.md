# Надёжность, очередь человека и мониторинг

## Delivery и recovery

At-least-once capture/jobs: source commit checkpoint продвигается после durable persistence; transactional outbox + unique keys обеспечивают идемпотентный эффект. Worker ACK — после сохранения результата. Lease expires → повтор без потери case; poison jobs после трёх попыток уходят в DLQ и alert. Backoff 1/5/15 минут с jitter — предложение; повтор не переписывает business deadlines. Backlog monitor не ждёт исчерпания retry для mandatory дела.

PostgreSQL HA/fencing, broker quorum в независимых failure domains, резервные копии и tested restore. Proposed RPO ≤15 мин для восстановимых features/recommendations; для принятого review/action audit — отсутствие потерь acknowledged writes в пределах оговорённого single-node failure через sync replica. Site disaster требует отдельного согласования RPO. RTO recommendation service ≤4 ч, но deterministic queue доступна независимо от модели. При общей недоступности UI действует существующий bank continuity runbook, а не новая неподтверждённая гарантия.

## Наблюдаемый fallback

| Сигнал | Действие | Кто получает уведомление |
|---|---|---|
| Required feature missing или age >30 мин | Не ранжировать моделью, existing rules+deadline/age | Data on-call; кейс остаётся видимым |
| Истории <30 дней / неизвестный сегмент / out-of-range cohort | Abstain, dedicated manual lane в рамках общей capacity; sample для оценки | ML validation + финмониторинг |
| Percentile около quota cutoff (например ±0,02) | Tie-break по age; не объявлять высокую уверенность | Аудит распределения, без тревоги на каждый кейс |
| Low score против mandatory rule | Rule wins; due date неизменен | Policy owner при систематическом расхождении |
| Model/feature service unavailable, invalid schema/NaN, превышение лимита batch | Deterministic fallback без ожидания ML; circuit breaker после 5 ошибок подряд, half-open probe через 5 мин | Operations; thresholds — предложения для настройки |
| OCR unreadable/omitted page, extraction без evidence/конфликт | Human review; показать оригинал и проблемное поле | Андеррайтинг |
| Недоступен внешний source signal | Mark signal stale/unknown, policy по РВК; не считать отсутствие сигнала «низким риском» | Комплаенс + source owner |

## Матрица мониторинга

| Уровень | Метрики и срезы | Предлагаемый триггер / реакция |
|---|---|---|
| Вход | Count/lag по source, missingness, schema, duplicate rate; feature distributions по segment/tenure/channel | Missing required >1% за 2 batch или lag >30 мин → затронутый scope на fallback; расследовать pipeline |
| Модель | Score quantiles, OOD/abstain, input drift, version skew | PSI >0,2 как diagnostic trigger, не доказательство падения качества; проверка shift/contract прежде retrain |
| Очередь | Mandatory deadlines, oldest/p95 age, M/K/control slots, arrived/reviewed, backpressure, segment share | Любой due breach из-за reorder → остановить online reorder; sample capacity нарушена → остановить эксперимент |
| Человек | Review minutes, disagreement, override, label lag, blind quality sample, workloads | Guide agreement ниже gate → заморозить promotion/переобучение и пересогласовать guide |
| Бизнес | Review-worthy yield/CI, cohort time-to-review, расследования/confirmed отдельно, complaints/client impacts | Недоказанный lift → не расширять; attributable wrongful block/data exposure → немедленно остановить ветку |
| Документы | CER/numeric exact на audit, evidence precision, conflict detection, coverage, correction time | Не прошла схема/источник → review; critical wrong number в accepted path → rollback версии |

Guardrails жалоб/снятых приостановок: кейсовые 120/600 и 450/600 — исходные месячные counts, не готовые causal rates. В пилоте фиксируют denominator вмешательств, cohort и maturity window, сравнивают с concurrent control. Предлагаемая non-inferiority margin +2 п.п. требует утверждения комплаенса; при слишком широком CI gate не считается доказанным. Абсолютное число приостановок модель не должна увеличивать автоматически вообще.

Очередь растёт на 25 тыс. flagged/месяц уже сейчас. Даже сокращение разбора с 12 до 9 минут при прежних 2 000 ч/месяц даёт примерно 13 333 review, а не 35 000. Ranker улучшает использование ресурса, но не решает capacity gap. Руководитель финмониторинга отдельно утверждает дополнительный ресурс/изменение процесса; вытеснение старых кейсов маскирующим фильтром запрещено.

Пересчёт признаков/score не снимает existing human decision. Rollback модели возвращает signed предыдущий bundle, соответствующие schema/normalizer/policy; новые версии не перезаписывают историю. Подробный сценарий нового сегмента — [Task5](../Task5/degradation.md).
