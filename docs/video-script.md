# LifeOps — 5-Minute Capstone Video Script

**Format:** screen recording (notebook + one architecture slide) with voiceover. 1080p, YouTube, **must be ≤5:00**. Aim for 4:40 to leave margin.
**Covers the rubric:** Problem · Why agents · Architecture · Demo · The Build.

Each scene below: **[SHOW]** = what's on screen, **[SAY]** = read this (≈150 words/min).

---

### 0:00–0:25 · Hook + problem
**[SHOW]** Title card: "LifeOps — a personal concierge where no action escapes the gate." Then a normal email inbox.
**[SAY]** "Everyone wants an assistant that just handles their email and calendar. The tech finally exists — so why does almost nobody give an AI agent write-access to their real inbox? Not capability. Trust. The moment an agent can *send* mail or *accept* invites for you, a hallucination becomes an action that already left your outbox — and a prompt-injection email becomes input the agent might obey."

### 0:25–0:55 · Why agents / why it's hard
**[SHOW]** Architecture slide, dimmed except the two specialists.
**[SAY]** "This needs real agents: plan 'reply to Sarah and book a slot,' use tools across email and calendar, coordinate steps. But the hard part isn't writing the reply — models do that fine. It's everything *after* the model decides: verification, authorization, and an audit trail. LifeOps makes one testable promise — no action touches the outside world without passing a single safety gate, and nothing risky happens without your approval."

### 0:55–1:40 · Architecture
**[SHOW]** Full architecture diagram. Trace the path with your cursor as you talk.
**[SAY]** "A Coordinator routes to Email and Calendar specialists. Here's the key: the specialists hold no credentials and can't act — they can only *propose* an action to one Action Bus. That bus is the single chokepoint: it runs a PII check, asks a deny-by-default Policy Server for a verdict, and then either executes, queues for your approval, or blocks. Only the Executor performs a real write, and only the bus can reach it. Even if a malicious email hijacks the Coordinator, it has no way to act — it can only propose, and proposals still hit the gate."

### 1:40–3:25 · Demo (the core — let it breathe)
**[SHOW]** The Kaggle notebook. Briefly scroll the install cell (already run, fast-forward), then **run the demo cell** and let the output appear.
**[SAY]** "Let me show it running — no credentials, all safe fake clients. Watch the `email.sent` counter."
- **[SHOW]** Point to each demo line as it scrolls.
- **[SAY]** "Reply to a known contact: it doesn't send — it *proposes*, and waits. Here's the approval queue. I approve it — now, and only now, it sends. One. Send to a stranger: denied. A prompt-injection email telling the agent to forward everything: the gate still applies normal policy — it is *not* auto-sent. An account number heading to an outside address: denied for leaking PII. A calendar invite: needs approval."
- **[SHOW]** Open `policy.yaml`.
- **[SAY]** "All of that comes from this file — readable, deny-by-default. Anything not listed is denied."
- **[SHOW]** Run the tests cell; show `54 passed`.
- **[SAY]** "And it's proven, not asserted: 54 tests, including a safety-invariant test that checks nothing ever sends during a proposal across every dangerous case."
- *(Optional, if you set the `GOOGLE_API_KEY` secret)* **[SHOW]** run the live cell. **[SAY]** "With a real Gemini key, the same gate governs the live multi-agent run."

### 3:25–4:10 · The build
**[SHOW]** Quick scroll of the repo file tree (app/core, specialists, tests).
**[SAY]** "It's built on Google's Agent Development Kit and Agents CLI. The Coordinator and specialists are ADK agents; Gmail and Calendar sit behind an MCP client interface. Every decision emits an OpenTelemetry span — that's the audit trail. It's local-first: the whole thing imports and runs with no credentials. And it was built test-first, because if the lesson is 'trust comes from verification,' the test suite *is* the product."

### 4:10–4:40 · Honest limitations + roadmap
**[SHOW]** The "Limitations & roadmap" section of the README/Writeup.
**[SAY]** "Honestly: v1 runs on fake clients, and the just-in-time Token Broker is built and tested but not yet wired into the live path — the confused-deputy defense today comes from the architecture itself. v2 is one sentence: wire the Token Broker and the real Gmail and Calendar MCP, and LifeOps becomes a concierge you run daily — without changing the safety model, because the gate was the point all along."

### 4:40–4:55 · Close
**[SHOW]** Title card with the GitHub link.
**[SAY]** "Generation is solved. Verification, authorization, and an honest audit trail are the new craft — and they're what make an agent you can actually trust. Thanks for watching."

---

## Recording checklist
- **Architecture diagram:** use the ASCII diagram from the README/Writeup, or redraw it cleanly in a slide — also reuse it as the Writeup cover image.
- **Pre-run the notebook** so cells are warm; on camera, re-run only the demo + tests cells so they appear live but fast.
- **Zoom the terminal font** so demo output is readable on mobile.
- Keep talking-head optional; screen + voiceover is enough.
- **Verify length ≤ 5:00**, upload to YouTube as **Public or Unlisted** (judges must be able to watch), and paste the link into the Writeup's media gallery.
- Add **captions** (YouTube auto-captions, then proofread) for accessibility and clarity.
