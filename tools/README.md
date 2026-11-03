# Генерация и проверки

Из корня workspace:

```sh
python3 Solution-AI-Sprint7/tools/calculate_tco.py
python3 Solution-AI-Sprint7/tools/calculate_tco.py --check
python3 Solution-AI-Sprint7/tools/render_diagrams.py --java /path/to/java --jar /path/to/plantuml.jar
python3 Solution-AI-Sprint7/tools/validate.py
```

`calculate_tco.py` использует стандартный Python/Decimal, генерирует Markdown-таблицы и проверяет арифметику горизонтов. `--check` не меняет файлы. Внутренние допущения перечислены в [Task4](../Task4/assumptions.md); результаты нельзя считать банковским бюджетом без их согласования.

`render_diagrams.py` сначала проверяет PlantUML syntax, затем генерирует только PNG. Требуются существующие Java и PlantUML; C4-PlantUML включена локально в vendor, сеть/Graphviz не нужны (Smetana). Конфигурация VS Code не изменяется.

`validate.py` использует Pillow для проверки PNG. Проверяет структуру, триаж 1–18, разделы 0–5 паспортов, поля ADR, локальные ссылки/includes, JSON-примеры и воспроизводимость TCO. Качество моделей, законность реальной обработки, нагрузка, ROI и production recovery этими проверками не подтверждаются. PNG дополнительно просматриваются визуально.
