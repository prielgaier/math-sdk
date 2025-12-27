"""Executables for Duel At Dawn features."""

import random
from copy import deepcopy
from game_calculations import GameCalculations
from src.calculations.statistics import get_random_outcome


class GameExecutables(GameCalculations):
    """Executable functions for Duel At Dawn game."""

    def expand_vs_reel(self, reel_index: int, duel_mult: int):
        """Expand VS symbol to full wild reel with duel multiplier."""
        # Replace entire reel with wilds
        for row in range(len(self.board[reel_index])):
            wild_symbol = self.create_symbol("W")
            wild_symbol.assign_attribute({"multiplier": duel_mult})
            self.board[reel_index][row] = wild_symbol
        
        # Track this expanding reel
        if reel_index not in self.duel_reels:
            self.duel_reels.append(reel_index)
            # Remove from available reels
            if reel_index in self.available_reels:
                self.available_reels.remove(reel_index)

    def expand_outlaw_reel(self, reel_index: int):
        """Expand Outlaw symbol to full wild reel."""
        # Replace entire reel with wilds (base multiplier 1x)
        for row in range(len(self.board[reel_index])):
            wild_symbol = self.create_symbol("W")
            wild_symbol.assign_attribute({"multiplier": 1})
            self.board[reel_index][row] = wild_symbol
        
        # Track this expanding reel
        if reel_index not in self.outlaw_reels:
            self.outlaw_reels.append(reel_index)
            # Remove from available reels
            if reel_index in self.available_reels:
                self.available_reels.remove(reel_index)

    def shoot_outlaw_wilds(self, num_wilds: int, mult_values: dict):
        """Shoot random wilds onto the board from Outlaw feature."""
        shot_wilds = []
        available_positions = []
        
        # Get all available positions (not already wild reels)
        for reel_idx in range(self.config.num_reels):
            if reel_idx not in self.outlaw_reels and reel_idx not in self.duel_reels:
                for row_idx in range(self.config.num_rows[reel_idx]):
                    available_positions.append((reel_idx, row_idx))
        
        # Randomly select positions
        if len(available_positions) >= num_wilds:
            selected_positions = random.sample(available_positions, num_wilds)
            
            for reel_idx, row_idx in selected_positions:
                # Assign random multiplier
                mult = get_random_outcome(mult_values)
                wild_symbol = self.create_symbol("W")
                wild_symbol.assign_attribute({"multiplier": mult})
                self.board[reel_idx][row_idx] = wild_symbol
                
                shot_wilds.append({
                    "reel": reel_idx,
                    "row": row_idx,
                    "multiplier": mult
                })
        elif len(available_positions) > 0:
            # If not enough positions, use all available
            for reel_idx, row_idx in available_positions:
                mult = get_random_outcome(mult_values)
                wild_symbol = self.create_symbol("W")
                wild_symbol.assign_attribute({"multiplier": mult})
                self.board[reel_idx][row_idx] = wild_symbol
                
                shot_wilds.append({
                    "reel": reel_idx,
                    "row": row_idx,
                    "multiplier": mult
                })
        
        return shot_wilds

    def process_vs_symbols(self):
        """Process all VS symbols on the board."""
        vs_events = []
        
        for reel_idx in range(self.config.num_reels):
            for row_idx in range(self.config.num_rows[reel_idx]):
                symbol = self.board[reel_idx][row_idx]
                if symbol.name == "VS":
                    if symbol.check_attribute("duel_multiplier"):
                        duel_mult = symbol.get_attribute("duel_multiplier")
                    else:
                        duel_mult = 2  # Default if not assigned
                    self.expand_vs_reel(reel_idx, duel_mult)
                    vs_events.append({
                        "reel": reel_idx,
                        "multiplier": duel_mult
                    })
        
        return vs_events

    def process_outlaw_symbols(self):
        """Process all Outlaw symbols on the board."""
        outlaw_events = []
        
        for reel_idx in range(self.config.num_reels):
            for row_idx in range(self.config.num_rows[reel_idx]):
                symbol = self.board[reel_idx][row_idx]
                if symbol.name == "O":
                    # Expand reel first
                    self.expand_outlaw_reel(reel_idx)
                    
                    # Shoot wilds
                    if symbol.check_attribute("num_wilds"):
                        num_wilds = symbol.get_attribute("num_wilds")
                    else:
                        num_wilds = 1  # Default
                    
                    if symbol.check_attribute("wild_mult_values"):
                        mult_values = symbol.get_attribute("wild_mult_values")
                    else:
                        mult_values = {2: 100, 3: 50, 4: 30, 5: 20}  # Default
                    
                    shot_wilds = self.shoot_outlaw_wilds(num_wilds, mult_values)
                    
                    outlaw_events.append({
                        "reel": reel_idx,
                        "num_wilds": num_wilds,
                        "shot_wilds": shot_wilds
                    })
        
        return outlaw_events

    def update_with_existing_wilds(self) -> None:
        """Replace drawn boards with existing sticky-wilds (for free spins)."""
        updated_exp_wild = []
        for expwild in self.expanding_wilds:
            new_mult_on_reveal = get_random_outcome(
                self.get_current_distribution_conditions()["mult_values"][self.gametype]
            )
            expwild["mult"] = new_mult_on_reveal
            updated_exp_wild.append({"reel": expwild["reel"], "row": 0, "mult": new_mult_on_reveal})
            for row, _ in enumerate(self.board[expwild["reel"]]):
                self.board[expwild["reel"]][row] = self.create_symbol("W")
                self.board[expwild["reel"]][row].assign_attribute({"multiplier": new_mult_on_reveal})

    def assign_new_wilds(self, max_num_new_wilds: int):
        """Assign unused reels to have sticky symbol."""
        self.new_exp_wilds = []
        for _ in range(max_num_new_wilds):
            if len(self.available_reels) > 0:
                chosen_reel = random.choice(self.available_reels)
                chosen_row = random.choice([i for i in range(self.config.num_rows[chosen_reel])])
                self.available_reels.remove(chosen_reel)

                wr_mult = get_random_outcome(
                    self.get_current_distribution_conditions()["mult_values"][self.gametype]
                )
                expwild_details = {"reel": chosen_reel, "row": chosen_row, "mult": wr_mult}
                self.board[expwild_details["reel"]][expwild_details["row"]] = self.create_symbol("W")
                self.board[expwild_details["reel"]][expwild_details["row"]].assign_attribute(
                    {"multiplier": wr_mult}
                )
                self.new_exp_wilds.append(expwild_details)

    def run_freespin_from_base(self, scatter_key: str = "fs_scatter") -> None:
        """Override to use fs_scatter by default."""
        # Store the freegame_mode from distribution before entering free spins
        conditions = self.get_current_distribution_conditions()
        self.freegame_mode = conditions.get("freegame_mode", "wild_wild_west")
        
        self.record(
            {
                "kind": self.count_special_symbols(scatter_key),
                "symbol": scatter_key,
                "gametype": self.gametype,
            }
        )
        self.update_freespin_amount(scatter_key=scatter_key)
        self.run_freespin()

    def create_board_reelstrips(self) -> None:
        """Override to use correct reel based on freegame_mode in free game."""
        # If in free game mode, use the stored freegame_mode to select reel
        if self.gametype == self.config.freegame_type and hasattr(self, 'freegame_mode'):
            # Temporarily modify reel_weights to force the correct reel
            conditions = self.get_current_distribution_conditions()
            original_weights = conditions["reel_weights"][self.gametype].copy()
            
            if self.freegame_mode == "dusk_til_dawn":
                # Force FR1 for Dusk 'Til Dawn
                conditions["reel_weights"][self.gametype] = {"FR1": 1}
            else:
                # Use FR0 for Wild Wild West (default)
                conditions["reel_weights"][self.gametype] = {"FR0": 1}
        
        # Call parent method
        super().create_board_reelstrips()
        
        # Restore original weights if we modified them
        if self.gametype == self.config.freegame_type and hasattr(self, 'freegame_mode'):
            if 'original_weights' in locals():
                conditions["reel_weights"][self.gametype] = original_weights

