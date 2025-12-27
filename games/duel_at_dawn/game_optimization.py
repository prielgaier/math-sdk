"""Set conditions/parameters for optimization program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructConditions,
    ConstructFenceBias,
    verify_optimization_input,
)


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.01, av_win=5000, search_conditions=5000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame_www": ConstructConditions(
                        rtp=0.37, hr=200, search_conditions={"symbol": "fs_scatter"}
                    ).return_dict(),
                    "freegame_dtd": ConstructConditions(
                        rtp=0.15, hr=500, search_conditions={"symbol": "fs_scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.44).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.5,
                            "win_range": (10, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame_www",
                            "scale_factor": 0.8,
                            "win_range": (1000, 2000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame_dtd",
                            "scale_factor": 1.2,
                            "win_range": (3000, 4000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame", "freegame_www", "freegame_dtd"],
                    bias_ranges=[(2.5, 5.5), (200.0, 500.0), (500.0, 1000.0)],
                    bias_weights=[0.7, 0.2, 0.1],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)

