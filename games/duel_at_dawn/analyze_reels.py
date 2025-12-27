"""Analyze reel strips for FS scatter symbols."""

import os

reels_path = os.path.join(os.path.dirname(__file__), "reels")
files = ["BR0.csv", "FR0.csv", "FR1.csv", "WCAP.csv"]

print("\n=== Analyzing Reel Strips ===\n")

for filename in files:
    filepath = os.path.join(reels_path, filename)
    if not os.path.exists(filepath):
        print(f"{filename}: NOT FOUND")
        continue
    
    with open(filepath, 'r', encoding='UTF-8') as f:
        lines = f.readlines()
    
    total_symbols = 0
    fs_count = 0
    vs_count = 0
    o_count = 0
    reel_counts = [0] * 5
    reel_fs_counts = [0] * 5
    reel_vs_counts = [0] * 5
    reel_o_counts = [0] * 5
    
    for line in lines:
        symbols = [s.strip() for s in line.strip().split(',')]
        for reel_idx, symbol in enumerate(symbols):
            if reel_idx >= 5:
                continue
            total_symbols += 1
            reel_counts[reel_idx] += 1
            
            if symbol == "FS":
                fs_count += 1
                reel_fs_counts[reel_idx] += 1
            elif symbol == "VS":
                vs_count += 1
                reel_vs_counts[reel_idx] += 1
            elif symbol == "O":
                o_count += 1
                reel_o_counts[reel_idx] += 1
    
    print(f"\n{filename}:")
    print(f"  Total symbols: {total_symbols}")
    print(f"  FS symbols: {fs_count} ({fs_count/total_symbols*100:.2f}%)")
    print(f"  VS symbols: {vs_count} ({vs_count/total_symbols*100:.2f}%)")
    print(f"  O symbols: {o_count} ({o_count/total_symbols*100:.2f}%)")
    print(f"  Reel lengths: {reel_counts}")
    print(f"  FS per reel:")
    for i in range(5):
        fs_pct = (reel_fs_counts[i] / reel_counts[i] * 100) if reel_counts[i] > 0 else 0
        print(f"    Reel {i}: {reel_fs_counts[i]} FS ({fs_pct:.2f}%)")
    print(f"  VS per reel:")
    for i in range(5):
        vs_pct = (reel_vs_counts[i] / reel_counts[i] * 100) if reel_counts[i] > 0 else 0
        print(f"    Reel {i}: {reel_vs_counts[i]} VS ({vs_pct:.2f}%)")
    
    # Check if 3+ FS scatters are possible
    min_fs_per_reel = [reel_fs_counts[i] for i in range(5)]
    print(f"  Can trigger 3 FS? {'YES' if sum(min_fs_per_reel) >= 3 else 'NO'}")
    print(f"  Can trigger 4 FS? {'YES' if sum(min_fs_per_reel) >= 4 else 'NO'}")

print("\n=== Analysis Complete ===\n")

