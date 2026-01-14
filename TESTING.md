# Testing Guide - Kitchen AI Assistant

## 🧪 Experiment Protocol

This is a **living document** to track learnings from real kitchen testing.

## Pre-Test Setup

### Test Environment
- [ ] Server running on localhost:3000
- [ ] Anthropic API key configured
- [ ] Browser dev console open (check for errors)
- [ ] Notepad ready for observations

### Baseline Workflow (Control)
Before using AI assistance, document your normal prep workflow:
1. What order do you naturally prep tasks?
2. How long does full mise typically take?
3. What do you usually forget or do inefficiently?

## Test Scenarios

### Scenario 1: Cold Start (No Progress)
**Hypothesis**: AI suggestions help prioritize when starting from zero

**Test**:
1. Open app with 0% completion
2. Click "Get Smart Suggestions"
3. Record the suggestions
4. Compare to your natural order

**Questions**:
- Did AI suggest something you wouldn't have thought of?
- Is the suggested order more logical than yours?
- Would you actually follow it?

---

### Scenario 2: Mid-Prep (50% Complete)
**Hypothesis**: AI adapts suggestions based on current progress

**Test**:
1. Mark ~50% of items complete
2. Click "Get Smart Suggestions"
3. See if suggestions change based on what's done

**Questions**:
- Does AI recognize what's already done?
- Are suggestions context-aware?
- Do they account for remaining time/dependencies?

---

### Scenario 3: Conversational Queries
**Hypothesis**: Chat is faster than looking up techniques/timing

**Test Queries**:
- "How long does braising cabbage take?"
- "Can I prep crispy onions ahead of time?"
- "What's the best way to render dates?"
- "What should I prep first if service is in 2 hours?"

**Questions**:
- Are answers accurate and helpful?
- Is asking faster than searching online?
- Would you use this hands-free while prepping?

---

### Scenario 4: Real Service Prep
**THE BIG TEST**: Use during actual service prep

**Protocol**:
1. Start mise from zero
2. Use AI suggestions to guide order
3. Ask questions as they come up
4. Track any time saved/wasted

**Metrics**:
- Total prep time vs. baseline
- Number of times AI was consulted
- Number of times AI suggestions were followed
- Number of times AI was ignored

---

## Observation Template

After each test session, fill this out:

### Session Info
- **Date**: _______
- **Duration**: _______
- **Completion %**: _______

### AI Usage
- Times chat opened: _______
- Questions asked: _______
- Suggestions requested: _______
- Suggestions followed: _______

### Qualitative Notes

**What worked well:**
-
-
-

**What was annoying:**
-
-
-

**Unexpected behaviors:**
-
-
-

**Would I use this again?** YES / NO / MAYBE

**Why or why not?**


---

## Decision Checkpoints

### After 5 Test Sessions

Review and decide:

**Chat Feature**
- [ ] KEEP - Used frequently and helpful
- [ ] ITERATE - Used but needs improvement
- [ ] KILL - Rarely used or not helpful

**Smart Suggestions**
- [ ] KEEP - Changes behavior for the better
- [ ] ITERATE - Good idea, poor execution
- [ ] KILL - Ignored or unhelpful

**Next Features to Try**
- [ ] Proactive timing alerts
- [ ] Voice interface
- [ ] Multi-day prep planning
- [ ] Custom prep lists
- [ ] None - kill the whole thing

---

## Red Flags (Immediate Kill Signals)

Stop testing and kill the feature if:
- ❌ AI takes longer than just doing the work
- ❌ Suggestions are consistently wrong
- ❌ You naturally avoid using it
- ❌ It creates more cognitive load than value
- ❌ You'd be embarrassed to show another cook

---

## Success Signals (Scale Up)

Expand the project if:
- ✅ You naturally reach for it during prep
- ✅ It changes your workflow for the better
- ✅ You'd miss it if it was gone
- ✅ Other cooks ask to use it
- ✅ Measurable time savings

---

## Future Experiment Ideas

If Phase 1 succeeds, test:

### Voice Interface
- **Hypothesis**: Hands-free is crucial in a kitchen
- **Test**: Add speech-to-text for queries while hands are dirty

### Timing Predictions
- **Hypothesis**: AI can learn your pace and predict completion times
- **Test**: Track actual vs. estimated completion times

### Multi-Station Prep
- **Hypothesis**: AI can coordinate parallel work across stations
- **Test**: Expand to multi-cook scenarios

### Adaptive Learning
- **Hypothesis**: AI improves suggestions based on your actual workflow
- **Test**: Track completion order and feed back to model

---

## Notes Section

Use this space for freeform observations:

```
[Date] [Time] - Observation
Example: 2026-01-15 10:30 - AI suggested starting with cabbage braise first.
This was smart - I usually forget it takes 45min and scramble at the end.
```
