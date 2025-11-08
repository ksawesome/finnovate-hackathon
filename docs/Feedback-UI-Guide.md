# 🎨 Feedback UI Quick Guide

## What Users See in Risk Dashboard

### Section 1: Feedback Statistics (Top)
```
┌─────────────────────────────────────────────────────────────┐
│  🤖 ML Predictions & Feedback                               │
│  Help improve our AI by providing feedback on predictions  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Total   │  │ Accuracy │  │Correct-  │  │Uncertain │  │
│  │ Feedback │  │   Rate   │  │  ions    │  │          │  │
│  │    19    │  │   0.0%   │  │    5     │  │    0     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Section 2: Prediction Cards (Expandable)
```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Review ML Predictions                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ 📊 10010001 - Cash on Hand (Score: 0.85)                │
│    ┌──────────────────────────────────────────────────┐    │
│    │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │    │
│    │  │ Anomaly  │  │ Priority │  │  Needs   │       │    │
│    │  │  Score   │  │  Score   │  │Attention │       │    │
│    │  │   0.85   │  │  8.5/10  │  │   Yes    │       │    │
│    │  └──────────┘  └──────────┘  └──────────┘       │    │
│    │                                                   │    │
│    │  Balance: ₹125,450,000                           │    │
│    │  ─────────────────────────────────────────────   │    │
│    │  Was this prediction helpful?                    │    │
│    │                                                   │    │
│    │  [ ✅ Correct ]  [ ❌ Incorrect ]  [ ❓ Uncertain ]│    │
│    └──────────────────────────────────────────────────┘    │
│                                                              │
│  ▶ 📊 10020002 - Accounts Receivable (Score: 0.72)        │
│  ▶ 📊 20030001 - Trade Payables (Score: 0.68)             │
│  ▶ 📊 40010001 - Revenue (Score: 0.61)                    │
│  ▶ 📊 50020001 - Operating Expenses (Score: 0.55)         │
└─────────────────────────────────────────────────────────────┘
```

### Section 3: Correction Form (Shown After Clicking ❌ Incorrect)
```
┌─────────────────────────────────────────────────────────────┐
│  ▼ 📊 10010001 - Cash on Hand (Score: 0.85)                │
│    ┌──────────────────────────────────────────────────┐    │
│    │  [Predictions shown above...]                    │    │
│    │  ─────────────────────────────────────────────   │    │
│    │  Provide Correction:                             │    │
│    │                                                   │    │
│    │  Actual Anomaly Score (0-1)  Actual Priority(0-10)│   │
│    │  ┌─────────────────┐         ┌─────────────────┐│    │
│    │  │      0.3        │         │       5.0       ││    │
│    │  └─────────────────┘         └─────────────────┘│    │
│    │                                                   │    │
│    │  Comments (optional)                             │    │
│    │  ┌───────────────────────────────────────────┐  │    │
│    │  │ This balance is expected for month-end    │  │    │
│    │  │ closing. No anomaly here.                 │  │    │
│    │  └───────────────────────────────────────────┘  │    │
│    │                                                   │    │
│    │  [ Submit ]  [ Cancel ]                          │    │
│    └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Section 4: Feedback History (Bottom)
```
┌─────────────────────────────────────────────────────────────┐
│  📈 Recent Feedback History                                 │
├─────────────────────────────────────────────────────────────┤
│  Account    │ Type     │ Feedback  │ Predicted │ Actual    │
│  Code       │          │ Type      │ Value     │ Value     │
├─────────────┼──────────┼───────────┼───────────┼───────────┤
│ 10010001    │ anomaly  │ incorrect │   0.85    │   0.30    │
│ 10010001    │ priority │ incorrect │   8.50    │   5.00    │
│ 10020002    │ anomaly  │ correct   │   0.72    │     -     │
│ 20030001    │ priority │ uncertain │   6.80    │     -     │
│ 40010001    │ anomaly  │ incorrect │   0.61    │   0.45    │
└─────────────────────────────────────────────────────────────┘
```

---

## User Workflow

### Happy Path (Correct Prediction)
1. User opens Risk Dashboard
2. Scrolls to "🤖 ML Predictions & Feedback"
3. Clicks expander for an account
4. Reviews prediction (anomaly: 0.85, priority: 8.5/10)
5. Clicks **✅ Correct** button
6. Sees success message: "✅ Thank you! Feedback recorded."
7. Feedback stored in MongoDB
8. Statistics update automatically

**Time**: ~10 seconds

### Correction Path (Incorrect Prediction)
1. User opens Risk Dashboard
2. Scrolls to "🤖 ML Predictions & Feedback"
3. Clicks expander for an account
4. Reviews prediction (anomaly: 0.85, priority: 8.5/10)
5. Disagrees - clicks **❌ Incorrect** button
6. Form appears with number inputs
7. Enters actual anomaly score: 0.3
8. Enters actual priority score: 5.0
9. Adds comment: "Expected for month-end"
10. Clicks **Submit**
11. Sees success message: "✅ Corrections submitted!"
12. Feedback stored with actual values
13. Available for next retraining cycle

**Time**: ~30 seconds

### Uncertain Path
1-4. (Same as above)
5. Unsure - clicks **❓ Uncertain** button
6. Sees info message: "📝 Feedback recorded as uncertain."
7. Feedback stored without actual values
8. System knows to get more opinions

**Time**: ~10 seconds

---

## Technical Details

### State Management
```python
# Streamlit session state tracks correction forms
st.session_state[f'fb_{idx}_{account_code}_show_correction'] = True

# Unique keys prevent conflicts
key=f"fb_{idx}_{account_code}_correct"
```

### Feedback Collection
```python
from src.feedback_handler import MLFeedbackCollector

collector = MLFeedbackCollector()

# Quick feedback (correct/uncertain)
collector.collect_prediction_feedback(
    account_code='10010001',
    prediction_type='anomaly',
    predicted_value=0.85,
    feedback_type='correct',
    user_id='user@example.com',
    period='Mar-24',
    entity='AEML'
)

# Correction with actual value
collector.collect_prediction_feedback(
    account_code='10010001',
    prediction_type='anomaly',
    predicted_value=0.85,
    actual_value=0.30,  # User's correction
    feedback_type='incorrect',
    user_id='user@example.com',
    comments='Expected for month-end',
    period='Mar-24',
    entity='AEML'
)
```

### Statistics Display
```python
stats = collector.get_feedback_stats()
# Returns:
# {
#   'total_feedback': 19,
#   'correct': 0,
#   'incorrect': 5,
#   'uncertain': 0,
#   'accuracy_rate': 0.0,
#   'correction_rate': 26.3
# }
```

---

## Design Principles

### ✅ Quick Feedback First
- Default action = one click
- **✅ Correct** button requires no form
- Most predictions are correct, so optimize for that

### ✅ Progressive Disclosure
- Correction form only shown when needed
- Expandable cards hide complexity
- Advanced options (comments) are optional

### ✅ Clear Visual Hierarchy
- Statistics at top (overview)
- Predictions in middle (action area)
- History at bottom (reference)

### ✅ Immediate Feedback
- Success messages after submission
- Statistics update in real-time
- Rerun refreshes the page

### ✅ Mobile-Friendly
- Streamlit columns adapt to screen size
- Buttons stack vertically on mobile
- Forms are touch-friendly

---

## Accessibility

- **Color Coding**:
  - ✅ Green = Correct/Success
  - ❌ Red = Incorrect/Error
  - ❓ Blue = Uncertain/Info

- **Icons**:
  - All buttons have emoji + text
  - Not relying on color alone

- **Clear Labels**:
  - "Actual Anomaly Score (0-1)"
  - "Actual Priority (0-10)"
  - Range indicators prevent invalid input

---

## Future Enhancements

### 1. Bulk Feedback
- Select multiple accounts
- Apply same feedback to all
- "Mark all as reviewed"

### 2. Keyboard Shortcuts
- `C` = Correct
- `I` = Incorrect
- `U` = Uncertain
- `Enter` = Submit form

### 3. Confidence Slider
- Instead of binary correct/incorrect
- Slider from "Completely Wrong" to "Completely Right"
- Captures nuanced feedback

### 4. Expert Mode
- Show feature importance
- Display model confidence
- Explain prediction reasoning

### 5. Gamification
- Leaderboard of most helpful reviewers
- Badges for feedback milestones
- Accuracy tracking per user

---

## Troubleshooting

### Issue: Buttons not working
**Cause**: Unique key collision
**Fix**: Each button has `key=f"fb_{idx}_{account_code}_action"`

### Issue: Form doesn't appear after clicking ❌
**Cause**: Session state not updating
**Fix**: Added `st.rerun()` after button click

### Issue: Feedback not saving
**Cause**: MongoDB connection error
**Fix**: Check `MONGODB_URI` environment variable

### Issue: Statistics not updating
**Cause**: Cache not cleared
**Fix**: Set `ttl=300` on `@st.cache_data`

---

## Testing Checklist

- [ ] Click **✅ Correct** → See success message
- [ ] Click **❌ Incorrect** → Form appears
- [ ] Fill form → Click Submit → See success message
- [ ] Click Cancel → Form disappears
- [ ] Check feedback history → New entry at top
- [ ] Check statistics → Numbers updated
- [ ] Open different account → Independent forms
- [ ] Refresh page → Feedback persists (MongoDB)

---

**Built by**: Project Aura Team
**Date**: November 8, 2024
**Status**: ✅ Fully Integrated and Tested
