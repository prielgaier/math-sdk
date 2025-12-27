"""Main file for generating results for Duel At Dawn game."""

import threading
import time
from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs


class TimeoutError(Exception):
    """Custom exception for timeout errors."""
    pass


def run_with_timeout(func, timeout_seconds, *args, **kwargs):
    """Run a function with a timeout. Raises TimeoutError if function doesn't complete in time."""
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        raise TimeoutError(
            f"Operation timed out after {timeout_seconds} seconds. "
            f"This likely indicates a hang or infinite loop in the simulation."
        )
    
    if exception[0]:
        raise exception[0]
    
    return result[0]

if __name__ == "__main__":

    num_threads = 8  # Increased for faster simulation
    rust_threads = 20
    batching_size = 50000  # Compatible with 3000 sims and 8 threads
    compression = False  # Disable compression for faster testing
    profiling = False

    num_sim_args = {
        "base": int(3e3),  # 3000 sims for comprehensive book coverage
    }

    run_conditions = {
        "run_sims": True,
        "run_optimization": False,  # Set to True after initial testing
        "run_analysis": False,  # Disable for quick test
        "run_format_checks": False,  # Disable for quick test
    }
    target_modes = ["base"]

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        # Calculate timeout based on number of simulations
        # Allow ~1 second per 100 simulations, with minimum 60 seconds
        total_sims = sum(num_sim_args.values())
        timeout_seconds = max(60, int(total_sims / 100) + 30)  # Minimum 60s, +30s buffer
        
        print(f"\nStarting simulation with timeout: {timeout_seconds} seconds")
        print(f"Total simulations: {total_sims}")
        print(f"If simulation hangs, it will timeout after {timeout_seconds} seconds\n")
        
        try:
            run_with_timeout(
                create_books,
                timeout_seconds,
                gamestate,
                config,
                num_sim_args,
                batching_size,
                num_threads,
                compression,
                profiling,
            )
        except TimeoutError as e:
            print(f"\n{'='*60}")
            print(f"ERROR: {e}")
            print(f"{'='*60}")
            print("\nPossible causes:")
            print("  1. Infinite loop in check_repeat() logic")
            print("  2. force_freegame: True but reel strips can't trigger")
            print("  3. Deadlock in multi-threading")
            print("  4. Reel strip doesn't have enough FS scatters")
            print("\nCheck:")
            print("  - Run analyze_reels.py to verify FS symbol counts")
            print("  - Check game_override.py check_repeat() logic")
            print("  - Verify force_freegame conditions in game_config.py")
            print(f"{'='*60}\n")
            raise

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}, {"symbol": "fs_scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)

