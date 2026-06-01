# Rozwój i utrzymanie

## Struktura katalogów

- `travelmate/models.py` — kontrakty danych
- `travelmate/prompts/` — prompty i reguły domenowe per agent
- `travelmate/agents/` — implementacje agentów
- `travelmate/graph.py` — orkiestracja agentów (LangGraph)
- `travelmate/services/planner_service.py` — logika aplikacyjna
- `travelmate/api/main.py` — FastAPI backend
- `travelmate/tools/` — narzędzia wspólne
- `travelmate/web/` — frontend (Tailwind + PWA)
- `ai-cost-cache-dashboard/` — osobna aplikacja analityczna
- `docs/` — dokumentacja projektowa i operacyjna

## Jak dodać nowego agenta

1. Dodaj prompt w nowym pliku w `travelmate/prompts/`
2. Dodaj model wyjściowy w `travelmate/models.py` (jeśli potrzebny)
3. Zaimplementuj funkcję agenta w `travelmate/agents/`
4. Rozszerz `PlannerState` o nowe pole stanu
5. Dodaj węzeł i krawędzie w `build_graph()` w `graph.py`
6. Dodaj `get_tracker().record("nazwa_agenta", response, elapsed_seconds=...)` po `llm.invoke()`
7. Zaktualizuj `formatter_agent` jeśli nowy agent wpływa na finalny output

## Dobre praktyki

- Utrzymuj prompty krótkie i jednoznaczne
- Korzystaj ze strukturalnych wyjść (`with_structured_output`) tam, gdzie to możliwe
- Traktuj `formatter_agent` jako jedyne miejsce odpowiedzialne za finalny Markdown
- Nie mieszaj logiki walidacji wejścia z logiką formatowania
- Konfigurację modeli utrzymuj wyłącznie w `travelmate/tools/config.py` i `model_factory.py`
- Integracje mapowe (HERE) utrzymuj w `travelmate/tools/here_maps.py`
- Każdy agent musi raportować tokeny przez `token_tracker` — nie pomijaj tego kroku

## Testowanie

Uruchomienie testów:
```bash
python -m pytest tests/ -v
```

Aktualnie: 23 testy jednostkowe (formatter, input parser, itinerary, markdown, output writer, transport).

Minimalny smoke test po zmianach:
1. `python3 -m pytest tests/ -v` — wszystkie testy muszą przejść
2. `python3 -m travelmate.api.main` — serwer startuje bez błędów
3. Wyślij zapytanie przez UI — plan generuje się poprawnie
4. Sprawdź `output/{run_id}/token_usage.json` — tokeny są zapisane

## Ograniczenia obecnej wersji (POC)

- Brak semantic cache — każde zapytanie idzie do LLM
- Brak dynamicznego routingu modeli (jeden model dla wszystkich agentów)
- Brak Security Guards (Input/Output Shield)
- Brak auth i rate limiting
- Token tracker dla Gemini może zwracać 0 jeśli API nie zwraca usage_metadata

## Kierunki rozbudowy (produkcja)

Szczegółowy plan w `ARCHITEKTURA_PRODUKCYJNA.md` i `IMPLEMENTACJA_TECHNICZNA.md`:

- Semantic Cache (PostgreSQL + pgvector) — 3 ścieżki: Full Hit, Partial Hit, Full Miss
- Dynamiczny routing modeli (Complexity Router — 3 tiery: Simple/Standard/Complex)
- Security Guards (Input Shield + Output Shield)
- Query Enricher i Editorial Formatter
- Azure deployment z auto-scaling
- B2C freemium + B2B API
