# Użycie TravelMate AI

## Wymagania

- Python 3.11+
- Klucz API dla wybranego providera LLM (OpenAI, Anthropic, Google lub LM Studio)

## Konfiguracja

1. Wybierz providera modeli w `.env`:
   ```
   MODEL_PROVIDER=openai | anthropic | google | lmstudio
   MODEL_TEMPERATURE=0.3
   ```

2. Uzupełnij klucz API dla wybranego providera:
   - OpenAI: `OPENAI_API_KEY`, `OPENAI_MODEL`
   - Anthropic: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
   - Google: `GOOGLE_API_KEY`, `GOOGLE_MODEL`
   - LM Studio: `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL`, `LMSTUDIO_API_KEY`

3. (Opcjonalnie) Włącz integrację HERE Maps:
   ```
   HERE_API_KEY=...
   HERE_GEOCODE_BASE_URL=https://geocode.search.hereapi.com/v1
   HERE_SEARCH_BASE_URL=https://discover.search.hereapi.com/v1
   ```

4. (Opcjonalnie) Włącz integrację TripAdvisor:
   ```
   TRIPADVISOR_API_KEY=...
   ```

5. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt -e .
   ```

## Uruchomienie

### GUI webowe (rekomendowane)

```bash
python3 -m travelmate.api.main
```

Otwórz `http://127.0.0.1:8000` w przeglądarce.

### CLI

```bash
python3 -m travelmate.cli --input sample_input.json
```

## Interfejs webowy — funkcje

### Zakładka Chat
- Wpisz zapytanie w języku naturalnym (polskim lub angielskim)
- Użyj **quick suggestions** (przyciski pod polem tekstowym) dla szybkiego startu
- **Ctrl+Enter** — skrót klawiszowy do wysłania
- Po wygenerowaniu planu pojawia się przycisk **"Open Interactive Plan"** — otwiera HTML z mapą POI
- Przycisk **"Copy Markdown"** — kopiuje plan do schowka

### Zakładka My Trips
- Lista wszystkich wygenerowanych planów z `output/`
- Kliknij "Open →" aby otworzyć plan w nowej karcie
- Przycisk "Refresh" odświeża listę

### Admin View
- Kliknij przycisk **Admin** w prawym górnym rogu
- Pokazuje statusy agentów w czasie rzeczywistym (IDLE/PROCESSING/DONE/ERROR)
- Log stream z logami pipeline'u
- Debug JSON z outputami każdego agenta

### Dark/Light mode
- Przycisk 🌙/☀️ w prawym górnym rogu
- Preferencja zapisywana w localStorage

### Model status
- W headerze widoczny aktywny provider i model (np. `google · gemini-2.5-flash`)
- Zielona kropka = połączenie aktywne

## Parametry wejściowe

Model `ItineraryInput`:

| Pole | Typ | Opis |
|---|---|---|
| `destination` | string (min. 2 znaki) | Miasto lub region |
| `days` | int (1–14) | Liczba dni |
| `budget` | Low / Mid / Luxury | Poziom budżetu |
| `pace` | Relaxed / Moderate / Intense | Tempo zwiedzania |
| `home_location` | string / null | Miejsce startu (dla transportu) |
| `travel_start_date` | YYYY-MM-DD / null | Data wyjazdu |
| `travel_end_date` | YYYY-MM-DD / null | Data powrotu |
| `participants` | int (1–30) | Liczba uczestników |
| `baggage` | list | Lista bagaży (owner, pieces, wymiary, waga) |
| `interests` | list[string] | Zainteresowania |
| `constraints` | list[string] | Ograniczenia (dieta, dostępność itp.) |
| `accommodation_area` | string / null | Preferowana dzielnica noclegu |

Przykład JSON:
```json
{
  "destination": "Rzym",
  "days": 3,
  "budget": "Mid",
  "pace": "Moderate",
  "home_location": "Kraków",
  "travel_start_date": "2026-07-10",
  "travel_end_date": "2026-07-13",
  "participants": 2,
  "interests": ["historia", "sztuka", "street-food"],
  "constraints": ["wegetariańskie opcje"],
  "accommodation_area": "Trastevere"
}
```

## Format wyjściowy

Każdy run zapisuje w `output/{timestamp}_{destination}_{days}d/`:

| Plik | Zawartość |
|---|---|
| `itinerary.html` | Interaktywny plan z mapą POI (Leaflet) |
| `itinerary.md` | Plan w formacie Markdown |
| `request.json` | Parametry zapytania |
| `token_usage.json` | Zużycie tokenów per agent (input/output/czas) |

## AI Cost & Cache Dashboard

Osobna aplikacja analityczna dostępna po uruchomieniu:
```bash
cd ai-cost-cache-dashboard && ./start.sh
```

Otwórz `http://localhost:5173`. Pokazuje:
- Porównanie kosztów tokenów dla 8 modeli LLM
- Semantic cache showcase z hit/miss visualization
- Automatycznie ładuje nowe runy z `output/`

## Typowe problemy

### `ModelConfigurationError` — brak klucza API
Uzupełnij odpowiedni klucz dla wybranego `MODEL_PROVIDER` w `.env`.

### `ModuleNotFoundError`
Upewnij się że zainstalowałeś zależności: `pip install -r requirements.txt -e .`

### Ostrzeżenia dot. godzin otwarcia
Oczekiwane zachowanie `verification_agent` — model sygnalizuje miejsca wymagające ręcznego potwierdzenia.

### Brak danych HERE (source="unresolved")
HERE nie zwróciło jednoznacznego wyniku dla danego miejsca. Plan jest nadal poprawny, brakuje tylko współrzędnych i adresu.

### Token usage = 0 w token_usage.json
Gemini API może nie zwracać `usage_metadata` w niektórych konfiguracjach. Znany problem, w trakcie naprawy.
