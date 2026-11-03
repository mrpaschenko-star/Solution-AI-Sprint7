# ADR-002. Локальный OCR с проверяемой геометрией и ручной коррекцией

Статус: предварительное. Дата:2026-11-01. Инициатива:№2. [Паспорт](../ocr-passport.md).

## Контекст

Разнородные сканы/фото входят в 90-минутную обработку заявки. Источник истины для текста — оригинал; corpus/volume пока неизвестны.

## Жёсткие ограничения

Банковская тайна/ПДн, допуск DPO/Legal; sandbox файлов; source hash/page provenance; никаких изменений решения по кредиту от сырого OCR.

## Сравнительные критерии

После допуска: numeric/evidence quality50%, correction time25%, стоимость 15%, поддержка/переносимость 10%; все значения предложены, не измерены.

## Рассмотренные варианты

| Вариант | За | Против | Решение |
|---|---|---|---|
| Ручной ввод | Понятный контроль | Время и человеческие ошибки | Baseline/fallback |
| Tesseract rus/eng локально | Простой CPU baseline | Фото/таблицы могут требовать preprocessing | Допущен в benchmark |
| PaddleOCR multilingual/layout локально | Кандидат для сложного layout | Нужно проверить русские веса/лицензии/ресурсы | Основной challenger, не объявлен победителем |
| Public OCR/vision API | Managed serving | Внешний data-flow не допущен | Исключён из real-data pilot до approval |

## Решение

Пилот on-prem,1 200test+300dev страниц; native parser bypass, OCR только для изображения. Prod on-prem versioned selected engine после quality/cost gate; числовые поля подтверждает человек. Hardware выбирается benchmark, автоматическая закупка GPU не предполагается.

## Допущения

| Допущение | Источник | Критично |
|---|---|---|
| Есть репрезентативные оригиналы и доступ | Кейс + inventory | Да |
| Печатный русский/латиница — основной scope | Предложение, согласовать | Да |
| Ручная транскрипция достаточно велика для эффекта | Гипотеза | Да |

## Риски и что с ними делаем

Пропущенные/нечитаемые страницы — completeness gate и review; ложные цифры — numeric audit; вредоносные документы — TB4 sandbox. OCR не подтверждает подлинность.

## План выхода

Хранить originals, neutral token/bbox schema, corrections и test corpus; model engine adapter заменяем. Dual-run на locked set перед сменой, native/manual fallback. Не зависеть от proprietary-only coordinates/export.

## Триггеры пересмотра

Новый язык/рукопись, изменённая лицензия, numeric gate failure, невыгодная correction time, source privacy conditions.

## История

v1.0,2026-11-01 — проектное решение; запуск и измеренное качество не заявлены.
