# LifeOps — 5-Minute Capstone Video Script

**Format:** screen recording (notebook + one architecture slide) with voiceover. 1080p, YouTube, **must be ≤5:00**. Aim for 4:30 to leave margin.
**Covers the rubric:** Problem · Why agents · Architecture · Demo · The Build.

Each scene below: **[SHOW]** = what's on screen, **[SAY]** = read this aloud (plain English, ≈150 words/min).
*(For a pure read-aloud version with no stage directions, use `docs/video-teleprompter-plain.md`.)*

---

### 0:00–0:30 · Hook + problem
**[SHOW]** Title card: "LifeOps — a personal assistant you can actually trust to act for you." Then a normal email inbox.
**[SAY]** "Imagine an assistant that takes care of your email and your calendar for you. We finally have the technology to build it. But most people would never let an AI near their real inbox. Why? It's not that it can't do the work — it's that they don't trust it. The second an assistant can send an email or accept a meeting for you, a mistake isn't just a bad sentence anymore. It's a real email that already went out. And a scam email in your inbox could even try to trick the assistant into doing something bad."

### 0:30–1:00 · Why agents
**[SHOW]** Architecture slide, dimmed except the two helpers.
**[SAY]** "So this is a real job for an AI agent. It has to make a plan — like 'reply to Sarah and find a time to meet' — and use your email and calendar to do it. But writing a nice reply is the easy part. The hard part is everything after: making sure the action is safe, and only doing it with your okay. That's the whole idea behind LifeOps. It makes one simple promise: it never does anything in the real world without passing one safety check first, and it never does anything risky without asking you."

### 1:00–1:45 · Architecture
**[SHOW]** Full architecture diagram. Trace the path with your cursor as you talk.
**[SAY]** "Here's how it works. A main assistant passes your request to two helpers — one for email, one for calendar. The key part: these helpers can't actually do anything on their own. All they can do is suggest an action. Every suggestion goes to one place — think of it as a single gate. The gate checks for private information, checks the rules, and then does one of three things: it does the action, it asks you first, or it blocks it. Only one part of the system is allowed to actually send or book anything, and it only listens to the gate. So even if a scam email tricks the assistant, it still can't do anything — it can only make a suggestion, and every suggestion goes through the gate."

### 1:45–3:30 · Demo (the core — let it breathe)
**[SHOW]** The Kaggle notebook. Briefly scroll the install cell (already run, fast-forward), then **run the demo cell** and let the output appear.
**[SAY]** "Let me show you. This is running live, with no real accounts, so it's completely safe. Keep an eye on the 'emails sent' number."
- **[SHOW]** Point to each demo line as it scrolls.
- **[SAY]** "First, a reply to someone I know. It doesn't send it — it suggests it, and waits. Here's the list of things waiting for me. I approve it — and now, only now, it actually sends. One email. Now, an email to a stranger: blocked. Here's a scam email — the text literally tells the assistant to forward all my mail to someone else. The gate still does its normal check. It does not send it. Now an email with a bank card number going to an outsider: blocked, because it would leak private information. And a meeting invite: it asks me first."
- **[SHOW]** Open `policy.yaml`.
- **[SAY]** "All of these rules live in one simple file you can just read. If something isn't on the list, it's blocked by default."
- **[SHOW]** Run the tests cell; show `54 passed`.
- **[SAY]** "And this isn't just talk — there are 54 automatic tests that prove it, including one that checks nothing ever gets sent without my approval."
- *(Optional, if you set the `GOOGLE_API_KEY` secret)* **[SHOW]** run the live cell. **[SAY]** "And with a real AI key, the same gate runs the live version too."

### 3:30–4:10 · The build
**[SHOW]** Quick scroll of the repo file tree (app/core, specialists, tests).
**[SAY]** "It's built using Google's tools for making AI agents. Email and calendar connect through a standard plug-in system. Every decision gets logged, so you can always see what the assistant did and why. And the whole thing runs on your own computer, with no passwords needed just to try it. I built it test-first, because the real value here isn't writing the email — it's being able to trust it."

### 4:10–4:40 · Honest limitations + roadmap
**[SHOW]** The "Limitations & roadmap" section of the README/Writeup.
**[SAY]** "Let me be honest about what's done and what's next. Right now it runs on safe pretend accounts, and one of the security pieces is built and tested but not fully connected yet. The next version is simple: hook it up to real Gmail and Calendar, and it becomes something you'd actually use every day — without changing how the safety works, because the safety was the point from the start."

### 4:40–4:55 · Close
**[SHOW]** Title card with the GitHub link.
**[SAY]** "Getting an AI to write something is easy now. The real skill is making one you can actually trust to act for you. That's what LifeOps is about. Thanks for watching."

---

## Recording checklist
- **Architecture diagram:** use the ASCII diagram from the README/Writeup, or redraw it cleanly in a slide — also reuse it as the Writeup cover image.
- **Pre-run the notebook** so cells are warm; on camera, re-run only the **demo** and **tests** cells so they appear live but fast.
- **Zoom the terminal font** so demo output is readable on mobile.
- Keep talking-head optional; screen + voiceover is enough.
- **Verify length ≤ 5:00**, upload to YouTube as **Public or Unlisted** (judges must be able to watch), and paste the link into the Writeup's media gallery.
- Add **captions** (YouTube auto-captions, then proofread) for accessibility and clarity.
