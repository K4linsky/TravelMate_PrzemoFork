# TravelMate — Mapa Wdrożenia Produkcyjnego

> Harmonogram, zasoby, budżet, TCO i ROI dla przejścia z POC do architektury produkcyjnej. Wersja: 1.0 | Data: 2026-05-24

---

## 1. Podsumowanie wykonawcze

| | |
|---|---|
| **Całkowity czas wdrożenia** | 18 tygodni (4,5 miesiąca) |
| **Budżet wdrożenia (CAPEX)** | $42 000 – $58 000 |
| **Miesięczny koszt operacyjny (OPEX)** | $460 – $760/miesiąc (przy 1000 req/dzień) |
| **TCO rok 1** | $47 520 – $67 120 |
| **Break-even** | Miesiąc 8-10 (przy modelu freemium B2C) |
| **ROI rok 1** | 180% – 340% (scenariusz bazowy) |
| **Skala docelowa** | 1 000 req/dzień, możliwość skalowania do 10 000+ |

---

## 2. Harmonogram — 4 fazy wdrożenia

### Oś czasu

```
Tydzień:  1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18
          ├────────────────────┤├───────────────────────┤├──────────────────┤├─────────────────┤
          │    FAZA 1          ││    FAZA 2              ││    FAZA 3        ││    FAZA 4       │
          │    Fundament       ││    Cache + Routing     ││    Security      ││    Hardening    │
          │    (6 tygodni)     ││    (6 tygodni)         ││    (3 tygodnie)  ││    (3 tygodnie) │
```

---

### FAZA 1 — Fundament (Tygodnie 1-6)

**Cel**: Infrastruktura Azure + baza danych + monitoring. Użytkownik nie widzi zmian.

**Tygodnie 1-2: Azure Setup**
- Provisioning Azure Resource Group
- Azure Container Apps (FastAPI deployment)
- Azure Database for PostgreSQL Flexible Server
- Instalacja rozszerzenia pgvector
- Azure Key Vault (sekrety, klucze API)
- Azure Monitor + Application Insights (podstawowe logi)
- CI/CD pipeline (GitHub Actions → Azure Container Registry)

**Tygodnie 3-4: Baza danych i embedding**
- Schemat bazy danych (tabele: semantic_cache, cache_stats, security_events)
- Indeksy HNSW i B-tree
- Embedding pipeline (generowanie wektorów dla istniejących runów z output/)
- Cache Writer (async zapis po każdym Full Miss — tylko write, bez read)
- Migracja istniejących 7 runów POC do cache jako seed data

**Tygodnie 5-6: Monitoring i testy**
- Dashboard operacyjny (latency, error rate, throughput)
- Dashboard kosztowy (token usage per agent, cost per request)
- Load testing (symulacja 100 req/dzień)
- Dokumentacja deployment
- Go/No-Go review

**Deliverables Fazy 1:**
- ✅ System działa na Azure (identycznie jak POC)
- ✅ Każdy request loguje pełne metryki (tokeny, czas, koszt)
- ✅ Cache zbiera dane (write-only)
- ✅ CI/CD działa

**Zasoby Fazy 1:**
- 1x Backend Developer (senior) — 6 tygodni full-time
- 1x DevOps/Cloud Engineer — 4 tygodnie
- Azure infrastructure costs: ~$800

---

### FAZA 2 — Cache + Routing (Tygodnie 7-12)

**Cel**: Semantic cache aktywny + dynamiczny routing modeli. Pierwsze oszczędności kosztowe.

**Tygodnie 7-8: Complexity Router**
- Implementacja Complexity Router Agent
- Rozszerzenie PlannerState (complexity_score, routing_config)
- Rozszerzenie model_factory (model_id parameter)
- Aktualizacja 6 agentów (1 linijka per agent)
- Aktualizacja grafu LangGraph
- Testy jednostkowe Complexity Router (100+ przypadków testowych)

**Tygodnie 9-10: Cache Read + Full Hit**
- Cache Lookup (ANN search + Cache Decision Engine)
- Full Hit path (similarity ≥ 0.88)
- A/B test: 20% ruchu przez nowy system, 80% przez stary
- Kalibracja similarity threshold na podstawie danych z Fazy 1
- Dashboard cache (hit rate, savings)

**Tygodnie 11-12: Partial Hit + Query Enricher**
- Cache Decomposer (logika per komponent)
- Partial Hit path (similarity 0.70-0.87)
- Query Enricher Agent (kontekst sezonowy, kulturowy, normalizacja)
- Rozszerzenie A/B test do 50% ruchu
- Analiza jakości odpowiedzi (manual review 50 planów)

**Deliverables Fazy 2:**
- ✅ Cache hit rate > 20% (cel po 6 tygodniach zbierania danych)
- ✅ Complexity Router aktywny (3 tiery)
- ✅ Koszty LLM spadają o ~30% vs Faza 1
- ✅ Partial Hit path działa

**Zasoby Fazy 2:**
- 1x Backend Developer (senior) — 6 tygodni full-time
- 1x ML Engineer / AI Specialist — 4 tygodnie (kalibracja modeli, quality review)
- Azure costs: ~$1 200 (więcej ruchu, cache queries)

---

### FAZA 3 — Security (Tygodnie 13-15)

**Cel**: Security Guards + Azure API Management. System gotowy na ruch publiczny.

**Tydzień 13: Input Shield**
- Regex-based injection detection
- LLM classifier (SAFE/UNSAFE)
- PII detection i sanitization
- Rate limiting (Redis)
- Testy penetracyjne (prompt injection, jailbreak attempts)

**Tydzień 14: Output Shield + Azure API Management**
- Output Shield (data leakage, role escape, hallucination check)
- Azure API Management setup (rate limiting, auth)
- JWT authentication (B2C)
- API Key management (B2B)
- WAF rules

**Tydzień 15: Editorial Formatter + testy end-to-end**
- Editorial Formatter (B2C vs B2B output)
- Testy end-to-end (pełny flow wszystkich 3 ścieżek)
- Security audit (zewnętrzny lub wewnętrzny)
- Performance testing (100 concurrent users)

**Deliverables Fazy 3:**
- ✅ System bezpieczny na ruch publiczny
- ✅ Auth działa (JWT + API Keys)
- ✅ Security Guards aktywne
- ✅ Editorial Formatter aktywny

**Zasoby Fazy 3:**
- 1x Backend Developer (senior) — 3 tygodnie
- 1x Security Engineer — 2 tygodnie
- Azure costs: ~$600

---

### FAZA 4 — Hardening i Launch (Tygodnie 16-18)

**Cel**: Produkcja gotowa. Launch B2C i B2B.

**Tydzień 16: Azure AD B2C + B2B API**
- Azure AD B2C integration (rejestracja, logowanie)
- B2B API endpoints (POST /v1/itinerary, webhook support)
- B2B dokumentacja API (OpenAPI spec)
- Pricing tiers (freemium B2C, per-request B2B)

**Tydzień 17: Load testing + SLA**
- Load testing: 1000 req/dzień przez 3 dni
- Auto-scaling konfiguracja (Container Apps)
- SLA dokumentacja (99.9% uptime)
- Runbook (incident response procedures)
- Backup i disaster recovery

**Tydzień 18: Soft launch**
- Soft launch B2C (invite-only, 100 użytkowników)
- Monitoring 24/7 przez pierwszy tydzień
- Feedback collection
- Bug fixes
- Public launch preparation

**Deliverables Fazy 4:**
- ✅ System produkcyjny z SLA 99.9%
- ✅ B2C freemium działa
- ✅ B2B API działa
- ✅ Auto-scaling skonfigurowany
- ✅ Runbook gotowy

**Zasoby Fazy 4:**
- 1x Backend Developer (senior) — 3 tygodnie
- 1x Frontend Developer — 2 tygodnie (B2C UI polish)
- 1x DevOps — 1 tydzień
- Azure costs: ~$800

---

## 3. Zasoby — zespół

### Minimalny zespół (startup/bootstrap)

| Rola | Zaangażowanie | Fazy | Koszt (rynkowy) |
|---|---|---|---|
| Backend Developer Senior (Python/FastAPI/LangGraph) | Full-time 18 tygodni | 1-4 | $18 000 – $27 000 |
| DevOps/Cloud Engineer (Azure) | Part-time 8 tygodni | 1, 4 | $6 400 – $9 600 |
| ML Engineer / AI Specialist | Part-time 6 tygodni | 2 | $6 000 – $9 000 |
| Security Engineer | Part-time 2 tygodnie | 3 | $2 400 – $3 600 |
| Frontend Developer | Part-time 2 tygodnie | 4 | $2 000 – $3 000 |
| **TOTAL TEAM** | | | **$34 800 – $52 200** |

### Alternatywa: jeden full-stack developer

Jeśli jeden developer pokrywa backend + DevOps + ML:
- 18 tygodni full-time
- Koszt: $18 000 – $27 000
- Ryzyko: dłuższy czas, wyższe ryzyko błędów w security i ML

### Zewnętrzne usługi (opcjonalne)

| Usługa | Koszt | Kiedy |
|---|---|---|
| Security audit (zewnętrzny) | $3 000 – $5 000 | Przed Fazą 4 |
| Load testing tool (k6 Cloud) | $200/miesiąc | Faza 4 |
| Legal (GDPR compliance review) | $1 500 – $3 000 | Przed launch |

---

## 4. Budżet wdrożenia (CAPEX)

### Scenariusz minimalny (1 developer)

| Pozycja | Koszt |
|---|---|
| Developer (18 tygodni) | $18 000 |
| Azure infrastructure (18 tygodni) | $3 400 |
| LLM API costs (development + testing) | $800 |
| Security audit | $3 000 |
| Narzędzia i licencje | $500 |
| **TOTAL CAPEX** | **$25 700** |

### Scenariusz standardowy (zespół 3-4 osób)

| Pozycja | Koszt |
|---|---|
| Zespół deweloperski | $34 800 – $52 200 |
| Azure infrastructure (18 tygodni) | $3 400 |
| LLM API costs (development + testing) | $1 200 |
| Security audit | $4 000 |
| Legal (GDPR) | $2 000 |
| Narzędzia i licencje | $800 |
| Buffer (10% na nieprzewidziane) | $4 620 – $6 160 |
| **TOTAL CAPEX** | **$50 820 – $69 760** |

---

## 5. TCO — Total Cost of Ownership (rok 1)

### Koszty operacyjne miesięczne (OPEX) przy 1000 req/dzień

| Komponent | Koszt/miesiąc |
|---|---|
| Azure Container Apps (1-3 repliki) | $50 – $80 |
| Azure PostgreSQL Flexible (Standard_D2s_v3) | $100 – $150 |
| Azure Cache for Redis (C1) | $55 |
| Azure API Management (Developer tier) | $50 |
| Azure AD B2C (do 50K MAU — free) | $0 |
| Azure Monitor + Application Insights | $20 |
| Azure Blob Storage (HTML outputs) | $5 |
| Azure Key Vault | $5 |
| **Infrastructure subtotal** | **$285 – $365/miesiąc** |

### LLM API costs przy 1000 req/dzień

Założenia:
- 40% cache hit rate (Full Hit: $0.001, Partial Hit: $0.015)
- 60% cache miss: 50% SIMPLE ($0.035), 35% STANDARD ($0.085), 15% COMPLEX ($0.25)

```
Dziennie:
  400 cache hits × $0.008 avg    = $3.20
  300 SIMPLE × $0.035            = $10.50
  210 STANDARD × $0.085          = $17.85
  90 COMPLEX × $0.25             = $22.50
  TOTAL/dzień                    = $54.05
  TOTAL/miesiąc                  = ~$1 622
```

Dla porównania — bez cache i bez routingu (wszystko Claude Sonnet):
```
  1000 req × $0.15 avg           = $150/dzień = $4 500/miesiąc
```

**Oszczędność z cache + routing: ~$2 878/miesiąc (~64%)**

### TCO rok 1 (scenariusz standardowy)

| | Koszt |
|---|---|
| CAPEX (wdrożenie) | $50 820 – $69 760 |
| OPEX miesiące 1-6 (ramp-up, niższy ruch) | $8 000 – $12 000 |
| OPEX miesiące 7-12 (pełna skala) | $11 460 – $15 780 |
| **TCO rok 1** | **$70 280 – $97 540** |

### TCO rok 2 (tylko OPEX, brak CAPEX)

| | Koszt |
|---|---|
| OPEX 12 miesięcy (1000 req/dzień) | $22 920 – $31 560 |
| Maintenance developer (part-time) | $12 000 – $18 000 |
| **TCO rok 2** | **$34 920 – $49 560** |

---

## 6. ROI — Return on Investment

### Model przychodów

**B2C Freemium:**
- Free tier: 5 planów/miesiąc (koszt akwizycji, nie przychód)
- Basic: $9.99/miesiąc — 20 planów
- Premium: $19.99/miesiąc — unlimited

**B2B API:**
- Starter: $99/miesiąc — 500 req
- Growth: $299/miesiąc — 2000 req
- Enterprise: $999/miesiąc — 10 000 req + SLA

### Scenariusz bazowy (konserwatywny)

Założenia po 12 miesiącach:
- 500 B2C użytkowników płatnych (avg $12/miesiąc)
- 10 klientów B2B (avg $200/miesiąc)

```
Przychód miesięczny (miesiąc 12):
  B2C: 500 × $12 = $6 000
  B2B: 10 × $200 = $2 000
  TOTAL: $8 000/miesiąc

Koszty miesięczne (miesiąc 12):
  OPEX: $1 907 – $2 630
  Maintenance: $1 000 – $1 500
  TOTAL: $2 907 – $4 130

Zysk miesięczny (miesiąc 12): $3 870 – $5 093
```

### Scenariusz optymistyczny

Założenia po 12 miesiącach:
- 2000 B2C użytkowników płatnych (avg $14/miesiąc)
- 30 klientów B2B (avg $350/miesiąc)

```
Przychód miesięczny (miesiąc 12):
  B2C: 2000 × $14 = $28 000
  B2B: 30 × $350 = $10 500
  TOTAL: $38 500/miesiąc
```

### Analiza ROI

| Metryka | Scenariusz bazowy | Scenariusz optymistyczny |
|---|---|---|
| CAPEX | $60 000 | $60 000 |
| Break-even (miesiąc) | Miesiąc 10 | Miesiąc 6 |
| Przychód rok 1 | $48 000 | $180 000 |
| Koszty rok 1 (CAPEX + OPEX) | $83 000 | $83 000 |
| ROI rok 1 | -42% (inwestycja) | +117% |
| Przychód rok 2 | $96 000 | $462 000 |
| Koszty rok 2 (tylko OPEX) | $42 000 | $65 000 |
| ROI rok 2 | +129% | +611% |
| **ROI skumulowany 2 lata** | **+73%** | **+430%** |

### Kluczowe dźwignie ROI

1. **Cache hit rate** — każdy % wzrostu hit rate = ~$29/miesiąc oszczędności przy 1000 req/dzień. Cel 40% = $1 160/miesiąc oszczędności vs brak cache.

2. **B2B konwersja** — jeden klient Enterprise ($999/miesiąc) = 52% miesięcznych kosztów OPEX. Priorytet: 3-5 klientów Enterprise w roku 1.

3. **Skala** — przy 5000 req/dzień koszty rosną liniowo (~$9 000/miesiąc LLM) ale przychody rosną szybciej (więcej użytkowników). Marża rośnie ze skalą.

---

## 7. Ryzyka i mitygacje

| Ryzyko | Prawdopodobieństwo | Wpływ | Mitygacja |
|---|---|---|---|
| Wzrost cen LLM API | Średnie | Wysoki | Pricing table w JSON, łatwa zmiana modeli, cache redukuje zależność |
| Niska jakość odpowiedzi w SIMPLE tier | Niskie | Średni | A/B testing, manual review, opcja "Improve" dla użytkownika |
| Cache hit rate < 20% | Niskie | Średni | Seed cache z popularnymi destynacjami, obniż similarity threshold |
| Opóźnienie wdrożenia | Średnie | Średni | Buffer 10% w budżecie, fazy niezależne (każda ma wartość samodzielnie) |
| Atak prompt injection | Niskie | Wysoki | Input Shield, monitoring, fail-safe fallback |
| Konkurencja (Google Trips, TripAdvisor AI) | Wysokie | Wysoki | Szybkie wdrożenie, B2B API jako moat, personalizacja |

---

## 8. Kamienie milowe i kryteria sukcesu

| Kamień milowy | Tydzień | Kryterium sukcesu |
|---|---|---|
| M1: Azure Live | 2 | System działa na Azure, CI/CD aktywny |
| M2: Cache Collecting | 6 | 100+ wpisów w cache, metryki logowane |
| M3: Cache Active | 10 | Cache hit rate > 15%, koszty LLM -20% |
| M4: Full Routing | 12 | 3 tiery aktywne, Partial Hit działa |
| M5: Security Ready | 15 | Security Guards aktywne, auth działa |
| M6: Production Launch | 18 | 100 użytkowników B2C, 2 klientów B2B |
| M7: Scale | Miesiąc 6 | 500 req/dzień, cache hit rate > 35% |
| M8: Break-even | Miesiąc 10 | Przychody > koszty operacyjne |

---

## 9. Rekomendacja

**Rekomendowany scenariusz**: Standardowy (zespół 3-4 osób), budżet $55 000 – $70 000.

**Uzasadnienie**:
- Fazy są niezależne — każda dostarcza wartość samodzielnie. Można zatrzymać po Fazie 2 jeśli budżet się skończy i mieć działający system z cache i routingiem.
- Największy ROI pochodzi z B2B API — priorytet na szybkie wdrożenie Fazy 3 i 4 dla pierwszych klientów Enterprise.
- Cache hit rate jest kluczową metryką — im szybciej uruchomisz Fazę 1 (zbieranie danych), tym szybciej cache zacznie działać efektywnie.
- Nie warto oszczędzać na security (Faza 3) — jeden incydent bezpieczeństwa może zniszczyć reputację produktu.

**Następny krok**: Decyzja o modelu finansowania (bootstrap vs inwestor) i wyborze pierwszego developera/zespołu.

---

*Dokument: MAPA_WDROZENIA.md | Wersja: 1.0 | Data: 2026-05-24*
