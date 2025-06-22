## 🧠 Prompt Title: Remove GPU Code from main.py
📅 Date: 2025-06-22 18:35

### 🔍 Improved Business Logic:
- Removed all code related to GPU detection and usage in `main.py`.
- Ensured the `WhisperModel` is always initialized with `device="cpu"` and `compute_type="int8"`.

---

## Review
- Removed GPU-related code from `main.py` by simplifying the `WhisperSingleton` class to always use `device="cpu"` and `compute_type="int8"`.
- This change ensures that the application will run solely on the CPU, eliminating any dependencies on GPU hardware or libraries like `torch`.