# План пилота и условия запуска

**Предложение:** максимум 12 недель, бюджет до 4,53 млн₽. Это лимит для согласования, не уже одобренный расход. Scope — приоритизация, без автоматического снятия/создания блокировок и без смены РВК.

| Этап | Срок | Неопределённость / работа | Gate / owner |
|---|---|---|---|
| 0. Допуск и capacity | Недели 1–2 | Data-flow approval, права/retention, mandatory M/deadlines, объёмы, source capture, реестр labels | Финмониторинг/ИБ/DPO/Legal/IT подтверждают scope; нет допуска или K/capacity — остановка |
| 1. Guide и data baseline | Недели 2–5 | Cohort inventory, rubric, два эксперта, стартовая вероятностная разметка, SQL features/point-in-time tests | Guide agreement, correct lineage и нет утечки будущего; adjudication budget подтверждён |
| 2. Shadow | Недели 5–8 | Rules+same UI vs peer baseline vs Isolation Forest, 2 000 initial labels, locked test; model outputs не меняют queue | Fallback/replay/restore, test gates и blind yield; нет преимущества — оставить baseline |
| 3. Controlled online | Недели 9–12 | Разрешённый discretionary scope, randomized client-clusters, равные quotas; постоянный probability control | Финмониторинг разрешает ограниченную перестановку, mandatory очередь неизменна; monitoring daily |
| 4. Решение | Конец 12 недели | CI, coverage, source failures, ручные часы, resource costs, harms и экономика | Совместный sign-off sponsor/Finance/комплаенса/ML validation; неоднозначный результат не трактуется как GO |

1200 инженерных ч×2500 =3 млн₽; initial labels880 ч×1000 =0,88 млн; guide0,2 млн;3 месяца infra0,45 млн. Итого 4,53 млн₽ — **подмножество**, а не добавка к полному TCO. Около 1200/12=100 инженерных ч/неделю плюс 880 экспертных часов за пилот; последние требуют оплаченного замещения или отдельного ресурса. Иначе пилот сам ухудшит текущий контроль и не запускается.

## Дизайн сравнения

Замораживаются rules/policy и UI между двумя arms; меняется ranking discretionary cases. Randomization по клиентскому кластеру, stratified segment/risk/сумма; все связанные кейсы одного клиента в одной ветке. Mandatory случаи обрабатываются независимо от ветки и не становятся частью «успеха модели». Нельзя сравнивать model topK со старым месяцем без учёта mix/сезонности.

Probability control1000/месяц — отдельный поток разметки с logged inclusion probabilities для всех существенных страт, в том числе непомеченных. При пересечении с очередью один первичный review учитывается один раз; флаги выборки и веса сохраняются. Reviewers основной очереди видят evidence pack, adjudicators эталона скрытый score/arm. Анализирует независимый validation owner.

Первый месяц даёт prevalence review-worthy и intracluster correlation для power analysis. Нельзя вывести sample size confirmed fraud из 400 эскалаций. Если на locked test мало положительных/широкий CI, статистический gate не выполнен. Допустимо отдельное решение о продлении с бюджетом; без него пилот заканчивается выводом «не доказано».

## Success gates и guardrails

- Lift review-worthy Yield@K ≥20% относительно сильного deterministic baseline, нижняя 95% граница разницы >0; нет существенного ухудшения ключевых сегментов. K одинаков и фиксирован capacity.
- Среднее активное время ≤9 мин с учётом исправлений/допроверки; отдельные percentiles и без cherry-picking лёгких кейсов. Это технический gate, **не** доказательство ROI.
- Нет пропуска mandatory due dates из-за сервиса, потерянных source IDs, действий без сотрудника, утечки данных. Zero tolerance к подтверждённому нарушению этих условий.
- Complaint/reversed-suspension rates по зрелым intervention cohorts: заранее согласованная non-inferiority margin (предложение+2 п.п.), источник и denominator. При широком CI нельзя объявлять отсутствие вреда.
- Probability sample не прекращён, нет скрытого роста oldest backlog. Processing fallback и restore испытаны.
- Экономика: measured hours/costs + отдельно подтверждённый Finance эффект покрывают расходы выбранного горизонта. Если это risk investment без ROI, нужен явный sponsor budget и критерий результата, а не выдуманная прибыль.

Остановка: нарушен hard guardrail; нет допуска/guide/capacity; бюджет/12 недель исчерпаны без доказанного uplift; model не лучше rules+UI; время проверки/abstain делает экономику хуже. Rollback меняет только порядок discretionary queue и bundle; штатный контроль продолжает работать.

Delayed расследования/confirmed findings дозревают после 12 недель: их последующий анализ не продлевает online эксперимент автоматически и не даёт права преждевременно объявить «fraud recall». Учёт и бюджет сопровождения этих исходов входят в steward/ML эксплуатацию либо в отдельно согласованный close-out, если пилот закрыт.
