"""Events specific to Duel At Dawn features."""

from copy import deepcopy
from src.events.event_constants import EventConstants
from src.events.events import json_ready_sym

VS_DUEL = "vsDuel"
OUTLAW_FEATURE = "outlawFeature"
FREEGAME_MODE = "freegameMode"
NEW_EXP_WILDS = "newExpandingWilds"
UPDATE_EXP_WILDS = "updateExpandingWilds"


def vs_duel_event(gamestate, vs_events: list) -> None:
    """Create event for VS symbol duels."""
    for vs_event in vs_events:
        event = {
            "index": len(gamestate.book.events),
            "type": VS_DUEL,
            "reel": vs_event["reel"],
            "multiplier": vs_event["multiplier"],
        }
        gamestate.book.add_event(event)


def outlaw_feature_event(gamestate, outlaw_events: list) -> None:
    """Create event for Outlaw feature."""
    for outlaw_event in outlaw_events:
        # Adjust row positions if padding is included
        shot_wilds = deepcopy(outlaw_event["shot_wilds"])
        if gamestate.config.include_padding:
            for wild in shot_wilds:
                wild["row"] += 1
        
        event = {
            "index": len(gamestate.book.events),
            "type": OUTLAW_FEATURE,
            "reel": outlaw_event["reel"],
            "numWilds": outlaw_event["num_wilds"],
            "shotWilds": shot_wilds,
        }
        gamestate.book.add_event(event)


def freegame_mode_event(gamestate, mode: str) -> None:
    """Create event for free game mode."""
    event = {
        "index": len(gamestate.book.events),
        "type": FREEGAME_MODE,
        "mode": mode,  # "wild_wild_west" or "dusk_til_dawn"
    }
    gamestate.book.add_event(event)


def new_expanding_wild_event(gamestate) -> None:
    """Passed after reveal event"""
    new_exp_wilds = gamestate.new_exp_wilds
    if gamestate.config.include_padding:
        for ew in new_exp_wilds:
            ew["row"] += 1

    event = {"index": len(gamestate.book.events), "type": NEW_EXP_WILDS, "newWilds": new_exp_wilds}
    gamestate.book.add_event(event)


def update_expanding_wild_event(gamestate) -> None:
    """On each reveal - the multiplier value on the expanding wild is updated (sent before reveal)"""
    existing_wild_details = deepcopy(gamestate.expanding_wilds)
    wild_event = []
    if gamestate.config.include_padding:
        for ew in existing_wild_details:
            if len(ew) > 0:
                ew["row"] += 1
                wild_event.append(ew)

    event = {"index": len(gamestate.book.events), "type": UPDATE_EXP_WILDS, "existingWilds": wild_event}
    gamestate.book.add_event(event)

