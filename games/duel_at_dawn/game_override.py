from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is used to override or extend universal state.py functions.
    Handles Duel At Dawn specific logic for VS and Outlaw features.
    """

    def reset_book(self):
        """Reset game specific properties"""
        super().reset_book()
        self.expanding_wilds = []  # Track expanding wild reels
        self.duel_reels = []       # Track VS symbol reels (DuelReels)
        self.outlaw_reels = []     # Track Outlaw symbol reels
        self.shot_wilds = []       # Track randomly placed wilds from Outlaw
        self.freegame_mode = None  # "wild_wild_west" or "dusk_til_dawn"
        self.available_reels = [i for i in range(self.config.num_reels)]

    def assign_special_sym_function(self):
        """Assign special symbol functions"""
        self.special_symbol_functions = {
            "W": [self.assign_mult_property],
            "VS": [self.assign_duel_property],
            "O": [self.assign_outlaw_property],
        }

    def assign_mult_property(self, symbol):
        """Assign multiplier to wild symbols in free game"""
        if self.gametype != self.config.basegame_type:
            mult_values = self.get_current_distribution_conditions().get(
                "duel_mult_values", {}
            )
            if not mult_values:
                mult_values = {2: 200, 3: 150, 4: 100, 5: 80, 10: 50, 20: 30, 50: 20, 100: 10, 200: 5}
            multiplier_value = get_random_outcome(mult_values)
            symbol.assign_attribute({"multiplier": multiplier_value})

    def assign_duel_property(self, symbol):
        """Assign duel multiplier to VS symbol"""
        # Duel multiplier range: 2x to 200x
        mult_values = self.get_current_distribution_conditions().get(
            "duel_mult_values", {}
        )
        if not mult_values:
            mult_values = {2: 200, 3: 150, 4: 100, 5: 80, 10: 50, 20: 30, 50: 20, 100: 10, 200: 5}
        duel_mult = get_random_outcome(mult_values)
        symbol.assign_attribute({"duel_multiplier": duel_mult})

    def assign_outlaw_property(self, symbol):
        """Assign properties to Outlaw symbol"""
        # Outlaw can shoot 1-6 wilds with multipliers
        num_wilds = get_random_outcome({1: 200, 2: 150, 3: 100, 4: 50, 5: 20, 6: 10})
        symbol.assign_attribute({"num_wilds": num_wilds})
        
        # Assign multiplier values for shot wilds
        mult_values = self.get_current_distribution_conditions().get(
            "outlaw_mult_values", {}
        )
        if not mult_values:
            mult_values = {2: 300, 3: 200, 4: 150, 5: 100, 10: 50, 20: 30, 50: 15, 100: 8, 200: 3}
        symbol.assign_attribute({"wild_mult_values": mult_values})

    def check_repeat(self) -> None:
        """Checks if the spin failed a criteria constraint at any point."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_freegame"] and not (self.triggered_freegame):
                self.repeat = True

            # Only repeat for zero wins if:
            # 1. Criteria is "0" (zero-win criteria) - this should never happen as "0" expects 0 wins
            # 2. OR criteria has an explicit win_criteria that requires non-zero win
            # For "basegame" and other criteria without win_criteria, 0 wins are allowed
            if self.win_manager.running_bet_win == 0.0:
                if self.criteria == "0":
                    # Criteria "0" expects 0 wins, so this is correct - don't repeat
                    pass
                elif win_criteria is not None and win_criteria > 0:
                    # Criteria requires a specific non-zero win, but got 0 - repeat
                    self.repeat = True
                # For criteria like "basegame" with no win_criteria, 0 wins are allowed - don't repeat
        
        # Call parent to increment repeat_count and check for warnings
        super().check_repeat()

