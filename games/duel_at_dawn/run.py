"""Main file for generating results for Duel At Dawn game."""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

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
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}, {"symbol": "fs_scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)

