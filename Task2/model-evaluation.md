# Шортлисты и процедура выбора

Кандидаты сверены с [официальными источниками](../sources/model-sources.md). Версии весов и runtime фиксируются до измерения; смена версии — новый benchmark. Предварительный фаворит не объявляется победителем без корпуса.

## №1: ранжирование

| Кандидат | Допуск / смысл | Выбор и условие |
|---|---|---|
| Rules + сумма/ageing, тот же UI | Не требует fraud labels, сохраняет policy | Обязательный baseline и fallback; может оказаться достаточным |
| Isolation Forest на point-in-time агрегатах | Unsupervised; CPU, score аномалии, не fraud probability | Предпочтительный pilot candidate при проверенной пригодности сегментов |
| Robust peer-group deviations (median/MAD) | Простая воспроизводимая аномальность, мало обучения | Второй baseline; выбирается при сопоставимом yield и меньшем сопровождении |
| Supervised boosting / learning-to-rank | Возможен позже для review-worthy с unbiased evaluation | Не допущен сейчас к «схема/не схема»: нет зрелых labels. Weak escalation labels могут исследоваться только как имитация старой policy |
| LLM по назначениям платежей | Добавляет недоверенный текст/стоимость, не решает отсутствие labels | Не включён; retrieval, prompts, fine-tuning не нужны текущему контракту |

Стартовая разметка 2 000: 1 000 flagged +1 000 unflagged случайно внутри известных страт. Guide измеряет `review_worthy`, uncertainty и evidence. Разметчики не видят score/ветку эксперимента. Gate согласованности: Cohen κ ≥0,7 и positive agreement ≥0,8 как предложения; при редком классе κ оценивается вместе с prevalence/матрицей расхождений. Если gate провален — править guide, не тренировать «более сильную модель».

Из 2 000 выделить 500 dev, 1 500 locked test по времени и клиентским группам; исходные вероятности и cluster IDs сохраняются. Эта выборка **может оказаться недостаточной**: при доле 1% ожидаются лишь ~15 положительных в test. Ноль находок не доказывает безопасность. На первом месяце оценивается variance для расчёта мощности; для rare confirmed endpoints пилот не заявляет статистическую победу.

Предлагаемый temporal design: fit на шести месяцах до T0, dev на следующем месяце, locked test на последующем периоде с доступными на момент операции признаками. Внутри dev/test отбор случайный по стратам; выборочный вес относится к соответствующему периоду, а не ко всей истории банка. Scaler, percentile reference, feature selection и гиперпараметры не подгоняются на test, даже при обучении без учителя. Дополнительный client-group holdout исключает этих клиентов из fit целиком; их прошлую историю можно использовать только для вычисления доступных тогда признаков. Temporal и unseen-client результаты показываются раздельно. Точные календарные границы фиксируются после inventory, а не выбираются по полученному score.

Приёмочные сценарии: типичный established client, small business/ИП, cold-start, разные суммы/каналы, дробление в окнах, legal high-frequency activity, missing/stale features, новые сегменты, поздние correction, duplicate delivery. Edge fixtures синтетические, отдельно от случайного набора: 50 на сценарий missing/stale/duplicates/cold-start/schema mismatch (250), без включения в оценку prevalence. Установленные ранее findings — challenge-набор с датой знания, не оценка recall полного потока.

Выбор: после hard gates сравнить Yield@K, review time, stability и стоимость. Lift цель ≥20% relative; paired/client-cluster bootstrap 95% CI разницы должен исключать 0. Если CI широк — «не доказано», а не «успех»; продлевать сбор только в заранее разрешённом бюджете. OOD/missing cases обязаны попадать в fallback с сохранением due date. Ни anomaly percentile, ни weak labels не калибруются в вероятность схемы; рабочая точка — quota K и abstention policy.

## №2: OCR

Tesseract rus/eng — baseline; PaddleOCR multilingual recognition + layout — challenger. Native text extractor bypass для валидных born-digital документов. General vision LLM не выбирается вместо OCR: нельзя восстанавливать отсутствующие цифры по правдоподобию. Corpus/gates — [паспорт](ocr-passport.md), 1 200 test страниц и 300 dev. Для каждой страты bootstrap по документам; numeric tokens не считать независимыми страницами.

На clean/photo/table сценариях измеряются CER, numeric exact, omission, abstain, latency и correction time. На unreadable/malformed ожидается review/reject, а не красивый текст. Провал numeric gate исключает автоматическое принятие этой страты; если ручной review не даёт экономии — остаётся ручной процесс. Выбирается самый дешёвый допустимый pipeline, не модель с минимальным CER на удобной части.

## №18: показатели

1. Parser/regex/native cells + ручной длинный хвост — baseline.
2. Parser + локальный Qwen2.5-7B-Instruct с JSON grammar и evidence IDs — основной challenger.
3. Тот же candidate с quantization — отдельная конфигурация, только после проверки numeric regression. Более крупная модель — новый cost/quality эксперимент, не автоматический fallback.

600 test +150 dev пакетов, страты в [паспорте](extraction-passport.md); минимум 3 000 полей теста не означает независимые 3 000 заявок. Test хранится отдельно от prompts/dev examples; клиентов и близкие templates держать в одном split. Две дорожки: идеальная транскрипция и реальный OCR, чтобы локализовать ошибку. Challenge: неверная единица/период, конфликт версий, пустое поле, текст «игнорируй правила», URL/exfil instructions, невидимый text layer.

Нет evidence/невалидная схема/противоречие → abstain/review. Любая попытка выполнить инструкцию из документа или сгенерировать критичное число без источника блокирует выпуск версии. Fine-tuning не применяется до доказательства, что ошибка именно semantic extraction и её нельзя устранить parser/контекстом; нужен отдельный разрешённый training corpus.

## Общие правила приёмки

Пороги — проектные предложения: финмониторинг/андеррайтинг утверждают цену ошибок и минимальный эффект; ИБ — hard security gates. В отчёте обязательны denominator, coverage, confidence intervals, стоимость и ручной workload. Ни один кандидат в этой работе не обучен/не измерен; результаты не подменяются паспортными обещаниями.
