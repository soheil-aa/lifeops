# LifeOps — Video Teleprompter (plain English, read-aloud)

*Simple words, short sentences. Read it like you're explaining it to a friend. Timestamps are targets; (parentheses) are the only on-screen cues. Total ≈ 4:30.*

---

**[0:00]**

Imagine an assistant that takes care of your email and your calendar for you. We finally have the technology to build it. But most people would never let an AI near their real inbox.

Why? It's not that it can't do the work. It's that they don't trust it.

The second an assistant can send an email or accept a meeting for you, a mistake isn't just a bad sentence anymore. It's a real email that already went out. And a scam email sitting in your inbox could even try to trick the assistant into doing something bad.

**[0:30]**

So this is a real job for an AI agent. It has to make a plan — like "reply to Sarah and find a time to meet" — and use your email and calendar to do it.

But writing a nice reply is the easy part. The hard part is everything that comes after: making sure the action is safe, and only doing it with your okay.

That's the whole idea behind LifeOps. It makes one simple promise. It never does anything in the real world without passing one safety check first. And it never does anything risky without asking you.

**[1:00]**

(show the diagram)

Here's how it works. A main assistant passes your request to two helpers — one for email, one for calendar. The key part: these helpers can't actually do anything on their own. All they can do is suggest an action.

Every suggestion goes to one place. Think of it as a single gate. The gate checks for private information, checks the rules, and then does one of three things: it does the action, it asks you first, or it blocks it.

Only one part of the system is allowed to actually send or book anything — and it only listens to the gate. So even if a scam email tricks the assistant, it still can't do anything. It can only make a suggestion, and every suggestion goes through the gate.

**[1:45]**

(run the demo)

Let me show you. This is running live, with no real accounts, so it's completely safe. Keep an eye on the "emails sent" number.

First, a reply to someone I know. It doesn't send it. It suggests it, and waits. Here's the list of things waiting for me.

(approve)

I approve it — and now, only now, it actually sends. One email.

Now, an email to a stranger: blocked.

Here's a scam email. The text literally tells the assistant to forward all my mail to someone else. The gate still does its normal check. It does not send it.

Now an email with a bank card number going to an outsider: blocked, because it would leak private information.

And a meeting invite: it asks me first.

(show the rules file)

All of these rules live in one simple file you can just read. If something isn't on the list, it's blocked by default.

(run the tests)

And this isn't just talk. There are 54 automatic tests that prove it — including one that checks nothing ever gets sent without my approval.

**[3:30]**

(scroll the code)

It's built using Google's tools for making AI agents. Email and calendar connect through a standard plug-in system. Every decision gets logged, so you can always see what the assistant did and why. And the whole thing runs on your own computer, with no passwords needed just to try it. I built it test-first, because the real value here isn't writing the email — it's being able to trust it.

**[4:10]**

(show the limitations)

Let me be honest about what's done and what's next. Right now it runs on safe pretend accounts, and one of the security pieces is built and tested but not fully connected yet. The next version is simple: hook it up to real Gmail and Calendar, and it becomes something you'd actually use every day — without changing how the safety works, because the safety was the point from the start.

**[4:40]**

Getting an AI to write something is easy now. The real skill is making one you can actually trust to act for you. That's what LifeOps is about.

Thanks for watching.
