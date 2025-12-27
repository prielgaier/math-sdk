"""Add FS symbols to BR0.csv to enable forcing 3-4 FS scatters."""

import os
import csv
import random

def add_fs_to_br0(file_path, num_per_reel=1):
    """Add FS symbols to reels 1, 2, and 4 in BR0.csv."""
    # Read the reel strip
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Count current FS symbols
    current_fs_count = sum(1 for row in rows for symbol in row if symbol == 'FS')
    print(f"Current FS symbols: {current_fs_count}")
    
    # Find positions where we can add FS symbols
    # We need to add to reels 1, 2, and 4 (columns 1, 2, 4 in 0-indexed)
    target_reels = [1, 2, 4]
    
    # Count current FS per reel
    fs_per_reel = {reel: 0 for reel in target_reels}
    for row in rows:
        for reel_idx in target_reels:
            if reel_idx < len(row) and row[reel_idx] == 'FS':
                fs_per_reel[reel_idx] += 1
    
    print(f"Current FS per reel: {fs_per_reel}")
    
    # Find rows that don't already have FS in the target reels
    available_positions = []
    for row_idx, row in enumerate(rows):
        for reel_idx in target_reels:
            if reel_idx < len(row) and row[reel_idx] != 'FS':
                # Check if this position would create a valid board
                # Avoid placing FS next to other special symbols if possible
                available_positions.append((row_idx, reel_idx))
    
    # Ensure at least one FS per target reel
    positions_to_add = []
    for reel_idx in target_reels:
        if fs_per_reel[reel_idx] == 0:
            # Find available positions for this reel
            reel_positions = [(r, c) for r, c in available_positions if c == reel_idx]
            if reel_positions:
                pos = random.choice(reel_positions)
                positions_to_add.append(pos)
                available_positions.remove(pos)
    
    # Add additional FS symbols if needed
    remaining_needed = (len(target_reels) * num_per_reel) - len(positions_to_add)
    if remaining_needed > 0 and available_positions:
        additional = random.sample(available_positions, min(remaining_needed, len(available_positions)))
        positions_to_add.extend(additional)
    
    # Add FS symbols
    num_added = 0
    for row_idx, reel_idx in positions_to_add:
        if rows[row_idx][reel_idx] != 'FS':
            rows[row_idx][reel_idx] = 'FS'
            num_added += 1
    
    # Write back
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"\nAdded {num_added} FS symbols")
    print(f"Total FS symbols now: {current_fs_count + num_added}")
    print(f"\nUpdated {file_path}")
    print("Run analyze_reels.py to verify the changes.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "reels", "BR0.csv")
    
    # Set random seed for reproducibility
    random.seed(42)
    
    add_fs_to_br0(file_path, num_per_reel=1)

