# Деградация на новом сегменте: что проверять и как менять архитектуру

Через три месяца после гипотетического запуска появились селлеры: частые мелкие поступления от платформ, возвраты и расчёты с самозанятыми. «Качество просело» сначала нужно определить: Yield@K, latency, complaint rate, label maturity или только score distribution. По описанию нельзя установить единственную истинную причину; наиболее вероятная рабочая гипотеза — legitimate behavior shift и отсутствие пригодного peer baseline, но её надо отличить от pipeline/selection ошибок.

## Конкурирующие объяснения

| Гипотеза | Что увидим | Дешёвая различающая проверка | Действие при подтверждении |
|---|---|---|---|
| H1 Новый legitimate segment не представлен | Sellers имеют высокий OOD/abstain и низкий expert yield при исправных inputs | 200 случайных sellers +200 matched established clients, blind double-review; frozen feature snapshot, cross-segment comparison | Выделить сегмент, собрать representative history; fallback до сегментной приёмки |
| H2 Изменился профиль сумм/частот/возвратов | Peer distributions отличаются; rule/model reasons концентрируются на нормальной деятельности | Сравнить median/MAD и score on matched inputs, ablation отдельных aggregates, counters/refunds | Сегментные окна/normalizer и feature redesign, не просто снизить глобальный порог |
| H3 Pipeline считает возврат как доход, сменились units/joins | В одном source после релиза скачок признаков; вне sellers тоже ошибки | 50 source-to-feature reconciliation, decimals/timezones, duplicate/late records; replay старым/новым pipeline на одних source rows | Откат feature build/schema и controlled reprocess; retraining ошибку маскирует |
| H4 Незнакомые формулировки назначения платежа | Возможно изменение ручной интерпретации или upstream rule parsing | Feature lineage показывает: raw text **не входит** в ranker. Проверить версию upstream rules и UI/guide отдельно | Не добавлять LLM автоматически; если проблема в upstream parser — его контракт/регрессия |
| H5 Мошенники изменили поведение | Mature confirmed cases меняют pattern даже при стабильной pipeline/segment mix | Раздельно смотреть зрелые расследования и blind probability sample по сопоставимым когортам; не подставлять escalation | Новые экспертные сценарии/признаки; доказательства могут потребовать месяцев |
| H6 Смещение обратной связи/смена разметчиков | Priority reviewed стало больше, control sample уменьшился, agreement упал | Audit inclusion probabilities, quotas, reviewer mix, guide versions; weighted vs unweighted yield | Восстановить sample/guide; старые смещённые метрики пометить непригодными |
| H7 Outcomes не дозрели | В новом сегменте больше открытых расследований и короткое follow-up | Сравнить cohort age/available_at и maturity curves, same observation window | Не обучать на pending как negative, ждать зрелых исходов |
| H8 Capacity/сезонность | Queue age вырос, review стало быстрее/хуже, изменился месячный mix | Сравнить arrival/review/deadline, staffing и concurrent контроль; baseline на том же времени | Ресурс/queue policy; не менять модель для исправления нехватки людей |

400 первичных примеров H1 — диагностический старт, не доказанная мощность для rare confirmed схем. Двойной 12-мин разбор +20% арбитража =176 ч, при proxy1000₽/ч 176 тыс.₽; data/ML диагностика 40 ч×2500=100 тыс.₽. Это **дополнительная** оценка incident response вне baseline TCO; можно заместить плановые sampled reviews при сохранении probabilistic design, либо явно увеличить бюджет. При малом числе положительных результат остаётся неопределённым.

## Порядок расследования

Сначала проверить units/schema/IDs/available_at и source completeness (H3), потому что это быстро и может объяснить весь эффект. Затем maturity/selection/guide (H6/H7), чтобы не чинить модель по неверной метрике. После — matched segment analysis и ablations (H1/H2); H5 требует более длительных исходов. H4 не является прямой причиной изменения model score при неизменных numeric inputs, поскольку текст не входил в модель, но может влиять на правила и ручную оценку.

До диагностики sellers переводятся на existing rules+deadline/age; новая модель не присваивает им автоматически «низкий риск». Mandatory проверки продолжаются. Неповреждённые сегменты могут оставаться на champion при отсутствии общего data дефекта; общий schema defect переводит затронутый input scope на fallback.

## Изменения в архитектуре

| Было в базовом проекте | Что уточняется после инцидента | Владелец |
|---|---|---|
| Feature gate и OOD | **Segment coverage registry**: segment taxonomy version, min history, training date range, data gates, разрешённый model/normalizer bundle; unknown→fallback | ML validation + бизнес |
| Общие freshness/drift панели | Сегментные панели score/coverage/quality/queue, отдельная label maturity view; алерт нового business segment до первого release | Operations + Data |
| Версионированный model bundle | Atomic deployment manifest `(feature schema, segment registry, model, normalizer, policy, test suite)`; worker отвергает несовместимое сочетание | Platform |
| Probability sample | Явное покрытие sellers с logged positive inclusion probability; аллокацию внутри 1000/мес. менять с weights, не silently добавлять workload | Финмониторинг + validation |
| Champion/challenger evaluation | Отдельные сегментные gates и client-cluster rollout; default no auto-promotion | Model governance |

Контролируемая схема: [PNG](diagrams/segment-rollout.png), [PlantUML](diagrams/segment-rollout.puml). Рекомендации не изменяют исторические human decisions; исправленный score — новая версия.

## Регрессионный набор при обновлении

Сохранить locked historical holdout старых сегментов и добавить sellers с real high-frequency legitimate behavior, refunds, self-employed counterparties, cold-start, сезонностью, дроблением/challenge и confirmed cases по maturity. Разделить client/template/time groups, не обучаться на регрессионном наборе. Sampled real data и synthetic challenges считать отдельно.

Обязательные проверки: point-in-time leakage, source-to-feature reconciliation, version/schema mismatch, unknown segment fallback, deadlines/ageing, quota/control allocation, retries/idempotency, restore/rollback, access/egress. Сравнить yield/CI и review time при том же K **по каждому сегменту**, а не скрывать провал селлеров общей средней.

У флагмана нет prompt, поэтому «смена промпта» к нему неприменима. Если позже добавляется text model — это новая постановка и новые TB/допуски. Для №18 prompt/OCR/model update всегда прогоняет OCR-vs-ideal pairs, periods/units/conflicts, evidence и prompt-injection suites из Task2, а не только несколько демонстраций.

## Rollout и rollback

Offline gates → shadow на живых inputs без влияния → canary5% client-clusters sellers →25% →100% только после заранее заданных окна наблюдения/объёма зрелых labels и approval. Проценты — предложения, не календарная гарантия. В каждой фазе сохраняется baseline/control sample и mandatory queue.

Stop: hard safety/contract/deadline failure, неприемлемый segment regression, отсутствие label maturity/power. Вернуть routing manifest на предыдущий **совместимый** bundle; если champion тоже не поддерживает sellers — на deterministic fallback. Проверить actual worker version, cached scores, in-flight jobs и active queue ordering. Существующие human actions не откатываются, новые рекомендации пишутся отдельно. Автоматическое ежедневное переобучение/продвижение не вводится.
