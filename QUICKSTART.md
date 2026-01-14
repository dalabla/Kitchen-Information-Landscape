# Quick Start - Get Testing in 2 Minutes

## Setup

1. **Set your API key**
   ```bash
   cp .env.example .env
   nano .env  # Add your Anthropic API key
   ```

2. **Install & Run**
   ```bash
   npm install
   npm start
   ```

3. **Open & Test**
   - Go to: http://localhost:3000
   - Click the 🤖 button (bottom right)
   - Try it out!

## First Tests to Run

### Test 1: Smart Suggestions (30 seconds)
1. Leave everything at 0% complete
2. Click "✨ Get Smart Suggestions"
3. See what AI recommends starting with

**Good sign**: Suggests long-cooking items first (braising, rendering)
**Bad sign**: Generic/random suggestions

---

### Test 2: Context Awareness (1 minute)
1. Mark a few items complete (click them)
2. Click "Get Smart Suggestions" again
3. See if suggestions change

**Good sign**: AI adapts based on what's done
**Bad sign**: Same suggestions regardless of progress

---

### Test 3: Natural Questions (2 minutes)
Open chat and ask:
- "What should I start with if service is in 3 hours?"
- "How long does braising cabbage take?"
- "Can I prep crispy onions ahead?"

**Good sign**: Helpful, specific answers
**Bad sign**: Generic or wrong information

---

## What to Watch For

### ✅ Success Signals
- You naturally reach for it
- Answers are faster than Google
- Suggestions change your workflow
- You'd miss it if it was gone

### ❌ Kill Signals
- Takes longer than just working
- You avoid using it
- Suggestions are ignored
- Creates cognitive overhead

---

## Quick Troubleshooting

**"Server won't start"**
- Check Node version: `node --version` (need 18+)
- Install deps: `npm install`

**"Chat doesn't respond"**
- Check .env has ANTHROPIC_API_KEY
- Check browser console for errors
- Verify server is running on port 3000

**"API errors"**
- Verify API key is valid
- Check rate limits on Anthropic console
- Look at server logs for details

---

## After Testing

1. **Document in TESTING.md**
   - What worked / what didn't
   - Usage frequency
   - Time impact

2. **Decide**
   - Keep feature
   - Iterate/improve
   - Kill feature

3. **Next iteration**
   - If useful → Add proactive features
   - If not → Kill and learn why

---

## Real Service Prep Test

The ultimate validation:

**Before Service**
- Start mise from zero
- Use AI to guide task order
- Ask questions as they come up
- Time yourself

**After Service**
- Compare to baseline prep time
- Count how many times AI was consulted
- Note what was helpful vs. ignored

**Be Honest**
- Would you use it again?
- Did it save time or waste it?
- Would you recommend to another cook?

If the answer to all three is "no" → Kill it and move on.

---

## Need Help?

Check:
1. README.md - Full documentation
2. TESTING.md - Detailed test protocols
3. Server logs - For API errors
4. Browser console - For frontend errors

---

## Remember

This is an **experiment**, not a product.

- Ship fast ✅
- Test honestly ✅
- Kill ruthlessly ✅
- Learn always ✅

The goal isn't to build features.
The goal is to find out if AI can actually help kitchens.

**Now go test it during real prep. 👨‍🍳**
