# Datastar Wordle with Synchronous Flask

A **Wordle** game clone built with **Datastar** and **Flask**, demonstrating how to create delightful, reactive web applications using **synchronous request-response architecture** with Server-Sent Events. This project showcases Datastar's power to deliver SPA-like experiences without complex async patterns or persistent connections.

## Overview

This Wordle implementation proves that you don't need complex async frameworks to build modern, interactive web applications. By leveraging **Datastar's SSE with n=1 pattern** (single event per request), we achieve smooth, reactive gameplay while maintaining Flask's familiar synchronous request-response model.

The game features multiple difficulty levels, real-time letter validation, smooth animations, and seamless state transitions - all powered by Datastar's reactive primitives and Flask's simplicity.

## Project Structure

```
datastar-wordle-flask/
├── app.py                # Main Flask application
├── templates/
│   └── index.html        # Landing page and difficulty selection
├── static/
│   ├── css/
│   │   ├── index.css     # Game-specific styling with CSS animations
│   │   └── gold.css      # Shared design system
│   ├── js/
│   │   ├── index.js      # Custom wordle-line web component
│   │   ├── datastar.js   # Datastar framework
│   │   └── gold.js       # Utility functions
│   ├── svg/              # Loading animations and icons
│   └── img/              # Game assets
├── utils/
│   └── logger.py         # Logging utilities
├── datastar_py/          # Local Datastar Python integration
├── words.py              # Word lists by difficulty
└── data.json             # TinyDB game state storage
```

## Technology Stack

- **Backend**: Flask (synchronous) with TinyDB for state persistence
- **Frontend**: Datastar for reactive UI with custom web components
- **Communication**: Server-Sent Events with single event per request (request-response model)
- **State Management**: Session-based game state with database persistence
- **Rate Limiting**: Flask-Limiter for production deployment protection

## Datastar Integration & Features

### 1. Synchronous SSE Pattern

Use SSE with exactly one event per request to maintain synchronous architecture:

```html
<main
  id="main"
  class="gz"
  data-on-wordle="@post('/attempt/' + evt.detail.value)"
  data-indicator-fetching
></main>
```

```python
from datastar_py.sse import ServerSentEventGenerator as SSE

# sent with
@app.post('/attempt/<details>')
def attempt(details):
    # Process game logic synchronously
    data = games.get(doc_id=session['db_id'])

    # Validate and update game state
    if valid_attempt:
        # Update database
        games.update({'attempts': attempts}, doc_ids=[db_id])

        # Generate updated HTML
        html = view_function(data)

        # Return single SSE fragment
        return SSE.merge_fragments(fragments=[html])
```

**Why This Matters**:

- **No persistent connections**: Each request completes immediately
- **No async complexity**: Standard Flask patterns work perfectly
- **Scalable**: Works with traditional hosting (no WebSocket requirements)
- **Datastar magic**: Still get reactive UI updates and smooth transitions

### 2. Custom Web Components Integration

**wordle-line Web Component**

This component listens to keydown events. If we have the maximum number of letters, we send a custom datastar event to make a post request.

```javascript
class WordleLine extends HTMLElement {
  _handleKeyDown(event) {
    const key = event.key;

    if (/^[a-zA-Z]$/.test(key) && this._value.length < this._length) {
      this.value = this._value + key.toUpperCase();
    } else if (key === "Enter" && this._value.length === this._length) {
      // Dispatch custom event for Datastar to catch
      this.dispatchEvent(
        new CustomEvent("wordle", {
          bubbles: true,
          detail: { value: this._value },
        })
      );
    }
  }
}
```

**Datastar Event Binding**:

```html
<main
  id="main"
  data-on-wordle="@post('/attempt/' + evt.detail.value)"
  data-indicator-fetching
>
  <wordle-line length="5"></wordle-line>
</main>
```

**Key Features**:

- **Props Down, Events Up**: Web component encapsulates input logic
- **Custom Event Integration**: Seamless communication with Datastar
- **Dynamic Length**: Component adapts to different word lengths
- **Keyboard Handling**: Full keyboard interaction (letters, backspace, enter)

### 3. Difficulty Selection with Smooth Transitions

**One-Click Game Start**

```html
<div class="gc difficulty-button" data-on-click="@post('/difficulty/easy')">
  <span>Easy</span>
  <p>5 letters - 7 tries</p>
</div>
```

**Server-Side Game Initialization**:

```python
@app.post('/difficulty/<difficulty>')
def difficulty(difficulty):
    match difficulty:
        case "easy":
            word = choice(words[5])
            no_tries, no_letters = 7, 5
        case "hackerman":
            word = choice(words[9])
            no_tries, no_letters = 1, 9
        # cultist???

    # Store game state with timestamp-based ID
    db_id = int(time.time() * 1000)  # Avoids TinyDB conflicts
    games.insert(table.Document(data, doc_id=db_id))
    session['db_id'] = db_id

    # Return game HTML with view transition
    html = view_function(data)
    return SSE.merge_fragments(fragments=[html], use_view_transition=True)
```

**Datastar Magic**:

- **`use_view_transition=True` with SSE**: Smooth page transitions without page reload
- **Session Management**: Automatic game state linking
- **Immediate Gameplay**: No loading screens or setup delays

### 4. Advanced CSS Animation Integration

**Data-Driven Animation Delays**

```python
def view_function(data):
    delay = 0
    for letter, color in zip(attempt['letters'], attempt['colors']):
        html += f'''
        <div class="square"
             completed
             data-delay="{delay}s"
             style="background: {bg_color}">
             {letter}
        </div>'''
        delay += 2 / no_tries  # Progressive delay based on difficulty
```

**CSS attr() Integration**:

```css
.square {
  transition: all 0.2s linear;
  transition-delay: attr(data-delay type(<time>), 0s);
}
```

**Result**: Each letter square animates in sequence, creating a satisfying reveal effect that scales with game difficulty.

### 5. Real-Time Loading States

**Built-in Fetching Indicators**

```html
<main
  id="main"
  data-on-wordle="@post('/attempt/' + evt.detail.value)"
  data-indicator-fetching
>
  <img src="/static/svg/gooey-balls.svg" data-show="$fetching" />
</main>
```

- **`data-indicator-fetching`**: Datastar automatically manages `$fetching` signal
- **`data-show="$fetching"`**: Loading animation appears during requests
- **Zero JavaScript**: Pure declarative loading states

### 6. Game Over Overlays with CSS Timing

**Delayed Success/Failure Notifications**

```python
overlay = f'''
<div class="gc overlay">
    <p class="gt l">A WINNER IS YOU</p>
    <p>In only {len(attempts)} attempts, wow :o</p>
    <a href="/new_game"><div class="gc difficulty-button">Play again?</div></a>
</div>
'''
```

**CSS-Controlled Timing**:

```css
.overlay {
  opacity: 0;
  animation: pop 1s linear 1s forwards; /* 1s delay, 1s duration */
}

@keyframes pop {
  to {
    opacity: 1;
  }
}
```

**Why This Works**: In synchronous mode, we can't delay server responses. Instead, we send the overlay immediately but use CSS to time its appearance, allowing the final guess animation to complete first.

### 7. Color-Coding System

**Wordle Logic with Visual Feedback**

```python
def get_colors(word, attempt):
    result = ['B'] * len(attempt)    # Black (not in word)
    remaining = {}

    # Count available letters
    for char in word:
        remaining[char] = remaining.get(char, 0) + 1

    # First pass: exact matches (Green)
    for i, (w_char, a_char) in enumerate(zip(word, attempt)):
        if w_char == a_char:
            result[i] = 'G'
            remaining[w_char] -= 1

    # Second pass: wrong position (Yellow)
    for i, a_char in enumerate(attempt):
        if result[i] != 'G' and a_char in remaining and remaining[a_char] > 0:
            result[i] = 'Y'
            remaining[a_char] -= 1

    return ''.join(result)
```

**Dynamic Background Colors**:

```python
bg_color = {'G': "green", 'Y': "chocolate", 'B': "black"}.get(color)
html += f'<div class="square" style="background: {bg_color}">{letter}</div>'
```

### 8. Multi-Threaded Database Safety

**TinyDB ID Hack**

```python
# Problem: TinyDB uses auto-incrementing IDs that conflict with multiple workers
# Solution: Use timestamp as document ID
db_id = int(time.time() * 1000)
games.insert(table.Document(data, doc_id=db_id))
```

This simple trick enables TinyDB usage in multi-threaded production environments without document ID conflicts.

## Key Datastar Patterns Demonstrated

### SSE with Request-Response Model

```python
# Single event per request - no persistent connections
return SSE.merge_fragments(fragments=[html])
```

### Custom Event -> POST Request

```html
data-on-wordle="@post('/attempt/' + evt.detail.value)"
```

### Fragment-Based Updates

```python
# Replace specific DOM sections without full page reload
return SSE.merge_fragments(fragments=[html], use_view_transition=True)
```

### CSS Animation Coordination

```css
.square {
  transition-delay: attr(data-delay type(<time>), 0s);
}
```

```html
<div
  class="square"
  completed
  data-delay="{delay}s"
  style="background: {bg_color}"
>
  {letter}
</div>
```

### Declarative Loading States

```html
data-indicator-fetching data-show="$fetching"
```

## Running the Application

### Prerequisites

- Python 3.9+
- uv package manager

### Setup

1. **Install dependencies**:

```bash
uv sync
```

2. **Run the application**:

```bash
uv run app.py
```

4. **Play**: Open `http://localhost:5000` in your browser

### Game Rules

- **Easy**: 5 letters, 7 attempts
- **Medium**: 5 letters, 6 attempts
- **Hard**: 6 letters, 5 attempts
- **Hackerman**: 9 letters, 1 attempt (good luck!)

## Notable Implementation Details

### Animation Performance

- **CSS-driven animations**: Leverage browser optimization instead of JavaScript
- **Staggered reveals**: Progressive letter animations create engaging feedback
- **Smooth transitions**: View transitions between game states

### Production Considerations

- **Rate limiting**: Built-in protection with Flask-Limiter
- **Database ID hack**: Multi-threaded TinyDB usage patterns

### Error Handling

- **Input validation**: Regex patterns ensure only valid letters
- **State protection**: Session-based game isolation

## Why This Architecture Matters

This project demonstrates that **modern web UX doesn't require complex async patterns**. By combining:

- **Flask's simplicity**: Familiar request-response patterns
- **Datastar's reactivity**: SPA-like user experience
- **SSE with n=1**: Real-time feel without persistent connections
- **Custom web components**: Reusable, encapsulated UI logic

We achieve:

- ✅ **Delightful animations** and smooth transitions
- ✅ **Real-time feedback** without complex state management
- ✅ **Scalable architecture** that works on traditional hosting
- ✅ **Developer-friendly** patterns that feel familiar
