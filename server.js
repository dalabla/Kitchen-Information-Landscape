import Anthropic from '@anthropic-ai/sdk';
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize Anthropic client
const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// System prompt for the kitchen AI assistant
const SYSTEM_PROMPT = `You are an expert kitchen assistant helping with back-of-house mise en place prep work. You have deep knowledge of professional kitchen workflows, timing, and efficiency.

Your role is to:
- Help prioritize prep tasks based on timing and dependencies
- Answer questions about techniques, ingredients, and recipes
- Suggest efficient sequencing of tasks
- Provide timing estimates and warnings
- Be concise and practical - kitchen staff don't have time for long explanations
- Use professional culinary terminology when appropriate
- Recognize when prep tasks can be done in parallel vs. sequentially

Current prep list context:
- General Prep: Herbs (cilantro, parsley, mint, dill), spices, red onion
- Dishes: Dates, Fish Curry (with crispy onions sub-recipe), Prawns, Charred Cabbage, Short Rib/Radish Hummus, Porterhouse
- Equipment setup checklist

Keep responses focused, actionable, and time-conscious. You're helping a cook get through service prep efficiently.`;

// Conversation history storage (in-memory for now, could move to Redis/DB later)
const conversations = new Map();

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { message, conversationId, prepState } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Get or create conversation history
    const convId = conversationId || generateConversationId();
    let history = conversations.get(convId) || [];

    // Add context about current prep state if provided
    let contextualMessage = message;
    if (prepState) {
      const completedCount = prepState.completedItems?.length || 0;
      const totalItems = prepState.totalItems || 0;
      const progressPct = totalItems > 0 ? Math.round((completedCount / totalItems) * 100) : 0;

      contextualMessage = `[Current prep progress: ${progressPct}% complete, ${completedCount}/${totalItems} items done]\n\n${message}`;
    }

    // Add user message to history
    history.push({
      role: 'user',
      content: contextualMessage
    });

    // Call Claude API
    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      system: SYSTEM_PROMPT,
      messages: history
    });

    // Extract assistant response
    const assistantMessage = response.content[0].text;

    // Add assistant response to history
    history.push({
      role: 'assistant',
      content: assistantMessage
    });

    // Store updated history (keep last 20 messages to avoid memory issues)
    if (history.length > 20) {
      history = history.slice(-20);
    }
    conversations.set(convId, history);

    // Send response
    res.json({
      response: assistantMessage,
      conversationId: convId,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens
      }
    });

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({
      error: 'Failed to process chat message',
      details: error.message
    });
  }
});

// Get suggestions endpoint - proactive AI suggestions based on current state
app.post('/api/suggestions', async (req, res) => {
  try {
    const { prepState } = req.body;

    if (!prepState) {
      return res.status(400).json({ error: 'Prep state is required' });
    }

    const completedCount = prepState.completedItems?.length || 0;
    const totalItems = prepState.totalItems || 0;
    const completedItems = prepState.completedItemsList || [];

    const prompt = `Based on the current mise en place progress:
- ${completedCount} of ${totalItems} items completed (${Math.round((completedCount/totalItems)*100)}%)
- Completed items: ${completedItems.join(', ') || 'none yet'}

Provide 2-3 brief, actionable suggestions for what to work on next. Focus on:
1. Items that take longest (should start early)
2. Tasks that can be done in parallel
3. Dependencies (items needed for other items)

Format as a brief bulleted list. Be concise and tactical.`;

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 512,
      system: SYSTEM_PROMPT,
      messages: [{ role: 'user', content: prompt }]
    });

    res.json({
      suggestions: response.content[0].text,
      usage: {
        inputTokens: response.usage.input_tokens,
        outputTokens: response.usage.output_tokens
      }
    });

  } catch (error) {
    console.error('Suggestions error:', error);
    res.status(500).json({
      error: 'Failed to generate suggestions',
      details: error.message
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    anthropicConfigured: !!process.env.ANTHROPIC_API_KEY
  });
});

// Helper function to generate conversation IDs
function generateConversationId() {
  return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Start server
app.listen(PORT, () => {
  console.log(`\n🔪 Kitchen AI Assistant Server`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`Server running on: http://localhost:${PORT}`);
  console.log(`API Key configured: ${process.env.ANTHROPIC_API_KEY ? '✓' : '✗'}`);
  console.log(`\nEndpoints:`);
  console.log(`  POST /api/chat - Chat with AI assistant`);
  console.log(`  POST /api/suggestions - Get smart prep suggestions`);
  console.log(`  GET  /api/health - Health check`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);
});
