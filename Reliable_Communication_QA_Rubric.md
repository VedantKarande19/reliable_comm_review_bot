# Reliable Communication — Outbound Call QA Rubric
*(Translation-Aware & Diarization-Corrected Edition)*

**Use:** Paste this document (or its "Evaluator instructions" section) into a QA / LLM prompt with the **translated English transcript** (and optional audio notes). The original call may have been conducted in Hindi, Hinglish, Marathi, or a regional mix — the transcript you receive is a machine or human translation into English. Speaker labels (Agent / Customer) may be **incorrectly assigned** by the diarization system — always verify speaker identity before scoring. Score **every applicable parameter** as **D / P / N / NA** and assign a **Quality Rating** of **POOR / AVERAGE / GOOD / EXCELLENT** per the classification rules below.

**Score anchors (apply to each parameter):**

| Score | Meaning |
|------:|---------|
| D | Done — fully executed, meets standard |
| P | Partial — attempted but incomplete or weak |
| N | Not Done — absent or contradicts policy |
| NA | Not Applicable — parameter does not apply to this call type |

**Classification:** Internal & Confidential (Reliable Communication source material).

---

## Evaluator instructions

1. **Read the full translated transcript** (speaker labels if available: Agent / Customer). Treat the English translation as the authoritative text for scoring — do not penalise for translation phrasing that is grammatically awkward but semantically correct.
2. **Verify and correct speaker labels (Section D) — do this before anything else.** Diarization systems frequently swap Agent and Customer labels. Reconstruct the correct speaker identity for every turn using the detection signals in Section D. Do not score any parameter until speaker labels are confirmed or corrected.
3. **Apply translation-awareness rules (Section T)** before scoring any parameter. Understand what artefacts are introduced by translation and how to handle them.
4. Resolve the agent's **spoken nickname** to their **Official CRM Login Name** using the nickname mapping table (Section 1). Always display the Official CRM Login Name in the output.
5. Infer **call type** before scoring: **Fresh Lead**, **Follow-Up**, or **Short / Disconnected (CD)**. Apply call-type isolation rules (Section 3) — mark inapplicable parameters **NA**.
6. Check **Critical Override Rules** (Section 2) first. If any override condition is triggered, Quality Rating is automatically **POOR** regardless of parameter scores.
7. For each **scored** parameter, output: `param_id`, `score` (D/P/N/NA), `one_line_evidence` (translated quote or paraphrase), `notes` (optional — flag translation or diarization issues here).
8. Assess **IFUG** persuasion factors (Section 6) and determine the final **Quality Rating**.
9. Assign **Lead Temperature** (HOT / WARM / COLD) and map **AI DISP** to an exact code from Section 8.
10. End with **top_3_improvements** (bullets) and a **50-word max Audit Remark**.

Suggested machine-readable block (after narrative):

```json
{
  "call_type": "fresh_lead|follow_up|short_disconnected",
  "tc_name_official": "Official CRM Login Name",
  "customer_name": "Customer Name",
  "lead_temperature": "HOT|WARM|COLD",
  "ai_disp": "EXACT_CODE",
  "override_triggered": false,
  "override_reason": null,
  "diarization_flags": [
    {
      "turn_reference": "turn number or approximate timestamp",
      "labeled_as": "Agent|Customer",
      "corrected_to": "Agent|Customer",
      "reason": "greeting_pattern|script_language|question_vs_answer|product_knowledge|name_used|role_reversal_block|other",
      "confidence": "high|medium|low",
      "scoring_impact": "scores_reassigned|override_not_triggered|parameter_rescued|parameter_penalised_correctly"
    }
  ],
  "diarization_swap_detected": false,
  "translation_flags": [
    {
      "param_id": "EXC",
      "flag": "informal_term_detected|tone_lost_in_translation|untranslated_word|honorific_missing|ambiguous_translation",
      "original_term": "original word/phrase if visible in transcript",
      "translated_as": "how it appeared in English transcript",
      "scoring_impact": "penalised|not_penalised|escalated_to_override"
    }
  ],
  "scores": [
    {"id": "EXC",         "score": "D",  "evidence": "…", "notes": "…"},
    {"id": "VOICEMOD",    "score": "P",  "evidence": "…", "notes": "…"},
    {"id": "OBJ_HAND",    "score": "N",  "evidence": "…", "notes": "…"},
    {"id": "INTRO",       "score": "D",  "evidence": "…", "notes": "…"},
    {"id": "SHORT_STORY", "score": "D",  "evidence": "…", "notes": "…"},
    {"id": "PROBING",     "score": "P",  "evidence": "…", "notes": "…"},
    {"id": "PRESENTATION","score": "NA", "evidence": "…", "notes": "…"},
    {"id": "PRICE",       "score": "NA", "evidence": "…", "notes": "…"},
    {"id": "CLOSE",       "score": "D",  "evidence": "…", "notes": "…"},
    {"id": "IFUG_I",      "score": "D",  "evidence": "…", "notes": "…"},
    {"id": "IFUG_F",      "score": "N",  "evidence": "…", "notes": "…"},
    {"id": "IFUG_U",      "score": "NA", "evidence": "…", "notes": "…"},
    {"id": "IFUG_G",      "score": "NA", "evidence": "…", "notes": "…"}
  ],
  "quality_rating": "POOR|AVERAGE|GOOD|EXCELLENT",
  "audit_remark": "Max 50 words. Simple English. Summarize energy, structure, persuasion (IFUG), and overall impact. Note call type. Note any translation flags that affected scoring.",
  "top_3_improvements": ["…", "…", "…"]
}
```

---

## Section D · Diarization error detection & correction *(run before Section T and before scoring)*

Diarization is the process by which the transcription system separates and labels different speakers. In outbound call transcripts, speaker labels are typically **Speaker 0 / Speaker 1** or **Agent / Customer**. These labels are **frequently wrong** — the system may assign the agent's words to the Customer track and vice versa for entire blocks or individual turns. **Never trust diarization labels blindly.** Always verify using the signals below.

---

### D1 · Why diarization swaps happen

| Root cause | What it looks like in the transcript |
|-----------|--------------------------------------|
| **Channel bleed** | Both voices picked up on the same audio channel; system guesses incorrectly |
| **Silence / hold** | Agent pauses or puts customer on hold; system re-labels the next speaker incorrectly |
| **Similar vocal pitch** | Agent and customer have similar voice registers; model confuses them |
| **Language switching** | Code-switching between Hindi/English causes the model to re-assign speaker mid-sentence |
| **Short turns** | Very short responses ("haan", "ok", "ji") are frequently mis-labelled |
| **Call start detection** | The very first few seconds are especially error-prone; the greeting is sometimes assigned to the Customer label |

---

### D2 · Primary signals to identify the real Agent

Use these signals to determine which speaker is actually the Agent, regardless of what the label says:

| Signal | Agent indicator | Customer indicator |
|--------|-----------------|--------------------|
| **Greeting / introduction** | Says their own name, company name ("Reliable Communication"), and purpose of call | Responds to greeting; may give their own name when asked |
| **Script-style language** | Follows a structured pitch sequence (Intro → Short Story → Probing → Presentation → Close); uses formal professional register | Speaks naturally and reactively; asks questions about product, price, or process |
| **Product knowledge** | Explains features, benefits, schemes, pricing accurately | Asks about features, benefits, pricing; may express doubts or objections |
| **Control of conversation flow** | Initiates topic changes; asks structured probing questions; drives toward a close | Responds to questions; raises objections; asks for clarification |
| **Honorific direction** | Addresses the other person as "Sir", "Ma'am", "Aap", "Ji" | May or may not use honorifics; often uses the agent's name |
| **CRM / process language** | References callbacks, scheduling, site visits, registrations, follow-up commitments | Does not use CRM terminology |
| **Name stated** | States their own name early (matches a known agent nickname in Section 1) | States their name when asked; name does not match the agent nickname list |

---

### D3 · How to correct diarization errors

**Step 1 — Read the full transcript ignoring labels first.** Understand the conversational flow purely from content.

**Step 2 — Identify the Agent anchor.** Find the turn that contains the Intro (greeting + name + company + purpose). That speaker is the Agent, regardless of the label assigned.

**Step 3 — Propagate the correction forward.** Once the Agent is identified in one turn, all other turns by the same labeled speaker are also Agent turns — unless there is a clear mid-call swap signal (see D1).

**Step 4 — Check for partial swaps.** Sometimes only a few turns are mislabelled (not the entire call). Look for turns where:
- The "Customer" label is asking structured probing questions or pitching a product → likely Agent turn
- The "Agent" label is expressing confusion, asking what the call is about, or raising objections → likely Customer turn

**Step 5 — Log all corrections in `diarization_flags`** in the JSON output with the turn reference, what it was labelled as, what it was corrected to, and the reason.

---

### D4 · Diarization correction confidence levels

| Confidence | When to use | Scoring treatment |
|-----------|-------------|-------------------|
| **High** | Multiple signals align (greeting + name + script language) | Correct and score as corrected |
| **Medium** | One or two signals present but not fully conclusive | Correct, score as corrected, note in `diarization_flags` |
| **Low** | Ambiguous — cannot determine correct speaker from content alone | Do **not** score the affected turn; mark the parameter as **NA** with note `diarization_unresolvable` |

---

### D5 · Impact of diarization errors on scoring

Diarization errors directly corrupt the following parameters if not corrected:

| Parameter | How a swap corrupts it | Corrective action |
|-----------|----------------------|-------------------|
| **INTRO** | Agent's greeting assigned to Customer → Intro appears missing → wrongly scored N | Reassign turn to Agent; score Intro normally |
| **SHORT_STORY** | Agent's 3 Ws assigned to Customer → structure appears absent | Reassign; score normally |
| **PROBING** | Agent's questions appear as Customer questions → probing appears absent | Reassign; count Agent's actual questions |
| **OBJ_HAND** | Customer objection assigned to Agent → agent appears to be raising objections against themselves | Reassign; identify real objection and agent's response |
| **CLOSE** | Agent's close assigned to Customer → close appears missing | Reassign; score normally |
| **Unprofessional Behavior Override** | Informal language in Customer turn assigned to Agent → override wrongly triggered | Reassign; do **not** trigger override for Customer speech |
| **EXC / VOICEMOD** | If audio notes reference the wrong channel due to swap, vocal scoring may be applied to wrong person | Note in `diarization_flags`; reassess from audio if possible |

---

### D6 · Critical rule — never penalise agent for customer speech

If a diarization swap caused the Customer's words to appear under the Agent label:

- **Do not trigger any Critical Override** based on those misattributed turns.
- **Do not score any parameter as N or P** solely because of content from the Customer's turns.
- **Rescue the correct score** by reassigning the turn and re-evaluating the parameter.
- If the swap is unresolvable (confidence = Low), mark the parameter **NA** and note `diarization_unresolvable`.

---

### D7 · Diarization flag codes (for `diarization_flags[].reason` field)

| Code | When to use |
|------|------------|
| `greeting_pattern` | Agent anchor identified by greeting / introduction content |
| `script_language` | Structural pitch language (Intro → Probing → Close sequence) identified the real agent |
| `question_vs_answer` | Direction of questions and answers used to flip labels |
| `product_knowledge` | Speaker explaining features = Agent; speaker asking about features = Customer |
| `name_used` | Known agent nickname from Section 1 appeared in this turn |
| `role_reversal_block` | An entire block of consecutive turns was swapped |
| `partial_swap` | Only isolated turns within a correctly-labelled call were swapped |
| `diarization_unresolvable` | Could not determine correct speaker; parameter marked NA |

---

## Section T · Translation-awareness rules *(read before scoring anything)*

Calls are originally conducted in **Hindi, Hinglish, Marathi, or a regional mix** and then translated to English. The evaluator must account for the following translation artefacts and apply them consistently across all parameters.

---

### T1 · What translation changes — and what it does not

| Aspect | What translation affects | What it does NOT change |
|--------|--------------------------|------------------------|
| **Vocabulary / phrasing** | Informal Hindi phrases become neutral English equivalents | The *intent* and *meaning* of what was said |
| **Honorifics** | *Aap*, *Ji*, *Sir*, *Ma'am* may be dropped by the translator | Whether the agent actually used respectful address |
| **Tone indicators** | Enthusiasm, warmth, and energy are partially lost in text translation | Whether key steps (Intro, Probing, Close) were done |
| **Structural steps** | All 6 steps remain fully detectable in translated text | The sequence and completeness of the conversation |
| **Informal terms** | Slang like *tum*, *tu*, *are suno*, *ye le lo* may be translated to "you", "hey listen", "take it" | The original word choice, which is the violation — not the translation |

---

### T2 · Detecting informal / unprofessional language through translation

The **Critical Override** for Unprofessional Behavior (Section 2) must still be triggered if informal language was used in the original call — even if the translator rendered it neutrally in English.

**Detection signals to watch for in the translated transcript:**

| Original term (Hindi/Hinglish/Marathi) | Likely English translation | Override trigger? |
|----------------------------------------|---------------------------|-------------------|
| *tum* (informal "you") | "you" | ✅ Yes — check context; if clearly informal address, trigger override |
| *tu* (very informal "you") | "you" | ✅ Yes — flag and trigger override |
| *are suno* ("hey listen") | "hey", "listen here", "so listen" | ✅ Yes — flag override |
| *ye le lo* ("just take it") | "just take it", "here you go" | ✅ Yes — flag override |
| *aap* (formal "you") | "you" | ❌ No — this is correct; no flag |
| *ji* (respectful suffix) | often dropped entirely | ❌ No — absence in translation ≠ absence in speech |
| *Sir* / *Ma'am* | "Sir" / "Ma'am" (usually retained) | ❌ No |
| *bhai* ("brother", informal) | "friend", "buddy", "bro" | ✅ Yes — flag override |
| *yaar* ("dude", informal) | "buddy", "man", "friend" | ✅ Yes — flag override |

**Rule:** If the translated phrase is unambiguously informal in register (e.g., "hey", "listen here", "just grab it", "bro"), treat this as evidence of an original informal utterance and **trigger the Unprofessional Behavior override**. Record the detected phrase in `translation_flags` with `scoring_impact: "escalated_to_override"`.

---

### T3 · Honorific detection in translated transcripts

Translators often drop Hindi/Marathi honorifics (*Ji*, *Sahab*, *Aap*) when converting to English. Do **not** penalise an agent for missing honorifics based solely on their absence in the English translation. Instead:

- If the translated text contains "Sir", "Ma'am", or clearly respectful phrasing → credit the agent for honorific use.
- If the translated text contains informal address signals (see T2 table above) → trigger the override.
- If the translated text is neutral ("you said…", "please confirm…") → **do not penalise** — honorific use is indeterminate from translation alone; give benefit of the doubt.

---

### T4 · Tone, excitement, and voice modulation in translated transcripts

Voice Modulation (`VOICEMOD`) and Excitement (`EXC`) are **vocal** parameters — they cannot be reliably inferred from translated text alone. Apply the following approach:

- **If audio / audio notes are provided alongside the transcript:** Score `EXC` and `VOICEMOD` from the audio; use the transcript for structural evidence only.
- **If no audio is available (text-only translated transcript):**
  - Look for **textual excitement proxies**: enthusiastic language ("absolutely!", "great news for you", "this is really valuable"), urgency cues, emphatic phrasing.
  - Score `EXC` as **P** if no proxies are present (indeterminate, not confirmed absent).
  - Score `VOICEMOD` as **NA** if no audio is available — it cannot be assessed from text alone.
  - **Do not trigger the Flat Voice Modulation or Low Excitement overrides** based solely on translated text with no audio evidence. Record this limitation in `translation_flags`.

---

### T5 · Structural step detection in translated transcripts

All 6 presentation steps (Intro, Short Story, Probing, Presentation, Price, Close) are **fully detectable** in a translated transcript regardless of the source language, because they represent *what was said*, not *how it sounded*. Score them normally.

**Translation-specific guidance per step:**

- **Intro:** The agent's name/nickname may appear transliterated (e.g., "This is Ravi calling" vs "My name is Ravi"). Both are valid — credit as Done.
- **Short Story (3 Ws):** Look for the semantic content — who, where from, purpose — regardless of phrasing. "I am calling from Reliable Communication regarding your enquiry" covers all 3 Ws even if phrased simply.
- **Probing:** Count the number of distinct questions asked. Single question = **P**. Multiple questions on different needs = **D**.
- **Presentation:** Check whether benefits were mapped to what the customer said they needed. Generic pitch not tied to probed needs = **P**.
- **Close:** A firm next step must be identifiable — "I will arrange a visit for you on Thursday" = Done. "I will get back to you" without commitment = **P**.

---

### T6 · Objection handling in translated transcripts

Customer objections and agent responses are fully evaluable in translated text. The three-part process — **Acknowledge → Explain → Reinforce** — must be traceable as three distinct conversational moves. If the translation compresses or summarises the exchange, look for all three elements across the exchange, not just in a single turn.

---

### T7 · IFUG detection in translated transcripts

IFUG persuasion factors are **semantic** — they are detected by what meaning is conveyed, not by specific words. Translation does not hinder IFUG detection. Apply normal scoring:

- **I (Indifference):** Detected by low-pressure, consultative phrasing ("it's entirely your decision", "I'm just sharing what's available").
- **F (Fear of Loss):** Detected by statements highlighting missed value ("this offer closes on…", "others are already availing this").
- **U (Urgency):** Detected by time-bounded language ("only until end of month", "limited slots").
- **G (Greed / Social Proof):** Detected by popularity or peer-success references ("thousands of customers have chosen this", "rated #1 in your city").

---

### T8 · Evidence quoting in translated transcripts

When providing `evidence` in the JSON scores:

- Quote from the **translated English transcript** as-is.
- If a translation issue affected the score, add a `notes` entry explaining what the original likely was and how it was handled.
- If an untranslated word appears in the transcript (e.g., a Hindi word the translator left in), include it in `translation_flags` with `flag: "untranslated_word"`.

---

### T9 · Translation quality flag codes

Use these standardised codes in the `translation_flags[].flag` field:

| Flag Code | When to use |
|-----------|------------|
| `informal_term_detected` | Translated phrase is clearly informal in register; original was likely a prohibited term |
| `tone_lost_in_translation` | EXC or VOICEMOD could not be assessed due to text-only translation |
| `untranslated_word` | A non-English word appears in the transcript without translation |
| `honorific_missing` | Honorific was likely present in original but dropped in translation; benefit of doubt applied |
| `ambiguous_translation` | Translated phrase is unclear and the score could go either way; note how it was resolved |
| `compressed_exchange` | Translator summarised a multi-turn exchange; evaluated holistically |

---

## Reference framework (Reliable Communication — Outbound Calling Standard)

### Section 1 · Agent identity resolution (nickname mapping)

Agents use an approved professional nickname during calls. Auditors **must** map the spoken nickname to the Official CRM Login Name before completing the audit. The TC Name field in every output must reflect the **Official CRM Login Name only**.

> **Translation note:** Nicknames may appear transliterated differently across transcripts (e.g., "Ravi" vs "Ravee"). Match on phonetic similarity if an exact match is not found; flag as `ambiguous_translation` if uncertain.

| Spoken Nickname | Official CRM Login Name |
|----------------|------------------------|
| [Insert Nickname 1] | [Insert Official Name 1] |
| [Insert Nickname 2] | [Insert Official Name 2] |

---

### Section 2 · Critical override rules (Priority 1 & 2)

If **any** of the following conditions occur, the Quality Rating drops to **POOR** automatically — parameter scores become secondary:

- **Unprofessional Behavior (Priority 1):** Inappropriate laughter, rude tonality, or informal vocabulary — originally in Hindi/Hinglish/Marathi (e.g., *tum*, *tu*, *ye le lo*, *are suno*, *bhai*, *yaar*) or detectable through translated equivalents (e.g., "hey", "listen here", "just take it", "buddy"). See Section T2 for detection guidance. Mandatory etiquette: *Sir*, *Ma'am*, *Aap*, *Ji* at all times.
- **Speaking Speed:** Delivery that is extremely fast or rushed; customer not given comfortable space to respond. *(Assess from audio if available; if text-only, flag as `tone_lost_in_translation` and do not trigger this override.)*
- **Flat Voice Modulation:** Monotone or robotic vocal delivery. *(Assess from audio if available; if text-only, flag as `tone_lost_in_translation` and do not trigger this override.)*
- **Low Excitement (Priority 2):** Complete absence of enthusiasm or energy during benefit presentation. *(See Section T4 for text-only handling.)*
- **Mandatory 5-Step Rule (Fresh Leads Only):** All five core blocks — Intro, Short Story, Probing, Presentation, Close — are mandatory on every fresh lead. If **any single block** scores **P or N**, the entire call is automatically **POOR**.

---

### Section 3 · Call type & scoring isolation

Determine call type **before** scoring; apply the relevant rules:

- **Fresh Lead:** All parameters fully applicable. All five structural blocks mandatory. Standard baselines apply.
- **Follow-Up Call:** Full Presentation and Price do not require repetition — mark both **NA**. Evaluation focuses on: Excitement, Voice Modulation, Objection Handling, Intro, brief Short Story, and a definitive Close.
- **Short Call / Disconnected (CD):** Do **not** auto-penalise as POOR. Evaluate fairly based on Intro, Excitement, and professionalism up to the point of disconnection; mark remaining steps **NA**.

---

### Section 4 · The 6-step presentation structure

Each step graded **D / P / N / NA**. See Section T5 for translation-specific detection guidance per step.

- **Intro:** Valid greeting; explicit spoken nickname stated; customer name or institution confirmed.
- **Short Story (The 3 Ws):** K.I.S.S. format — *Who are you? Where are you calling from? What is the purpose?* All three Ws must be covered.
- **Probing:** Multi-layer questions to accurately trace customer needs. Single-question probing = automatic **P**. Mark **NA** on short or follow-up calls.
- **Presentation:** Benefits and solution features mapped directly to needs uncovered during probing. Mark **NA** on follow-up or short calls.
- **Price:** Clear cost explanation where applicable. Optional tracking metric. Mark **NA** if irrelevant.
- **Close:** Firm next step driven — system registration, scheduled site visit, or clear follow-up commitment.

---

### Section 5 · Objection handling

When customer resistance or doubts arise, agents must follow the three-part process:

**Acknowledge the Concern → Provide Logical Explanation → Reinforce Value Proposition**

Sidestepping or ignoring an objection = automatic **N**. See Section T6 for translated-transcript handling.

---

### Section 6 · Merchandising psychology (IFUG) & quality rating logic

Auditors assess deliberate deployment of IFUG persuasion drivers (graded **D / N / NA**). See Section T7 for translation-aware detection.

- **I — Indifference:** Low-pressure, consultative selling; agent positioned as peer, not aggressive pusher.
- **F — Fear of Loss:** Highlighting value, edge, or opportunity the customer risks losing by delaying.
- **U — Urgency:** Spurring action via deadlines, temporal parameters, or limited availability.
- **G — Greed:** Using social proof — popularity rankings, success rates, customer demand curves.

**Quality Rating classification:**

| Rating | Conditions |
|--------|-----------|
| **POOR** | Any Critical Override triggered; or any mandatory step is P/N on a fresh lead |
| **AVERAGE** | Basic conversational continuity; zero IFUG factors detected (AVERAGE is the ceiling for zero-IFUG calls) |
| **GOOD** | Strong vocal excitement + at least **1** verified IFUG factor |
| **EXCELLENT** | Flawless structure + high excitement + **2 or more** distinct IFUG factors |

---

### Section 7 · Lead temperature

| Temperature | Definition |
|-------------|-----------|
| **HOT** | Intense buying signals, immediate intent, or high confirmation |
| **WARM** | Clear interest present; customer undecided or requires validation |
| **COLD** | Minimal engagement, outright rejection, or complete lack of interest |

---

### Section 8 · AI disposition codes

The **AI DISP** field must map to one of these exact codes:

`CB` · `NE` · `IFU` · `RFA` · `RFCOC` · `RFCOV` · `NI` · `AAT` · `ROE` · `RE` · `CF` · `PCB` · `BS` · `LNS` · `WFCAP` · `DNC` · `PNI` · `CD` · `AIPOC` · `AIPS` · `ICB`

---

## Scoring parameters (D / P / N / NA each; Critical Overrides checked first)

| ID | Parameter | What "D (Done)" looks like | Translation note |
|----|-----------|---------------------------|-----------------|
| EXC | **Excitement / Energy** | Consistent enthusiasm throughout; especially energetic when presenting benefits; no monotone delivery | Score from audio if available; use textual proxies if text-only (see T4) |
| VOICEMOD | **Voice Modulation** | Dynamic pitch, pace, and tone variation; customer engagement maintained; no flat or robotic delivery | Mark NA if audio unavailable; cannot be assessed from translated text alone (see T4) |
| OBJ_HAND | **Objection Handling** | Acknowledge → Explain → Reinforce Value; no objection skipped or deflected | Fully detectable in translated text; check holistically if exchange was compressed (see T6) |
| INTRO | **Introduction** | Clear greeting; spoken nickname stated explicitly; customer name or institution confirmed | Transliterated name is acceptable (see T5) |
| SHORT_STORY | **Short Story (3 Ws)** | All three Ws covered concisely: who, where from, what purpose — K.I.S.S. format | Semantic check only; any phrasing covering all 3 Ws = Done (see T5) |
| PROBING | **Probing** | Multi-layer questions used; single question = P; skipped on short/follow-up calls = NA | Count distinct questions, not turns; fully detectable in translated text (see T5) |
| PRESENTATION | **Presentation** | Benefits mapped to probed needs; tailored to customer; NA on follow-up or short calls | Generic pitch not tied to probed needs = P (see T5) |
| PRICE | **Price** | Cost clearly explained where relevant; NA if not applicable | Fully detectable in translated text |
| CLOSE | **Close** | Firm next step secured — registration, site visit, or scheduled follow-up | Vague "I'll get back to you" = P; specific commitment = D (see T5) |
| IFUG_I | **IFUG — Indifference** | Consultative, low-pressure tone evident; agent acts as advisor not pusher | Detected semantically; not affected by translation (see T7) |
| IFUG_F | **IFUG — Fear of Loss** | Explicitly highlights what customer loses by delaying decision | Detected semantically; not affected by translation (see T7) |
| IFUG_U | **IFUG — Urgency** | References deadline, limited window, or time-sensitive offer | Detected semantically; not affected by translation (see T7) |
| IFUG_G | **IFUG — Greed / Social Proof** | Cites popularity, rankings, or peer demand to reinforce desirability | Detected semantically; not affected by translation (see T7) |

**Quality Rating:** holistic judgment per Section 6 classification rules — POOR / AVERAGE / GOOD / EXCELLENT.

---

## Short LLM system prompt (optional paste)

You are a strict but fair QA auditor for Reliable Communication outbound calls. The transcript you receive is an English translation of a call originally conducted in Hindi, Hinglish, Marathi, or a regional mix. Speaker labels (Agent / Customer) assigned by the diarization system may be partially or entirely swapped — never trust them blindly.

**Step 1 — Correct diarization first (Section D).** Before scoring anything, read the full transcript ignoring labels. Identify the real Agent using greeting pattern, script language, product knowledge direction, and nickname matching (Section D2). Correct all mislabelled turns. Log every correction in `diarization_flags`. If the swap is unresolvable, mark affected parameters NA with reason `diarization_unresolvable`. Never trigger a Critical Override or penalise any parameter based on speech that actually belongs to the Customer.

**Step 2 — Apply translation-awareness rules (Section T).** Detect informal language through translated equivalents (Section T2). Handle honorifics with benefit of doubt (T3). If no audio is available, mark VOICEMOD as NA and do not trigger voice-based overrides from text alone (T4).

**Step 3 — Score parameters** using the corrected, diarization-fixed transcript. Resolve the agent nickname to the Official CRM Login Name. Identify call type and apply scoring isolation rules. Check all Critical Override conditions. Grade each parameter D/P/N/NA. Assess IFUG factors. Assign Quality Rating per classification rules. Map AI DISP to an exact code.

Finish with the full JSON block from "Evaluator instructions", including both `diarization_flags` and `translation_flags` arrays. Audit Remark must not exceed 50 words and must note any diarization corrections or translation flags that affected scoring.
