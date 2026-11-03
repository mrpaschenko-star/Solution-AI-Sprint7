# Task3 — архитектура сервисов

| Материал | Содержание |
|---|---|
| [architecture.md](architecture.md) | Контейнеры, компоненты, режим обработки и границы автоматизации |
| [contracts.md](contracts.md) | Выходные контракты всех трёх инициатив и проверки перед действием |
| [reliability-monitoring.md](reliability-monitoring.md) | Очередь, fallback, наблюдаемость, recovery |
| [security.md](security.md) | Угрозы и меры по пронумерованным границам доверия |

| C4 | PNG | Исходник |
|---|---|---|
| Флагман — Container | [PNG](diagrams/flagship-container.png) | [PlantUML](diagrams/flagship-container.puml) |
| Флагман — Component внутри Ranking Worker | [PNG](diagrams/flagship-component.png) | [PlantUML](diagrams/flagship-component.puml) |
| OCR — Container | [PNG](diagrams/ocr-container.png) | [PlantUML](diagrams/ocr-container.puml) |
| Показатели — Container | [PNG](diagrams/extraction-container.png) | [PlantUML](diagrams/extraction-container.puml) |

Пунктирные рамки TB1–TB5 обозначают границы доверия; конкретные угрозы вынесены в таблицу. Схемы показывают проектируемые deployable units, не уже развёрнутую инфраструктуру.
