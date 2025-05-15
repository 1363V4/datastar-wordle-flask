import { waapi, stagger } from 'https://cdn.jsdelivr.net/npm/animejs/+esm';

waapi.animate('.difficulty-button p', {
  scale: `.99`,
  duration: 500,
  loop: true,
  alternate: true,
  ease: 'linear',
});

const spin = waapi.animate('header span', {
  rotateX: 360,
  delay: stagger(200),
  duration: 2000,
  autoplay: false,
});

const spinGo = () => spin.play();

document.querySelector('header').addEventListener('click', spinGo)

// ---

class WordleLine extends HTMLElement {
  constructor() {
    super();
    this._value = '';
    this._length = 5; // Default length
    this._handleKeyDown = this._handleKeyDown.bind(this);
  }

  static get observedAttributes() {
    return ['length', 'value'];
  }

  connectedCallback() {
    this._render();
    window.addEventListener('keydown', this._handleKeyDown);
  }

  disconnectedCallback() {
    window.removeEventListener('keydown', this._handleKeyDown);
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (name === 'length') {
      this._length = parseInt(newValue, 10) || 5;
      this._render();
    } else if (name === 'value') {
      this._value = newValue || '';
      this._updateSquares();
    }
  }

  get value() {
    return this._value;
  }

  set value(val) {
    this._value = val;
    this.setAttribute('value', val);
    this._updateSquares();
  }

  get length() {
    return this._length;
  }

  set length(val) {
    this._length = parseInt(val, 10) || 5;
    this.setAttribute('length', this._length);
    this._render();
  }

  _handleKeyDown(event) {
    const key = event.key;
    
    if (/^[a-zA-Z]$/.test(key)) {
      // If key is a letter
      if (this._value.length < this._length) {
        this.value = this._value + key.toUpperCase();
      }
    } else if (key === 'Escape' || key === 'Backspace') {
      // Remove the last letter
      if (this._value.length > 0) {
        this.value = this._value.slice(0, -1);
      }
    } else if (key === 'Enter') {
      // If the value is full, dispatch a 'wordle' event
      if (this._value.length === this._length) {
        this.dispatchEvent(new CustomEvent('wordle', {
          bubbles: true,
          detail: { value: this._value }
        }));
      }
    }
  }

  _render() {
    this.innerHTML = '';
    this.style.gridTemplateColumns = `repeat(${this._length}, 1fr)`;
    for (let i = 0; i < this._length; i++) {
      const square = document.createElement('div');
      square.className = 'square';
      this.appendChild(square);
    }
    this._updateSquares();
  }

  _updateSquares() {
    const squares = this.querySelectorAll('.square');
    squares.forEach((square, index) => {
      square.textContent = index < this._value.length ? this._value[index] : '';
    });
  }
}

// Define the custom element
customElements.define('wordle-line', WordleLine);