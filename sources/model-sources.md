# Проверенные источники кандидатов

Не используются публичные leaderboard-оценки как обещание качества в банке.

| Кандидат | Первичный источник | Что подтверждает / что проверяем сами |
|---|---|---|
| Isolation Forest / scikit-learn | [Официальная документация](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) | Алгоритм поиска аномалий; score не вероятность схемы. Проверяем устойчивость и полезность ранжирования |
| PaddleOCR, multilingual recognition / layout | [Официальный репозиторий](https://github.com/PaddlePaddle/PaddleOCR) | Локальный OCR toolkit. Конкретные русские веса, версия, лицензия и hash фиксируются на пилоте |
| Tesseract + rus/eng traineddata | [Официальный репозиторий](https://github.com/tesseract-ocr/tesseract) | Локальный OCR baseline; качество фото/таблиц проверяем отдельно |
| Qwen2.5-7B-Instruct | [Карточка модели](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) | Вариант локального извлечения полей из OCR-текста. Лицензия весов/зависимостей и quantization регрессия входят в допуск |

Выбор Qwen — воспроизводимый кандидат, не заявление о новейшей или лучшей модели. Перед исполнением фиксируют revisions, hashes, SBOM, лицензии и аппаратные требования; скачивание и запуск весов в этой работе не выполнялись. Для флагмана LLM, GPU и retrieval не нужны.
