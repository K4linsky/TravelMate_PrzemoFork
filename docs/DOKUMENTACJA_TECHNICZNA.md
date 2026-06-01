# Dokumentacja techniczna — TravelMate AI

> Dokument opisuje aktualną implementację POC. Architektura produkcyjna opisana jest w `ARCHITEKTURA_PRODUKCYJNA.md` i `IMPLEMENTACJA_TECHNICZNA.md`.

## 1. Przegląd systemu

TravelMate AI to aplikacja Python wykorzystująca multi-agent workflow oparty o LangGraph.

Tryby uruchomienia:
- **GUI webowe** (rekomendowane): `python3 -m travelmate.api.main` → `http://127.0.0.1:8000`
- **CLI**: `python3 -m travelmate.cli --input sample_input.json`

## 2. Architektura logiczna

### 2.1 Warstwy

- `travelmate/web/` — frontend (Tailwind CSS + PWA, dark/light mode, My Trips tab)
- `travelmate/api/` — backend (FastAPI + WebSocket streaming)
- `travelmate/services/` — logika aplikacyjna (parse → plan → zapis → dashboard push)
- `travelmate/agents/` — 6 agentów pipeline'u
- `travelmate/prompts/` — prompty systemowe i zadaniowe per agent
- `travelmate/tools/` — narzędzia wspólne
- `travelmate/models.py` — kontrakty danych i typy stanu
- `ai-cost-cache-dashboard/` — osobna aplikacja analityczna (React + FastAPI)

### 2.2 Graf przetwarzania (LangGraph) — aktualny

```
START
  ├──► profile_agent   ┐ (równolegle)
  └──► transport_agent ┘
           │
         fan_in
           │
       geo_agent
           │
    itinerary_agent
           │
   verification_agent
           │
     formatter_agent
           │
          END
```

`profile_agent` i `transport_agent` działają równolegle — oszczędność ~2-4s per run.

## 3. Komponenty i odpowiedzialności

### 3.1 `PlannerService` (`travelmate/services/planner_service.py`)

- Parsuje wejście użytkownika (JSON / key-value / język naturalny via LLM)
- Resetuje `token_tracker` przed każdym runem
- Uruchamia graf agentów
- Zbiera `token_usage` po zakończeniu pipeline'u
- Zapisuje wyniki do `output/{run_id}/` (html, md, json, token_usage.json)
- Asynchronicznie pushuje run do AI Cost & Cache Dashboard (fire-and-forget)

### 3.2 Parser wejścia (`travelmate/tools/input_parser.py`)

Obsługiwane formaty:
1. JSON (wykrywany przez `{` na początku)
2. `key: value` (heurystyka — min. 4 pary, 80% linii)
3. Język naturalny (NLP parser via LLM z `with_structured_output`)

Domyślne wartości przy brakujących polach: `days=3`, `budget=Mid`, `pace=Moderate`, `participants=1`.

### 3.3 Agenci

| Agent | Krok | Wejście | Wyjście |
|---|---|---|---|
| `profile_agent` | 1 (równolegle) | ItineraryInput | profile_summary |
| `transport_agent` | 1 (równolegle) | ItineraryInput + profile | transport_report |
| `geo_agent` | 2 | request + profile + HERE context | GeoOutput (z HERE + TripAdvisor) |
| `itinerary_agent` | 3 | compact_geo + profile | ItineraryDraft |
| `verification_agent` | 4 | itinerary + geo + request | VerificationOutput |
| `formatter_agent` | 5 | wszystkie outputy | final_markdown |

Każdy agent po `llm.invoke()` wywołuje `get_tracker().record(agent_name, response, elapsed_seconds)`.

### 3.4 Token Tracker (`travelmate/tools/token_tracker.py`)

Thread-safe singleton. Obsługuje formaty usage_metadata dla:
- OpenAI (`token_usage.prompt_tokens` / `completion_tokens`)
- Anthropic (`usage.input_tokens` / `output_tokens`)
- Google Gemini (`usageMetadata.promptTokenCount` / `candidatesTokenCount`)

Zapisuje per agent: `input_tokens`, `output_tokens`, `total_tokens`, `elapsed_seconds`.

### 3.5 Model factory (`travelmate/tools/model_factory.py`)

`get_chat_model(model_id=None)`:
- Bez `model_id` — używa domyślnego z `.env`
- Z `model_id` — inicjalizuje konkretny model (przygotowane pod dynamiczny routing)

`get_model_runtime_status()` — zwraca provider, model, flagę aktywności, diagnostykę.

### 3.6 Dashboard Push (`travelmate/tools/dashboard_push.py`)

Po każdym zakończonym runie wysyła POST do `http://localhost:8001/api/runs/notify` z:
- `run_id`, `request_json`, `itinerary_md`, `token_usage`

Działa w tle (daemon thread) — nie blokuje odpowiedzi użytkownika. Jeśli dashboard nie działa — błąd jest logowany na poziomie DEBUG i ignorowany.

## 4. Modele danych

Kluczowe kontrakty (`travelmate/models.py`):

- `ItineraryInput` — wejście biznesowe (destination, days, budget, pace, interests, constraints...)
- `GeoOutput` — wynik warstwy geograficznej (mobility_strategy + days z morning/afternoon/evening zone)
- `GeoPlace` — szczegóły miejsca (name, coordinates, address, website, tripadvisor_*)
- `ItineraryDraft` — strukturalny plan (days z activities, meals, lodging)
- `VerificationOutput` — ostrzeżenia i korekty
- `PlannerState` — TypedDict z wszystkimi polami stanu LangGraph

## 5. API Endpoints

| Endpoint | Metoda | Opis |
|---|---|---|
| `/` | GET | Główny interfejs webowy |
| `/health` | GET | Status: provider, model, active, message |
| `/chat` | POST | Wysłanie zapytania, uruchomienie pipeline'u |
| `/admin/logs` | WebSocket | Streaming logów i statusów agentów |
| `/trips` | GET | Lista wszystkich runów z `output/` |
| `/trips/{id}/html` | GET | Serwowanie wygenerowanego HTML |
| `/manifest.json` | GET | PWA manifest |
| `/service-worker.js` | GET | PWA service worker |

## 6. Interfejs użytkownika

### 6.1 Web (Tailwind + FastAPI + PWA)

Pliki: `travelmate/web/index.html`, `travelmate/api/main.py`

Funkcje:
- **Chat tab** — chatowy interfejs, quick suggestions, Ctrl+Enter, typing indicator, progress bar z agentami
- **My Trips tab** — lista wszystkich wygenerowanych planów, otwieranie jednym kliknięciem
- **Admin View** — statusy agentów (IDLE/PROCESSING/DONE/ERROR), log stream, debug JSON
- **Dark/Light mode** — toggle z zapisem w localStorage
- **Model status** — provider i model w headerze
- **"Open Interactive Plan"** — przycisk po wygenerowaniu planu
- **"Copy Markdown"** — kopiowanie do schowka
- **PWA** — manifest + service worker, instalacja jako aplikacja

### 6.2 AI Cost & Cache Dashboard

Osobna aplikacja w `ai-cost-cache-dashboard/`:
- Frontend: React + Vite + Tailwind + shadcn/ui (port 5173)
- Backend: FastAPI (port 8001)
- Token Cost Comparison — 8 modeli LLM
- Semantic Cache Showcase — hit/miss visualization
- Auto-push z TravelMate po każdym runie
- Manual load z `output/` folder

## 7. Konfiguracja środowiska

Źródło: `.env` + `travelmate/tools/config.py`

Kluczowe zmienne:
```
MODEL_PROVIDER=openai|anthropic|google|lmstudio
MODEL_TEMPERATURE=0.3
OPENAI_API_KEY, OPENAI_MODEL
ANTHROPIC_API_KEY, ANTHROPIC_MODEL
GOOGLE_API_KEY, GOOGLE_MODEL
LMSTUDIO_BASE_URL, LMSTUDIO_MODEL, LMSTUDIO_API_KEY
HERE_API_KEY, HERE_GEOCODE_BASE_URL, HERE_SEARCH_BASE_URL
TRIPADVISOR_API_KEY, TRIPADVISOR_BASE_URL
```

## 8. Artefakty wyjściowe

Każde uruchomienie zapisuje w `output/{timestamp}_{destination}_{days}d/`:

| Plik | Zawartość |
|---|---|
| `itinerary.html` | Interaktywny plan z mapą Leaflet, dark/light mode |
| `itinerary.md` | Plan w Markdown |
| `request.json` | Parametry zapytania |
| `token_usage.json` | Tokeny i czas per agent |

## 9. Obsługa błędów

- Brak/niepoprawny klucz API → `ModelConfigurationError`
- Niepoprawne wejście → `ValueError` z komunikatem użytkowym
- Przekroczenie kontekstu modelu → fallback (itinerary_agent, verification_agent mają własne fallbacki)
- Błąd HERE API → `source="unresolved"`, plan kontynuuje bez danych mapowych
- Błąd dashboard push → logowane DEBUG, ignorowane

## 10. Bezpieczeństwo (POC)

- Sekrety w `.env` (nie commitować)
- Brak auth i rate limiting (POC — do dodania w produkcji)
- Brak input validation pod kątem prompt injection (do dodania w produkcji — Security Guards)
- Szczegóły w `ARCHITEKTURA_PRODUKCYJNA.md` sekcja "Architektura bezpieczeństwa"

## 11. Testowanie

```bash
python3 -m pytest tests/ -v
```

23 testy jednostkowe pokrywające: formatter_agent, input_parser, itinerary_agent, llm_content, markdown_contract, markdown_formatter, output_writer, transport_agent.

Smoke test po zmianach:
1. `python3 -m pytest tests/ -v` — wszystkie testy zielone
2. `python3 -m travelmate.api.main` — serwer startuje
3. Wyślij zapytanie przez UI — plan generuje się
4. Sprawdź `output/{run_id}/token_usage.json`
