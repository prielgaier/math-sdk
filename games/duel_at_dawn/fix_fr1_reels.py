"""Add FS symbols to FR1.csv to enable retriggers."""

import os
import random

reels_path = os.path.join(os.path.dirname(__file__), "reels")
fr1_path = os.path.join(reels_path, "FR1.csv")

# Read current FR1.csv
with open(fr1_path, 'r', encoding='UTF-8') as f:
    lines = [line.strip() for line in f.readlines()]

# Convert to 2D array (reel-based)
reels = [[] for _ in range(5)]
for line in lines:
    symbols = [s.strip() for s in line.split(',')]
    for reel_idx in range(5):
        if reel_idx < len(symbols):
            reels[reel_idx].append(symbols[reel_idx])

# Count current FS symbols
fs_positions = []
for reel_idx in range(5):
    for pos_idx, symbol in enumerate(reels[reel_idx]):
        if symbol == "FS":
            fs_positions.append((reel_idx, pos_idx))

print(f"Current FS symbols: {len(fs_positions)}")
print(f"FS positions: {fs_positions}")

# We need at least 4 FS symbols total to enable 3+ FS triggers
# Target: Add 2-4 more FS symbols, distributed across different reels
target_fs_count = 6  # Total FS symbols (currently 2, need 4 more)

# Find positions where we can add FS symbols
# Avoid positions too close to existing FS symbols
# Prefer reels 1, 2, 4 (which currently have 0 FS)
available_positions = []
for reel_idx in range(5):
    for pos_idx in range(len(reels[reel_idx])):
        # Check if position is far enough from existing FS
        too_close = False
        for fs_reel, fs_pos in fs_positions:
            if reel_idx == fs_reel:
                # Same reel - check distance
                distance = min(
                    abs(pos_idx - fs_pos),
                    abs(pos_idx - fs_pos + len(reels[reel_idx])),
                    abs(pos_idx - fs_pos - len(reels[reel_idx]))
                )
                if distance < 20:  # Keep at least 20 positions apart
                    too_close = True
                    break
        
        if not too_close:
            # Prefer reels 1, 2, 4 (which have 0 FS currently)
            priority = 1 if reel_idx in [1, 2, 4] else 2
            available_positions.append((priority, reel_idx, pos_idx))

# Sort by priority (reels with 0 FS first), then randomize
available_positions.sort(key=lambda x: (x[0], random.random()))

# Add FS symbols
fs_to_add = target_fs_count - len(fs_positions)
added = 0
for priority, reel_idx, pos_idx in available_positions:
    if added >= fs_to_add:
        break
    
    # Make sure we're not replacing a special symbol
    current_symbol = reels[reel_idx][pos_idx]
    if current_symbol not in ["VS", "O", "W", "S"]:  # Don't replace special symbols
        reels[reel_idx][pos_idx] = "FS"
        fs_positions.append((reel_idx, pos_idx))
        added += 1
        print(f"Added FS at Reel {reel_idx}, Position {pos_idx} (was: {current_symbol})")

print(f"\nAdded {added} FS symbols")
print(f"Total FS symbols now: {len(fs_positions)}")

# Write back to file
max_length = max(len(reel) for reel in reels)
with open(fr1_path, 'w', encoding='UTF-8') as f:
    for row_idx in range(max_length):
        row_symbols = []
        for reel_idx in range(5):
            if row_idx < len(reels[reel_idx]):
                row_symbols.append(reels[reel_idx][row_idx])
            else:
                row_symbols.append("")  # Shouldn't happen if reels are same length
        f.write(",".join(row_symbols) + "\n")

print(f"\nUpdated {fr1_path}")
print("Run analyze_reels.py to verify the changes.")

