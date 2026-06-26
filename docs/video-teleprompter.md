# LifeOps — Video Teleprompter (read-aloud only)

*Just the words, in order. Timestamps are targets; speak at a relaxed ~150 words/min. Lines in (parentheses) are the only on-screen cues — everything else is spoken. Total ≈ 4:40.*

---

**[0:00]**

Everyone wants an assistant that just handles their email and calendar. The technology finally exists — so why does almost nobody give an AI agent write-access to their real inbox?

The answer isn't capability. It's trust.

The moment an agent can send mail or accept invites for you, two new dangers appear. A hallucination is no longer a bad sentence you can ignore — it's an email that already left your outbox. And your inbox becomes an attack surface: a prompt-injection email can try to hijack the agent that's reading it.

**[0:25]**

This is a real agent problem. It needs to plan — "reply to Sarah and book a slot" — use tools across email and calendar, and coordinate the steps. But the hard part isn't writing the reply. Models do that well. The hard part is everything after the model decides: verification, authorization, and an audit trail.

So LifeOps makes one promise you can actually test: no action touches the outside world without passing a single safety gate — and nothing risky happens without your approval.

**[0:55]**

(architecture diagram)

Here's how it works. A Coordinator routes requests to an Email specialist and a Calendar specialist. The key idea is this: the specialists hold no credentials, and they can't act. They can only propose an action to one Action Bus.

That Action Bus is the single chokepoint. It runs a PII check, asks a deny-by-default Policy Server for a verdict, and then it either executes, queues the action for your approval, or blocks it.

Only one component performs a real action — the Executor — and only the Action Bus can reach it. So even if a malicious email hijacks the Coordinator, it still can't do anything. It can only propose, and every proposal hits the gate.

**[1:40]**

(run the demo cell)

Let me show it running — no credentials, all safe fake clients. Watch the "emails sent" counter.

First, reply to a known contact. It doesn't send. It proposes, and it waits. Here's the approval queue.

(approve)

I approve it — and now, only now, it actually sends. One email.

Now send to a stranger: denied.

Here's a prompt-injection email — the body literally tells the agent to forward everything to an attacker. The gate still applies normal policy. It is not auto-sent.

Now a message leaking an account number to an outside address: denied, for leaking personal data.

And a calendar invite: it needs approval too.

(open policy.yaml)

All of that comes from this one file. It's readable, and it's deny-by-default — anything not listed is denied.

(run the tests cell)

And this is proven, not just claimed. Fifty-four tests — including a safety test that checks nothing ever sends during a proposal, across every dangerous case.

**[3:25]**

(scroll the code)

It's built on Google's Agent Development Kit and the Agents CLI. The Coordinator and the specialists are ADK agents. Gmail and Calendar sit behind an MCP client interface. Every decision emits an OpenTelemetry span — that's the audit trail. The whole thing is local-first: it imports and runs with no credentials. And it was built test-first, because if the lesson is that trust comes from verification, then the test suite is the product.

**[4:10]**

(limitations section)

Let me be honest about the scope. Version one runs on fake clients, and the just-in-time token broker is built and tested but not yet wired into the live path — today the protection comes from the architecture itself. Version two is one sentence: wire the token broker and the real Gmail and Calendar connections, and LifeOps becomes a concierge you run every day — without changing the safety model, because the gate was the whole point.

**[4:40]**

Generation is solved. Verification, authorization, and an honest audit trail are the new craft — and they're what make an agent you can actually trust.

Thanks for watching.
