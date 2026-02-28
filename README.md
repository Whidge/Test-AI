# Orthophony Memory Test (Python UI)

This project provides a desktop memory game for orthophonist sessions.

## Game rules

- There are **4 shapes** and **4 colors**, creating **16 total combinations**.
- The therapist/user configures:
  - how many symbols are shown in a round (`1` to `16`);
  - how long each symbol stays on screen before the next appears.
- During memorization, symbols are shown one by one.
- During recall, all 16 combinations appear, and the patient must click them in the exact order they were shown.

## Points management

- `+10` points for each correct selection.
- `-5` points for an incorrect selection (round ends).
- `+20` bonus for completing the full sequence in order.
- The app tracks:
  - current round points;
  - session points (across rounds);
  - best round score (persisted locally).

## Run

```bash
python3 app.py
```

## Test

```bash
python3 -m unittest discover -s tests
```
