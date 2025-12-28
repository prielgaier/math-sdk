"""Duel At Dawn game configuration file."""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Duel At Dawn configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "duel_at_dawn"
        self.provider_number = 0
        self.working_name = "Duel At Dawn"
        self.wincap = 5000.0
        self.win_type = "lines"
        self.rtp = 0.9700
        self.construct_paths()

        # Game Dimensions - 5x5 grid
        self.num_reels = 5
        self.num_rows = [5] * self.num_reels

        # Paytable
        self.paytable = {
            (5, "W"): 50,
            (4, "W"): 20,
            (3, "W"): 10,
            (5, "H1"): 50,
            (4, "H1"): 20,
            (3, "H1"): 10,
            (5, "H2"): 30,
            (4, "H2"): 12,
            (3, "H2"): 6,
            (5, "H3"): 20,
            (4, "H3"): 8,
            (3, "H3"): 4,
            (5, "H4"): 15,
            (4, "H4"): 6,
            (3, "H4"): 3,
            (5, "H5"): 10,
            (4, "H5"): 4,
            (3, "H5"): 2,
            (5, "L1"): 5,
            (4, "L1"): 2,
            (3, "L1"): 1,
            (5, "L2"): 3,
            (4, "L2"): 1.5,
            (3, "L2"): 0.7,
            (5, "L3"): 2,
            (4, "L3"): 1,
            (3, "L3"): 0.5,
            (5, "L4"): 1.5,
            (4, "L4"): 0.7,
            (3, "L4"): 0.3,
        }

        # 19 Fixed Paylines for 5x5 grid
        # Each payline is defined as [row_reel0, row_reel1, row_reel2, row_reel3, row_reel4]
        # where row indices are 0-4 (0 = top row, 4 = bottom row)
        # Based on the "WAYS TO WIN" payline diagram
        self.paylines = {
            # Horizontal lines (5) - Straight across each row
            1: [0, 0, 0, 0, 0],  # Top row horizontal
            2: [1, 1, 1, 1, 1],  # Second row horizontal
            3: [2, 2, 2, 2, 2],  # Middle row horizontal
            4: [3, 3, 3, 3, 3],  # Fourth row horizontal
            5: [4, 4, 4, 4, 4],  # Bottom row horizontal
            # V-shapes (2)
            6: [0, 1, 2, 1, 0],  # V-shape: top(0)-middle(1)-bottom(2)-middle(1)-top(0)
            7: [2, 1, 0, 1, 2],  # Inverted V-shape: bottom(2)-middle(1)-top(0)-middle(1)-bottom(2)
            # Diagonals (2)
            8: [0, 1, 2, 3, 4],  # Diagonal: top-left(0) to bottom-right(4)
            9: [4, 3, 2, 1, 0],  # Diagonal: bottom-left(4) to top-right(0)
            # Zigzags (2)
            10: [0, 1, 2, 1, 0],  # Zigzag: top-bottom-top-bottom-top pattern
            11: [2, 1, 0, 1, 2],  # Zigzag: bottom-top-bottom-top-bottom pattern
            # W-shapes (2)
            12: [0, 1, 0, 1, 0],  # W-shape: top(0)-second(1)-top(0)-second(1)-top(0)
            13: [2, 1, 2, 1, 2],  # W-shape variant: middle(2)-second(1)-middle(2)-second(1)-middle(2)
            # Diagonal W-shapes (2)
            14: [0, 1, 2, 3, 4],  # Diagonal W: top to bottom (same as diagonal 8 - needs correction)
            15: [4, 3, 2, 1, 0],  # Diagonal W: bottom to top (same as diagonal 9 - needs correction)
            # Diamond pattern (1)
            16: [2, 1, 0, 1, 2],  # Diamond: middle(2)-second(1)-top(0)-second(1)-middle(2)
            # Curved/Complex patterns (3)
            17: [0, 0, 0, 1, 1],  # Top-left 3 positions, then middle-right 2 positions
            18: [1, 1, 1, 0, 0],  # Middle-left 3 positions, then top-right 2 positions
            19: [0, 1, 2, 1, 0],  # Complex X-pattern (needs correction based on image)
        }

        self.include_padding = True
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "multiplier": ["W"],
            "vs": ["VS"],  # VS symbol for DuelReels feature
            "outlaw": ["O"],  # Outlaw symbol
            "fs_scatter": ["FS"],  # Free spin scatter
        }

        # Free Spin Triggers
        # 3 FS scatters = Wild Wild West (10 spins)
        # 4 FS scatters = Dusk 'Til Dawn (10 spins)
        self.freespin_triggers = {
            self.basegame_type: {
                3: 10,  # 3 FS scatters = 10 spins (Wild Wild West)
                4: 10,  # 4 FS scatters = 10 spins (Dusk 'Til Dawn)
            },
            self.freegame_type: {
                3: 5,   # Retrigger with 3 FS scatters
                4: 10,  # Retrigger with 4 FS scatters
            },
        }
        self.anticipation_triggers = {
            self.basegame_type: 2,  # Anticipation at 2 FS scatters
            self.freegame_type: 2,
        }

        # Reels
        reels = {
            "BR0": "BR0.csv",      # Base game reel
            "FR0": "FR0.csv",      # Free game reel (Wild Wild West)
            "FR1": "FR1.csv",      # Free game reel (Dusk 'Til Dawn)
            "WCAP": "WCAP.csv",    # Win cap reel
        }
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels = {
            "basegame": self.reels["BR0"],
            "freegame": self.reels["FR0"],
        }

        # Duel multiplier values: 2x to 200x
        duel_mult_values = {
            2: 200, 3: 150, 4: 100, 5: 80, 10: 50, 20: 30, 50: 20, 100: 10, 200: 5
        }

        # Outlaw wild multipliers: 2x to 200x
        outlaw_mult_values = {
            2: 300, 3: 200, 4: 150, 5: 100, 10: 50, 20: 30, 50: 15, 100: 8, 200: 3
        }

        # Bet Modes
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # Win Cap Distribution
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FR1": 1},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": False,  # Disabled to prevent infinite loops if reel strips can't trigger
                            "duel_mult_values": duel_mult_values,
                            "outlaw_mult_values": outlaw_mult_values,
                        },
                    ),
                    # Free Game Distribution (Wild Wild West - 3 scatters)
                    Distribution(
                        criteria="freegame_www",
                        quota=0.05,  # 5% chance
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 100},  # Force 3 FS scatters
                            "force_wincap": False,
                            "force_freegame": True,  # Re-enabled after fixing FR1.csv
                            "freegame_mode": "wild_wild_west",
                            "duel_mult_values": {k: int(v * 0.8) for k, v in duel_mult_values.items()},
                            "outlaw_mult_values": {k: int(v * 0.8) for k, v in outlaw_mult_values.items()},
                        },
                    ),
                    # Free Game Distribution (Dusk 'Til Dawn - 4 scatters)
                    Distribution(
                        criteria="freegame_dtd",
                        quota=0.02,  # 2% chance
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR1": 1},  # Different reel for Dusk 'Til Dawn
                            },
                            "scatter_triggers": {4: 100},  # Force 4 FS scatters
                            "force_wincap": False,
                            "force_freegame": True,  # Re-enabled after fixing FR1.csv
                            "freegame_mode": "dusk_til_dawn",
                            "duel_mult_values": {k: int(v * 1.2) for k, v in duel_mult_values.items()},
                            "outlaw_mult_values": {k: int(v * 1.2) for k, v in outlaw_mult_values.items()},
                            "guaranteed_vs": True,  # Guarantee VS symbols in Dusk 'Til Dawn
                        },
                    ),
                    # Zero Win Distribution
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    # Base Game Distribution
                    Distribution(
                        criteria="basegame",
                        quota=0.529,  # Remaining quota
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]

