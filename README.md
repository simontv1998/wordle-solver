# wordle-solver

A CLI that solves Wordle puzzles using an **optimistic entropy strategy**: every guess is drawn from the remaining candidate pool (so each turn is a live chance to win), ranked by Shannon entropy to split candidates as evenly as possible.

**Benchmark on the built-in 990-word list:** 100% solve rate, 3.19 average guesses.

## Usage

```
python wordle_solver.py             # interactive — solver guides your live game
python wordle_solver.py solve CRANE # watch the solver crack a known answer
python wordle_solver.py bench       # benchmark against all words
```

## Interactive mode

Run without arguments to get turn-by-turn suggestions while you play on the NYT site (or anywhere else). Enter your guess, type the feedback, repeat.

```
Turn 1/6  |  990 candidate(s) left
  Suggestion: TRACE
  Your guess (Enter = use suggestion):
  Feedback for TRACE (e.g. GBYYB): BGYBB

   T | R | A | C | E        ← gray / green / yellow / gray / gray

Turn 2/6  |  47 candidate(s) left
  Suggestion: GROAN
  ...
```

Feedback key: `G` = green (right letter, right spot) · `Y` = yellow (right letter, wrong spot) · `B` = gray (absent)

## Strategy

*Optimistic* means the solver never wastes a guess on a word that cannot be the answer. Every suggestion is a word that could still win on that turn.

Within that constraint, candidates are ranked by **Shannon entropy** — the guess whose feedback partitions the remaining pool most evenly comes first, minimising expected guesses to solution.

A precomputed feedback table and LRU-cached `best_guess` keep each suggestion instant even on the first turn.

## Requirements

Python 3.10+, no third-party dependencies.
