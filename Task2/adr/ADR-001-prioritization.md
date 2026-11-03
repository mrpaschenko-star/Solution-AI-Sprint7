# ADR-001. Пилот on-prem ранжирования ручной проверки вместо классификатора схем

Статус: **предварительное** — архитектурная рекомендация; банковского approval нет. Дата:2026-11-01. Инициатива:№1. Актуальная редакция:v1.1; история проектных уточнений сохранена ниже.

## Контекст

[Паспорт](../flagship-passport.md):35 тыс. flagged/месяц,10 тыс. reviewed,12 мин,~400 escalated. Последняя метка отражает решение сотрудника, не истину о схеме. Непроверенные операции не являются negatives. Обязанность контроля не исчезает при отказе ML.

## Жёсткие ограничения

Модель не разрешает/блокирует платежи и не отменяет РВК. Не пересылать реальные данные непроверенному обработчику; data use/retention допускают комплаенс/DPO/Legal. Не ухудшать mandatory deadlines. Train/eval point-in-time, запрет будущих исходов в признаках. Human actions и provenance аудируются.

## Сравнительные критерии

После hard gates: полезность при фиксированном review budget40%, надёжность/объяснимость процесса 25%, совокупная стоимость 25%, переносимость 10%. Это предложенные веса принятия решения, не численно измеренные качества кандидатов. При отсутствии статистически доказанного преимущества выбирается простой baseline.

## Рассмотренные варианты

| Вариант | За | Против | Решение |
|---|---|---|---|
| Текущие правила/сумма | Нулевая ML-сложность | Backlog и слабое распределение внимания | Контрольная ветка; улучшить ageing/UI независимо |
| Rules+UI без ML | Объяснимо, дешевле | Может не видеть поведенческие комбинации | Обязательный сильный baseline и возможный конечный результат |
| Unsupervised ranker + policy + человек | Не требует fake fraud labels, проверяемый candidate | Аномальность часто легальна, требует контроля/экспертов | Выбран для условного пилота |
| Supervised на escalation | Быстрые weak labels | Повторяет старый отбор, не классифицирует схемы | Не выбран как fraud classifier; можно исследовать отдельно с честным target |
| LLM по назначениям / public API | Работает с текстом | Не решает labels, добавляет privacy/prompt risks/cost | Не нужен текущему контракту; внешние real-data calls не допущены |
| Cloud self-host / dedicated | Меньше hardware работы | Не закрыты правовые/contract/операторские gates | Только альтернативный costing; не основной маршрут |

## Решение

Пилот: isolated on-prem CPU, baseline и Isolation Forest challenger,2 тыс. initial expert cases с probabilistic отбором, constant full-stream sample; лимит 12 недель/4,53 млн₽. Priority response — anomaly percentile, не вероятность. Schema/feature gates и existing mandatory queue действуют до human action.

Target prod: тот же on-prem путь с HA/monitoring/restore и отдельными согласованными capacity. Выбор final model только по [приёмке](../model-evaluation.md). До положительного pilot/economic gate production не одобряется. Target RPO/RTO из [надёжности](../../Task3/reliability-monitoring.md) — предложения для владельцев, не обещанный SLA.

## Допущения

| Допущение | Источник | Критично |
|---|---|---|
| Есть допустимый capture и capacity on-prem | Проект, требуется inventory | Да |
| Guide даёт согласованную review-worthy метку | Гипотеза; не fraud truth | Да |
| Доступен дополнительный labelling resource | Оценка 880 ч начально и 48 ч/месяц затем | Да |
| −3 мин возможно, стоимость hours/infra разумна | [Допущения TCO](../../Task4/assumptions.md) | Да |

## Риски и что с ними делаем

Selection feedback loop — полный probability sample/weights и blind review. Novel legitimate business — abstain и segment controls. Automation bias — факты/невероятностный score, обучение сотрудников. Lost/duplicate jobs — outbox/idempotency/restore. Неизвестный economic benefit — ограниченный pilot и NO-GO на масштабирование.

## План выхода

Веса/feature code/eval manifests/labels принадлежат банковскому контуру в переносимых форматах; pinned open-source dependencies и signed images. Model adapter заменяем, версия normalizer/policy идёт с bundle. Экспорт datasets/queues в Parquet/JSON с ACL/retention, replay on new runtime, dual-run и сверка, затем switch; старые подписки закрываются после проверки. На exit заложено 500 тыс.₽; это оценка, не универсальная цена vendor lock-in. При невозможности переноса модели вернуть rules+UI, не терять кейсы.

## Триггеры пересмотра

Новый сегмент/OOD, изменённые правила/продукты/источник, зрелый достаточный corpus confirmed findings, новые правовые условия, рост расходов>30%, нарушение quality/guardrails или отсутствие lift. Смена pricing/weight licence требует отдельного review, не автоматической отправки данных в другой API.

## История

Все записи 2026-11-01 — этапы выполнения учебного задания, не реальные approvals.

- **v0.1, Task2 — предварительное размещение:** on-prem для пилота; cloud self-host как возможный target после допуска. Сохранено: внешняя передача не разрешена по умолчанию.
- **v0.2, Task2 — уточнена модель:** предварительная возможность «классификатор на escalation labels» **пересмотрена**: target не является confirmed scheme, selection bias. Выбран unsupervised prioritization и две линии разметки. Cloud target **отложен** до отсутствующих approval/cost evidence; on-prem — базовый target.
- **v0.3, Task3 — архитектура/надёжность:** зафиксированы feature/model/policy gates, case queue, control sample, fallback, trust boundaries и audit; синхронного blocking в платёжном пути нет.
- **v1.0, Task4 — итоговая рекомендация:** TCO24=21,424 млн₽, time-value21 месяц=10,5 млн₽; broad prod **NO-GO**, pilot **условный GO** до 4,53 млн₽. Положительный ROI не доказан; критерии закрытия зафиксированы.
- **v1.1, Task5 — hypothetical post-launch lesson:** добавлены versioned segment coverage registry, label-maturity dashboard и сегментный rollout/fallback. Это реакция на учебное допущение о запуске, не утверждение, что v1.0 GO уже выполнен.
