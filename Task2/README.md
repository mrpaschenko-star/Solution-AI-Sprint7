# Task2 — паспорта, данные и решения

| Инициатива | Паспорт по разделам 0–5 | ADR |
|---|---|---|
| №1 Приоритизация финмониторинга | [flagship-passport.md](flagship-passport.md) | [ADR-001](adr/ADR-001-prioritization.md), единый документ с историей v0.1–v1.1 |
| №2 OCR | [ocr-passport.md](ocr-passport.md) | [ADR-002](adr/ADR-002-ocr.md) |
| №18 Извлечение показателей | [extraction-passport.md](extraction-passport.md) | [ADR-003](adr/ADR-003-extraction.md) |

Общие решения: [размещение и допуск данных](placement.md), [выбор модели и приёмочные наборы](model-evaluation.md). Раздел 1 — единая [таблица 18 инициатив](../Task1/initiatives.md); полная постановка тройки также доступна в [Task1](../Task1/formulations.md).

Вердикт готовности всех трёх — **разрыв с планом закрытия**: есть потенциальные источники, но не проверенные корпуса, доступы и приёмочные метки. После выполнения входных gates допускается пилот, а не автоматический production.
