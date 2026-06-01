# Architektura TravelMate AI (POC)

> Dokument opisuje architekturę obecnej wersji POC. Architektura produkcyjna opisana jest w `ARCHITEKTURA_PRODUKCYJNA.md`.

## Cel systemu

TravelMate AI generuje plan podróży dzień-po-dniu na bazie preferencji użytkownika, z naciskiem na:

- spójność geograficzną (Geo-Clustering),
- realne tempo zwiedzania,
- dopasowanie gastronomii do lokalizacji, budżetu i ograniczeń.

## Główne komponenty

### `travelmate/models.py`

Zawiera modele danych Pydantic oraz stan grafu:

- `ItineraryInput` — wejście użytkownika
- `GeoOutput` — podział na miejsca i strategia przemieszczania
- `ItineraryDraft` — strukturalny plan dzienny
- `VerificationOutput` — ostrzeżenia i korekty
- `PlannerState` — wspólny stan przepływający przez węzły LangGraph

### `travelmate/prompts/`

Definiuje prompty w osobnych plikach per agent:
`profile_prompt.py`, `transport_prompt.py`, `geo_prompt.py`, `itinerary_prompt.py`, `verification_prompt.py`, `formatter_prompt.py`

### `travelmate/agents/`

Każdy agent ma osobny plik:
`profile_agent.py`, `transport_agent.py`, `geo_agent.py`, `itinerary_agent.py`, `verification_agent.py`, `formatter_agent.py`

### `travelmate/tools/`

Narzędzia współdzielone:

- `config.py` — wczytanie konfiguracji providerów
- `model_factory.py` — switch modeli (OpenAI / Anthropic / Google / LM Studio)
- `token_tracker.py` — śledzenie zużycia tokenów per agent (input/output/elapsed_seconds)
- `here_maps.py` — integracja HERE (geocode/discover/lookup)
- `tripadvisor.py` — integracja TripAdvisor (zdjęcia, oceny, linki)
- `payload.py` — serializacja wejścia
- `markdown_formatter.py` — budowa finalnego Markdown
- `dashboard_push.py` — asynchroniczny push do AI Cost & Cache Dashboard

### `travelmate/graph.py`

Zawiera wiring agentów i definicję grafu (`build_graph`).

**Aktualny graf (z równoległym pipeline'em):**

```
START → complexity_router (jeśli aktywny)
      → profile_agent  ┐ (równolegle)
      → transport_agent ┘
      → fan_in
      → geo_agent
      → itinerary_agent
      → verification_agent
      → formatter_agent
      → END
```

`profile_agent` i `transport_agent` działają równolegle — oszczędność ~2-4s per run.

### `travelmate/services/planner_service.py`

- Parsuje wejście użytkownika (JSON / key-value / język naturalny)
- Uruchamia graf agentów
- Zbiera token usage z `token_tracker`
- Zapisuje wyniki do `output/` (itinerary.html, itinerary.md, request.json, token_usage.json)
- Asynchronicznie pushuje run do AI Cost & Cache Dashboard

### `travelmate/api/main.py`

FastAPI backend z endpointami:

- `GET /` — główny interfejs webowy
- `POST /chat` — wysłanie zapytania, uruchomienie pipeline'u
- `WebSocket /admin/logs` — streaming logów i statusów agentów na żywo
- `GET /health` — status systemu (provider, model, active)
- `GET /trips` — lista wszystkich wygenerowanych planów
- `GET /trips/{id}/html` — serwowanie wygenerowanego HTML

## Przepływ danych

### 1) `profile_agent`
Buduje profil podróżnika (styl, tempo, budżet, zainteresowania). Działa równolegle z transport_agent.

### 2) `transport_agent`
Generuje raport transportowy (loty, kolej, wynajem auta, auto własne). Działa równolegle z profile_agent.

### 3) `geo_agent`
Tworzy plan strefami geograficznymi, wzbogaca każde miejsce przez HERE API i TripAdvisor.

### 4) `itinerary_agent`
Generuje szczegółowy plan (atrakcje, lunch, kolacja, nocleg) na podstawie geo clustrów.

### 5) `verification_agent`
Weryfikuje ryzyka (godziny otwarcia, logistyka, budżet).

### 6) `formatter_agent`
Składa wszystkie outputy do finalnego Markdown + HTML z mapą POI.

## Token Tracking

Każdy agent mierzy:
- `input_tokens` — tokeny wejściowe
- `output_tokens` — tokeny wyjściowe
- `elapsed_seconds` — czas wywołania LLM

Wyniki zapisywane w `output/{run_id}/token_usage.json` i dostępne w AI Cost & Cache Dashboard.

## Zarządzanie konfiguracją

`model_factory.get_chat_model()` korzysta z `MODEL_PROVIDER` i odpowiednich kluczy API z `.env`.

Obsługiwani providerzy: OpenAI, Anthropic, Google, LM Studio.

## Decyzje projektowe

- **Równoległy pipeline** — profile_agent i transport_agent działają jednocześnie
- **Strukturalne wyjścia agentów** — redukują ryzyko niespójnego JSON
- **Oddzielny formatter** — rozdziela logikę planowania od prezentacji
- **Token tracker** — mierzy realne zużycie tokenów per agent dla optymalizacji kosztów
- **Dashboard push** — asynchroniczny, nie blokuje odpowiedzi użytkownika
