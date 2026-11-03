# Архитектура: модель рекомендует, банк принимает решение

## Флагман: Container и Component

Сервис работает **после фиксации операции**, вне синхронного проведения платежа. Существующие обязательные AML-процедуры и их real-time части сохраняются. Модель не снимает флаг, не выпускает платёж и не вводит блокировку; отдельный штатный workflow с полномочиями сотрудника выполняет клиентское действие.

Создание кейса не зависит от успешного scoring: Capture регистрирует flagged/control anchor и исходные deadlines в Case Store до запуска модели. Рекомендация лишь дополняет уже доступный baseline case. Снимок признаков сохраняется отдельно; затем одна транзакция Case Store фиксирует case/version reference и job outbox. Повтор после сбоя между этими шагами безопасен по unique source key; recovery reconciliation находит незавершённые захваты. Без готовых признаков кейс сразу доступен по rules/age, а model job не требуется для его ручной проверки.

| Контейнер / владелец | Ответственность | Почему отдельный / что не делает |
|---|---|---|
| Capture & Feature Builder / data engineering | Разрешённый incremental export/CDC с checkpoints, schema/DQ, point-in-time SQL windows, quota snapshots | Изолирует source нагрузку; без full BI scan live Core. Работа на аналитической копии |
| Analytical Store / platform | PostgreSQL partitions для recent features/case refs; object store для разрешённых input snapshots, dataset manifests и audit | Один feature owner, shared infra как управляемый ресурс; не новый ledger и не полная копия истории навсегда |
| Job Queue / platform | Durable pending jobs, retry/lease/DLQ; выбран RabbitMQ, transactional outbox публикации | Не Kafka только ради 35 тыс. flagged; существующий поддерживаемый broker может заменить после fit-gap |
| Ranking Worker / ML team | Stateless scoring по pinned features/model, normalisation, policy validation, result outbox | CPU model library внутри worker; отдельный network inference server не нужен |
| Review API & UI / финмониторинг | Queue merge: mandatory/deadline → control slots → discretionary ranking/ageing, human outcomes, audit | UI показывает факты/версии, не вероятностный юридический вердикт. Claims/leases предотвращают двойной разбор |
| Case Store / platform + финмониторинг | Unique anchor IDs, state/leases/deadlines, approved action refs, outcomes и sampling probabilities | PostgreSQL HA; это очередь и evidence, исходная финансовая запись остаётся в Core |
| Training & Evaluation / ML validation | Versioned datasets, independent test, segmented metrics, champion/challenger; blind labeling exports | Offline; не делает автоматический promotion по агрегатной метрике |
| Model Registry / platform | Signed bundle: weights, scaler/schema, supported segments, dataset lineage, policy compatibility | Импорт через TB3, approval и откат; никакой dynamic download из worker |
| Monitoring / operations | Input/feature/queue/quality/business metrics и alerts, отдельный доступ к sensitive evidence | Метрики без ПДн; links в защищённый case store |

### Компоненты Ranking Worker

1. **Job intake/idempotency**: `(source_system, operation_id, as_of, feature_version, model_version, policy_version)`; повтор возвращает тот же результат. Новая версия даёт отдельную recommendation, не повторное клиентское действие.
2. **Feature gate**: проверяет age/completeness/schema/cold-start/segment coverage; при провале сразу fallback.
3. **Model adapter**: CPU Isolation Forest либо approved baseline. Не читает raw payment text, не имеет внешних tools.
4. **Score normalizer**: reference-distribution percentile по допустимому сегменту. Это не вероятность; при недостаточном reference cohort — abstain.
5. **Policy validator**: mandatory rules имеют приоритет; проверяет finite/range, source links, поддержанный bundle, abstention и proposal metadata. Выход worker не может менять due date.
6. **Evidence & result writer**: формирует проверяемые reason codes из SQL facts (например, transit ratio/window), сохраняет recommendation/outbox. Reason codes не выдаются за причинное объяснение модели.

Calibration в вероятность схемы отсутствует: нужного эталона нет. Boundary около quota cutoff трактуется как tie/uncertainty: deterministic age order, а не сверхточный бинарный порог. Model score согласуется с правилами через policy; конфликт «модель низко, mandatory rule высоко» всегда оставляет mandatory priority.

## Нагрузка и режим

20–25 млн операций в 30-дневный месяц — примерно 7,7–9,6 операций/с **в среднем**, не peak benchmark. Raw flow нужен для оконных признаков; ranker обслуживает 35 тыс. flagged/месяц плюс максимум 1 тыс. sample-кейсов. Batch каждые 15 минут; fallback не ждёт следующего успешного batch, а сохраняет доступность текущей case queue.

Нужно измерить пики, join cardinality, размер строк и recovery catch-up. Исходная оценка capacity: 64 vCPU /256 GiB суммарно, allocation на workers, SQL и staging; это ценовой сценарий, не доказательство достаточности. Пример резерва: 2 feature VM 16/64, 2 DB VM 8/32, 2 worker/API VM 4/16, 1 evaluation VM 8/32; broker/monitoring пользуются выделенными квотами общей платформы. Диски/реплики/backup и общий platform charge включаются в инфраструктурный бюджет, уточняются DBA.

## Документные инициативы

№2: intake с document version и hash → AV/sandbox/native parse → OCR Worker → OCR Store → review. Модель читает только безопасно отрендеренные страницы, не исполняет Excel/macros/embedded JS. OCR Store сохраняет token geometry, raw engine confidence, исправления и source hash. Текстовый слой PDF сверяется с изображением на противоречия; сомнительный слой не становится доверенным входом.

№18: Orchestrator получает только текущую заявку; Context Selector берёт relevant pages/таблицы по разрешённым metric definitions. Для известных cells работает parser. Для длинного хвоста локальный LLM получает delimiters, словарь и evidence IDs; JSON grammar с ограничением размера. Это bounded extraction, не агент: нет shell, браузера, payment/credit tools. Проверки единиц/периодов/арифметики и evidence выполняет обычный код; UI требует подтверждения андеррайтера.

Коэффициенты рассчитываются из подтверждённых полей детерминированно. Противоречия документов не разрешаются выбором «более правдоподобного» числа. Fine-tuning, external RAG и свободная генерация не нужны начальной постановке. OCR/№18 могут переиспользовать intake/storage/review, но модели и контракты версионируются отдельно.
