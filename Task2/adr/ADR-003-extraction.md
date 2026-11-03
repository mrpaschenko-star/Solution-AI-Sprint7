# ADR-003. Извлечение полей с evidence, без автономного кредитного решения

Статус: предварительное. Дата:2026-11-01. Инициатива:№18. [Паспорт](../extraction-passport.md).

## Контекст

Неоднородные документы требуют сопоставления показателей/периодов. Ввод на основе OCR может переносить его ошибки; тот же пакет может реально противоречить сам себе.

## Жёсткие ограничения

Только документы текущей заявки; допускаемые DPO/Legal цели; no tools/network/write credentials у модели; source evidence и human sign-off до использования критичных полей.

## Сравнительные критерии

После hard gates: tuple/evidence correctness50%, review time20%, cost20%, portability10%. Сначала accuracy/coverage trade-off, затем стоимость допустимых конфигураций.

## Рассмотренные варианты

| Вариант | За | Против | Решение |
|---|---|---|---|
| Parser/regex + человек | Детерминированность, низкая цена известных шаблонов | Длинный хвост ручной | Обязательный baseline и первичный путь |
| Parser + self-host Qwen2.5-7B-Instruct | Semantic mapping для новых заголовков | Hallucination/контекст/аппаратные затраты | Challenger с constrained schema/evidence, только после benchmark |
| Fine-tune сразу | Возможна специализация | Нет доказанного error source и разрешённого train corpus | Отложить |
| Public LLM / агент с инструментами | Быстрое prototype, гибкость | Не пройдены data-flow gates; лишние полномочия | Исключён из текущего пилота |

## Решение

Пилот on-prem text-only bounded extraction на 600test+150dev пакетов. Parser первым; candidate model только длинный хвост, вычисления кодом. Отдельно тест ideal transcription/real OCR. Target prod — тот же раздельный contract, on-prem serving после license/security/capacity gates; не выбран без замера победитель или GPU конфигурация.

## Допущения

| Допущение | Источник | Критично |
|---|---|---|
| Словарь показателей можно согласовать | Предложение андеррайтингу | Да |
| Документы позволяют установить эталон/abstain | Кейс + profiling | Да |
| Challenger даёт выигрыш поверх parser | Проверяемая гипотеза | Да |

## Риски и что с ними делаем

Неверная единица/период — validators и source highlight; prompt injection — TB5 isolation/no tools; чужой клиент — scope ACL; конфликт — manual, не усреднение. Эффект не складывается повторно с OCR.

## План выхода

Версионированные JSON metric/evidence contracts, prompts, snapshots и test corpus; локальные веса/engine adapter заменяем. Сначала regression и shadow, затем ограниченный canary. При провале вернуть parser+manual без потери приложенных документов.

## Триггеры пересмотра

Precision/evidence failure, новый набор показателей/форматов, cost gate, новая модель/OCR версия, изменение прав/лицензии. Retrieval/fine-tuning добавляются только после изолированного эксперимента.

## История

v1.0,2026-11-01 — предварительный локальный hybrid, финальное решение зависит от проверки.
