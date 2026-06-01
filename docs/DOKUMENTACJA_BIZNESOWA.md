# Dokumentacja biznesowa — TravelMate AI

## 1. Cel biznesowy

TravelMate AI to aplikacja wspierająca planowanie podróży poprzez automatyczne generowanie planu dzień-po-dniu na podstawie opisu użytkownika w języku naturalnym.

Główna wartość biznesowa:
- Skrócenie czasu przygotowania planu podróży z godzin do minut
- Standaryzacja jakości planów przez pipeline 6 wyspecjalizowanych agentów AI
- Personalizacja — uwzględnienie budżetu, tempa, zainteresowań i ograniczeń
- Elastyczność technologiczna — obsługa wielu providerów LLM (OpenAI, Anthropic, Google, LM Studio)
- Optymalizacja kosztów AI — token tracking, semantic cache (roadmapa), dynamiczny routing modeli (roadmapa)

## 2. Problem, który rozwiązujemy

Użytkownicy często:
- Nie wiedzą od czego zacząć planowanie
- Mają ograniczony czas na research
- Otrzymują niespójne rekomendacje z wielu źródeł
- Potrzebują planu uwzględniającego budżet, tempo i ograniczenia (dieta, dzieci, zwierzęta)

TravelMate AI agreguje te potrzeby do jednego, uporządkowanego procesu z interaktywną mapą POI.

## 3. Grupy docelowe

### 3.1 B2C — Użytkownicy indywidualni

- Pary i rodziny planujące city-break lub dłuższy wyjazd
- Osoby podróżujące samodzielnie
- Użytkownicy preferujący szybki, gotowy plan zamiast ręcznego researchu
- Model: freemium (5 planów/miesiąc gratis, potem $2/plan lub $9.99-19.99/miesiąc)

### 3.2 B2B — Partnerzy i integratorzy

- Biura podróży i konsultanci travel
- Portale contentowe o podróżach
- OTA (Online Travel Agencies) integrujące API
- Firmy benefitowe oferujące narzędzia planowania wyjazdów
- Model: $0.05-0.20/zapytanie lub pakiety miesięczne ($99-$999/miesiąc)

## 4. Propozycja wartości (Value Proposition)

- **Szybkość**: plan w 15-45 sekund (POC), < 15s dla prostych zapytań (produkcja z cache)
- **Spójność**: sekwencja 6 agentów pilnuje logiki i jakości wyniku
- **Personalizacja**: uwzględnienie preferencji, ograniczeń i stylu podróżowania
- **Czytelność**: interaktywny HTML z mapą POI + Markdown
- **Transparentność kosztów**: token tracking per agent, porównanie kosztów modeli w dashboardzie
- **Elastyczność**: obsługa wielu providerów LLM, łatwa zmiana modelu

## 5. Zakres produktu

### 5.1 Obecna wersja (POC)

W zakresie:
- Wejście w języku naturalnym (PL/EN)
- Parser strukturyzujący wymagania (JSON / key-value / NLP)
- Pipeline 6 agentów AI (profile, transport, geo, itinerary, verification, formatter)
- Integracja HERE Maps (współrzędne, adresy, POI)
- Integracja TripAdvisor (zdjęcia, oceny, linki)
- Interaktywny HTML z mapą Leaflet
- GUI webowe (FastAPI + Tailwind + PWA)
- My Trips — historia wygenerowanych planów
- Token tracking per agent
- AI Cost & Cache Dashboard (osobna aplikacja analityczna)
- Obsługa 4 providerów LLM

Poza zakresem POC (w roadmapie produkcyjnej):
- Semantic cache (PostgreSQL + pgvector)
- Dynamiczny routing modeli (Complexity Router)
- Security Guards (Input/Output Shield)
- Auth i rate limiting
- B2B API z webhooks
- System rezerwacji i płatności

### 5.2 Roadmapa produkcyjna

Szczegóły w `MAPA_WDROZENIA.md` i `ARCHITEKTURA_PRODUKCYJNA.md`.

**Faza 1** (tygodnie 1-6): Azure infrastructure + semantic cache (zbieranie danych)
**Faza 2** (tygodnie 7-12): Cache aktywny + Complexity Router (oszczędności kosztowe)
**Faza 3** (tygodnie 13-15): Security Guards + API Management (gotowość publiczna)
**Faza 4** (tygodnie 16-18): B2C launch + B2B API

## 6. Kluczowe procesy biznesowe

1. Użytkownik opisuje podróż w języku naturalnym
2. System parsuje i strukturyzuje wymagania
3. Pipeline agentów generuje plan (profil → transport → geo → itinerary → weryfikacja → formatowanie)
4. Użytkownik otrzymuje interaktywny plan HTML z mapą + Markdown
5. Plan zapisywany lokalnie w `output/` z pełnymi metadanymi

## 7. KPI i metryki sukcesu

### 7.1 Produktowe (POC)
- Współczynnik poprawnie ukończonych generacji (cel: > 95%)
- Średni czas generacji planu (aktualnie: ~25-35s)
- Zużycie tokenów per agent (mierzone przez token_tracker)
- Koszt per plan (aktualnie: ~$0.05-0.15 przy Gemini Flash)

### 7.2 Produktowe (produkcja)
- Cache hit rate (cel: > 40%)
- Koszt per zapytanie po tiering (cel: < $0.05 Simple, < $0.20 Complex)
- Latency P95 (cel: < 1s cache hit, < 15s cache miss Simple)

### 7.3 Biznesowe
- Liczba aktywnych użytkowników B2C (MAU)
- Liczba klientów B2B i przychód API
- Break-even (cel: miesiąc 8-10 od launchu)
- ROI rok 2 (cel: > 100%)

### 7.4 Jakościowe
- Satysfakcja użytkownika (NPS/CSAT)
- Ocena przydatności planu
- Czytelność i kompletność wyników

## 8. Ryzyka biznesowe

| Ryzyko | Prawdopodobieństwo | Mitygacja |
|---|---|---|
| Wzrost cen LLM API | Średnie | Semantic cache + dynamiczny routing modeli |
| Niska jakość odpowiedzi | Niskie | Pipeline weryfikacji + Cache Validation Gate |
| Konkurencja (Google, TripAdvisor AI) | Wysokie | Szybkie wdrożenie B2B API jako moat |
| Zależność od zewnętrznych API | Średnie | Multi-provider support, fallback mechanizmy |
| Bezpieczeństwo (prompt injection) | Niskie | Security Guards w roadmapie produkcyjnej |

## 9. Interesariusze

- **Product Owner**: priorytety, backlog, decyzje architektoniczne
- **Zespół inżynierski**: rozwój, utrzymanie, jakość
- **Użytkownicy końcowi B2C**: feedback, walidacja wartości
- **Klienci B2B**: integracja API, SLA
- **Partnerzy technologiczni (LLM providers)**: dostępność i SLA modeli

## 10. Definicja gotowości biznesowej (Business DoD)

Nowa funkcjonalność uznawana jest za gotową, gdy:
- Ma opis wartości i wpływu na KPI
- Ma scenariusz użycia i kryteria akceptacji
- Jest opisana w dokumentacji użytkowej i technicznej
- Posiada testy (jednostkowe lub integracyjne)
- Posiada plan monitorowania po wdrożeniu
