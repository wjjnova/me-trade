# Strategy Builder Redesign Summary

## Overview
The Strategy Builder page has been completely redesigned to provide a unified workflow for defining trading strategies with three interchangeable formats: Human Readable, JSON, and Backtrader Code.

## Key Changes

### 1. Database Schema Updates (`src/db/schema.py`)
Added three new columns to the `strategies` table:
- `human_readable` TEXT - Clear, structured description in plain English
- `json_definition` TEXT - Structured JSON strategy definition
- `backtrader_code` TEXT - Complete Backtrader Python strategy class

The legacy `json` column is maintained for backward compatibility.

### 2. LLM Integration (`src/strategy/nl_parser.py`)
- **New Method**: `parse_with_llm(text) -> Tuple[str, Dict, str]`
  - Uses OpenAI GPT-4 to convert natural language to all three formats
  - Falls back to rule-based parsing if LLM is unavailable
  - Requires `OPENAI_API_KEY` environment variable

- **New Method**: `_generate_human_readable(strategy_dict) -> str`
  - Generates human-readable descriptions from JSON strategy definitions
  - Used as fallback when LLM is not available

### 3. Strategy Builder Page Redesign (`pages/2_Strategy_Builder.py`)

#### Tab Structure (Before → After)
- ❌ Removed: "Natural Language" tab
- ❌ Removed: "Structured JSON" tab
- ✅ Added: "Define Strategy" tab (merged functionality)
- ✅ Kept: "Saved Strategies" tab (enhanced)

#### "Define Strategy" Tab Features
1. **Natural Language Input**
   - Text area for strategy description
   - Symbol override option
   - "Parse Strategy" button calls LLM to generate all 3 formats

2. **Three Format Editors** (in sub-tabs)
   - 📖 **Human Readable**: Editable plain text description
   - ⚙️ **JSON Definition**: Editable structured JSON with validation
   - 💻 **Backtrader Code**: Editable Python code with validation

3. **Cross-Format Operations**
   - Validate JSON → ensures schema compliance
   - Compile JSON → generates Backtrader code
   - Validate Code → checks for common issues
   - Update buttons to save edits to session state

4. **Save Functionality**
   - Saves all three formats to database simultaneously
   - Maintains backward compatibility with legacy `json` column

#### "Saved Strategies" Tab Features
1. **Three Format Display**
   - Each saved strategy shows 3 sub-tabs (Human/JSON/Code)
   - All formats are editable in place
   - Auto-generates missing formats from JSON if needed

2. **Per-Format Actions**
   - Validate button for each format
   - Update button to save changes to database
   - Separate updates for each format

3. **Strategy-Level Actions**
   - "Load to Editor" - loads all 3 formats to Define Strategy tab
   - "Delete" - removes strategy and associated data

### 4. Translation Updates (`src/ui/i18n.py`)
Updated both English and Chinese translations:

#### New Translation Keys
- `builder.tabs.define` - "Define Strategy" / "定义策略"
- `builder.define.*` - All Define Strategy tab strings
- `builder.saved.format_*` - Format-specific labels
- Removed legacy `builder.nl.*` and `builder.json.*` keys

### 5. Dependencies (`requirements.txt`)
Added OpenAI SDK:
```
openai>=1.3.0
```

## Usage Guide

### Setting Up LLM Integration
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. Without API key, the system falls back to rule-based parsing

### Workflow

#### Creating a New Strategy
1. Go to "Define Strategy" tab
2. Describe your strategy in plain English/Chinese
3. Click "Parse Strategy" (uses LLM if configured)
4. Review and edit all three formats as needed
5. Save with a meaningful name

#### Editing Saved Strategies
1. Go to "Saved Strategies" tab
2. Expand the strategy you want to edit
3. Switch to desired format tab (Human/JSON/Code)
4. Make edits directly in the text area
5. Click "Update" to save changes

#### Loading to Editor
1. In "Saved Strategies" tab, find your strategy
2. Click "Load to Editor"
3. All three formats populate the Define Strategy tab
4. Make changes and save as new version or update

## Technical Details

### LLM Prompt Design
The system uses a carefully crafted prompt that:
- Defines the three output formats clearly
- Provides JSON schema for structured validation
- Instructs to use pre-calculated indicators (e.g., `self.data.sma_20`)
- Returns JSON response with all three formats

### Backward Compatibility
- Legacy strategies with only `json` column still work
- Auto-generates Human Readable and Code formats on demand
- Saves to new columns on next update

### Session State Management
Three session state variables maintain current strategy:
- `human_readable` - Current human-readable text
- `json_definition` - Current strategy dictionary
- `backtrader_code` - Current Python code

## Benefits

1. **Unified Workflow**: Single tab for all strategy definition tasks
2. **Flexibility**: Edit in any format (NL → JSON → Code or vice versa)
3. **Transparency**: See all three representations simultaneously
4. **LLM-Powered**: Intelligent parsing with GPT-4 (when configured)
5. **Fallback Support**: Works without LLM using rule-based parsing
6. **Better UX**: Clearer navigation, less context switching
7. **Enhanced Editing**: Edit saved strategies in place across all formats

## Migration Notes

### For Users
- Old saved strategies remain accessible
- New format fields auto-generate on first edit
- No manual migration required

### For Developers
- New database columns added via ALTER TABLE (if not exists)
- NLParser now requires optional `use_llm` parameter
- Three-format tuple return from `parse_with_llm()`
- Session state structure changed (removed `current_strategy`, added three format variables)

## Future Enhancements

Potential improvements:
1. **Bi-directional Sync**: Edit code → update JSON automatically
2. **Format Comparison**: Side-by-side diff view
3. **Version History**: Track changes to each format over time
4. **Template Library**: Pre-built strategy templates in all formats
5. **Alternative LLMs**: Support for Claude, Llama, etc.
6. **Streaming Responses**: Real-time LLM output display
7. **Format Validation**: Real-time syntax checking for all formats

## Testing Recommendations

1. **Test LLM Integration**
   - With valid OPENAI_API_KEY
   - Without API key (fallback behavior)
   - With invalid API key (error handling)

2. **Test Format Conversions**
   - NL → JSON → Code pipeline
   - JSON validation edge cases
   - Code compilation errors

3. **Test Saved Strategy Operations**
   - Load from database
   - Edit and update each format
   - Delete strategy
   - Auto-generation of missing formats

4. **Test Backward Compatibility**
   - Load old strategies (json column only)
   - Update old strategies (should populate new columns)
   - Mix of old and new strategies in list

## Troubleshooting

### LLM Not Working
- Check `OPENAI_API_KEY` is set: `echo $OPENAI_API_KEY`
- Verify API key is valid on OpenAI dashboard
- Check network connectivity
- Review logs for specific errors

### Format Sync Issues
- Formats don't auto-sync (by design)
- Use "Compile to Code" to regenerate code from JSON
- Use "Validate" buttons to check format integrity

### Database Errors
- Run `python -c "from src.db import get_db; get_db().initialize_schema()"` to update schema
- Check database file permissions
- Verify SQLite version compatibility

---

**Implementation Date**: October 25, 2025
**Version**: 2.0.0
**Status**: ✅ Complete
