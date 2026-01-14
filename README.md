# Kitchen AI Assistant - Experimental Build

An experimental full-stack application testing whether Claude AI can meaningfully improve back-of-house kitchen mise en place workflows.

## 🎯 Core Hypothesis

**"Can conversational AI reduce prep time and improve kitchen efficiency, or is it just digital clutter?"**

This is a rapid-prototyping project to test AI assistance in time-pressured kitchen environments. Every feature is an experiment - ship fast, measure honestly, kill ruthlessly, scale what works.

## 🧪 What We're Testing

### Phase 1: Basic AI Integration (Current)
- **Hypothesis**: Kitchen staff will ask the AI for help with timing, sequencing, and techniques
- **Success Metric**: Do people actually use the chat, or ignore it after the first day?
- **Features**:
  - Context-aware chat (AI knows your current prep progress)
  - Smart suggestions based on what's done/remaining
  - Conversational interface for technique questions

### Future Phases (Only if Phase 1 proves useful)
- **Phase 2**: Proactive timing warnings ("Start braising cabbage now - takes 45min")
- **Phase 3**: Voice interface for hands-free operation
- **Phase 4**: Predictive prep sequencing based on service time

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

3. **Start the server**
   ```bash
   npm start
   ```

4. **Open the app**
   - Navigate to `http://localhost:3000`
   - Click the AI assistant button (bottom right)
   - Start testing

## 🏗️ Architecture

### Tech Stack
- **Frontend**: Vanilla HTML/CSS/JavaScript (no framework bloat - need it fast)
- **Backend**: Node.js + Express
- **AI**: Claude Sonnet 4 via Anthropic API
- **State**: LocalStorage (client-side) + In-memory conversations (server-side)

### Why This Stack?
- **Speed**: Zero build process, instant iteration
- **Focus**: Testing AI utility, not engineering architecture
- **Simplicity**: Easy to modify and kill features quickly

## 💡 Current Features

### AI Chat Panel
- Toggle with bottom-right button
- Conversational interface for kitchen questions
- Context-aware (AI sees your current progress)
- Example queries:
  - "What should I start with?"
  - "How long does braising cabbage take?"
  - "Can I prep the crispy onions in parallel with anything?"
  - "What's the technique for rendering dates?"

### Smart Suggestions
- Click "Get Smart Suggestions" button
- AI analyzes your current progress
- Suggests next tasks based on:
  - What takes longest (do first)
  - What can be parallelized
  - Dependencies between tasks

### Mise en Place Tracker
- Beautiful visual checklist
- Progress tracking
- Shared ingredient highlighting
- State persistence across sessions

## 📊 Measuring Success

### Usage Metrics to Track (Manual for now)
- [ ] How often do I actually open the chat?
- [ ] What questions do I ask most frequently?
- [ ] Do suggestions change my task order?
- [ ] Does AI save time or create friction?
- [ ] Do I ignore certain features?

### Kill Criteria
If after 2 weeks of real prep sessions:
- Chat is rarely opened → Kill the feature
- Suggestions are ignored → Kill smart suggestions
- Same questions asked repeatedly → Need better proactive features
- Takes longer than just doing the work → Kill the whole thing

### Scale Criteria
If AI genuinely helps:
- Expand to other prep lists (pasta, butchery, etc.)
- Add proactive features (timing warnings)
- Consider voice interface for hands-free
- Test with other kitchen staff

## 🔧 Development

### File Structure
```
├── index.html          # Main UI with mise tracker + AI chat
├── server.js           # Express server + Claude API integration
├── package.json        # Dependencies
├── .env               # API keys (not committed)
└── README.md          # This file
```

### Making Changes
1. **UI changes**: Edit `index.html` directly, refresh browser
2. **Backend changes**: Edit `server.js`, server auto-restarts with `--watch` flag
3. **Test immediately**: No build process, instant feedback

### Adding New Features
Ask yourself first:
- **What hypothesis does this test?**
- **How will I know if it works?**
- **Can I build it in < 2 hours?**

If you can't answer these, don't build it yet.

## 🗑️ Features That Got Killed

_(Nothing yet - this is v0.1)_

Document failed experiments here to avoid rebuilding them.

## 📝 Learning Log

### Build Notes
- Started with beautiful static checklist (already built)
- Added Claude API backend (30 min)
- Integrated chat panel into UI (45 min)
- Total time to v0.1: ~90 minutes

### Hypotheses to Validate
1. **Will I actually use conversational AI during real prep?**
   - Status: Untested
   - Next: Use during actual roast prep session

2. **Are smart suggestions better than my own task sequencing?**
   - Status: Untested
   - Next: Compare AI suggestions vs. my default order

3. **Does context-aware chat add value over generic ChatGPT?**
   - Status: Untested
   - Next: Try both and compare utility

## 🤔 Open Questions

- Is chat the right interface? (vs. voice, vs. proactive notifications)
- Should AI suggest equipment setup order too?
- Can AI learn from my actual completion times to improve suggestions?
- Would this work for other cooks, or just me?

## 📜 License

Experimental project - use however you want. No warranty that this actually helps kitchens.

## 🙋 Questions?

This is a personal experimental build. If you're adapting it for your own kitchen:
- Start with your actual prep list (edit `prepData` in `index.html`)
- Test with real service prep, not hypotheticals
- Kill features that don't help
- Share learnings
