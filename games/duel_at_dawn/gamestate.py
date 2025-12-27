"""Handles the state and output for a single simulation round"""

from game_override import GameStateOverride
from game_events import (
    vs_duel_event,
    outlaw_feature_event,
    freegame_mode_event,
    new_expanding_wild_event,
    update_expanding_wild_event,
)
from src.calculations.lines import Lines
from src.events.events import (
    update_freespin_event,
    reveal_event,
    set_total_event,
    set_win_event,
)
from src.calculations.statistics import get_random_outcome


class GameState(GameStateOverride):
    """Handle all game-logic and event updates for a given simulation number."""

    def run_spin(self, sim, simulation_seed=None):
        """Entry point for all game-modes."""
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board(emit_event=False, trigger_symbol="fs_scatter")

            # Process VS symbols (expand to wild reels)
            vs_events = self.process_vs_symbols()
            if vs_events:
                vs_duel_event(self, vs_events)

            # Process Outlaw symbols
            outlaw_events = self.process_outlaw_symbols()
            if outlaw_events:
                outlaw_feature_event(self, outlaw_events)

            # Emit reveal event
            reveal_event(self)

            # Calculate wins
            self.win_data = Lines.get_lines(
                self.board, self.config, global_multiplier=self.global_multiplier
            )
            Lines.record_lines_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            Lines.emit_linewin_events(self)

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition(scatter_key="fs_scatter") and self.check_freespin_entry(scatter_key="fs_scatter"):
                self.run_freespin_from_base(scatter_key="fs_scatter")

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        """Run free spin mode (Wild Wild West or Dusk 'Til Dawn)."""
        self.reset_fs_spin()
        self.expanding_wilds = []
        self.duel_reels = []
        self.outlaw_reels = []
        self.shot_wilds = []
        self.available_reels = [i for i in range(self.config.num_reels)]

        # Determine free game mode from distribution
        conditions = self.get_current_distribution_conditions()
        self.freegame_mode = conditions.get("freegame_mode", "wild_wild_west")
        freegame_mode_event(self, self.freegame_mode)

        # For Dusk 'Til Dawn, we can force VS symbols (handled in reel strips)
        # The reel strip FR1 should have more VS symbols

        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_board(emit_event=False, trigger_symbol="fs_scatter")

            # Process VS symbols
            vs_events = self.process_vs_symbols()
            if vs_events:
                vs_duel_event(self, vs_events)

            # Process Outlaw symbols
            outlaw_events = self.process_outlaw_symbols()
            if outlaw_events:
                outlaw_feature_event(self, outlaw_events)

            # Handle expanding wilds (if any were created in previous spins)
            wild_on_reveal = get_random_outcome(
                self.get_current_distribution_conditions().get("landing_wilds", {0: 100})
            )
            self.assign_new_wilds(wild_on_reveal)
            self.update_with_existing_wilds()  # Override board with expanding wilds

            reveal_event(self)
            if len(self.expanding_wilds) > 0:
                update_expanding_wild_event(self)
            if len(self.new_exp_wilds) > 0:
                new_expanding_wild_event(self)

            # Track new expanding wilds
            for wild in self.new_exp_wilds:
                self.expanding_wilds.append({"reel": wild["reel"], "row": 0, "mult": wild["mult"]})
            self.expanding_wilds = sorted(self.expanding_wilds, key=lambda x: x["reel"])

            # Calculate wins
            self.win_data = Lines.get_lines(
                self.board, self.config, global_multiplier=self.global_multiplier
            )
            Lines.record_lines_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
            Lines.emit_linewin_events(self)
            self.win_manager.update_gametype_wins(self.gametype)
            
            # Check for retriggers
            if self.check_fs_condition(scatter_key="fs_scatter"):
                self.update_fs_retrigger_amt(scatter_key="fs_scatter")

        self.end_freespin()

