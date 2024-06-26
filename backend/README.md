# Trinity

Установите все зависимости

```bash
pip install -r requirements.txt
```
или
```bash
pip3 install -r requirements.txt
```

Затем запустите сервер

```bash
flask run
```

Flask будет запущен на локальном сервере по адресу http://127.0.0.1:5000/

## Описание проекта

Проект представляет собой веб-приложение на Flask для анализа и обработки текстовых данных, основанный на различных языковых моделях и инструментах для обработки естественного языка (NLP).

### Основные компоненты проекта:

1. **Flask приложение**
   - Основной серверный компонент, обрабатывающий запросы клиентов.
   - Реализует API для работы с текстами и файлами.

2. **NLP инструменты (spaCy)**
   - Используется для лингвистической обработки текстов.
   - Загружается модель `en_core_web_trf` для обработки текста на английском языке.

3. **Кэширование и хранение данных**
   - Кэширование текстовых данных для ускорения повторных запросов.
   - Директории для хранения кэшей и сохраненных файлов.

4. **Обработка PDF файлов**
   - Чтение текста из PDF файлов с использованием библиотеки `pdfplumber`.
   - Кэширование текстов из PDF файлов для последующего анализа.

5. **Обработка текстовых данных**
   - Очистка текста от различных форматирований и мусорных символов.
   - Применение различных NLP техник для извлечения коллокаций и анализа временных форм предложений.

6. **Перевод коллокаций**
   - Использование API Яндекс.Переводчика для перевода найденных коллокаций.

7. **Анализ временных форм предложений**
   - Поиск предложений с активной формой глагола в разных временных формах.

## Основные функции API

### 1. `/web` - сохранение данных с веб-страницы

- **Метод:** GET
- **Описание:** Сохраняет текстовые данные с веб-страницы в файл.
- **Параметры:**
  - `url`: URL веб-страницы с текстом для сохранения.

### 2. `/collocations` - анализ коллокаций в тексте

- **Метод:** GET
- **Описание:** Ищет коллокации в тексте и их переводы.
- **Заголовки:**
  - `hash`: Хэш файла с текстом.
- **Параметры:**
  - `hash`: Хэш файла с текстом для анализа.

### 3. `/tense` - анализ временных форм предложений

- **Метод:** GET
- **Описание:** Анализирует временные формы предложений в тексте.
- **Параметры:**
  - `tense`: Временная форма для анализа.
- **Заголовки:**
  - `hash`: Хэш файла с текстом.

### 4. `/upload-pdf` - загрузка PDF файлов

- **Метод:** POST
- **Описание:** Загружает PDF файл и сохраняет его содержимое.
- **Формат данных:**
  - Файл в формате PDF.

## Прочие функции и модули

- **Модули:**
  - `collocations.py`: Анализ коллокаций.
  - `tenses.py`: Анализ временных форм предложений.
  - `utils.py`: Вспомогательные функции для работы с данными и текстом.

## Используемые технологии и инструменты

- **Язык программирования:** Python
- **Фреймворк:** Flask
- **NLP библиотека:** spaCy (модель `en_core_web_trf`)
- **API для перевода:** Яндекс.Переводчик
