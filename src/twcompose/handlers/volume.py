from collections import OrderedDict
from typing import List, Optional, cast

from twcompose.handlers import CommandHandler
from twcompose.handlers.state import CommandHandlerState
from twcompose.twitter.counts import MonthlyTwitterCountEstimator


class VolumeEstimatorCommandHandler(CommandHandler):
    """Collect volume information for all rules in the streams

    Saves the results in state.
    """

    def rules_to_estimate(self, state: CommandHandlerState) -> List[str]:
        """Resolve the rules to estimate

        If `state.command_args` contains `volume_rules`, then they are returned.
        Otherwise, all the rules in the `twitter-compose.yml` files are used.
        """
        assert state.twitter_compose_config is not None
        command_line_rules = state.command_args.get("volume_rules")
        if command_line_rules:
            return command_line_rules

        # Otherwise, looping through rules in the config
        return [
            item.value
            for queries in state.twitter_compose_config.streams.values()
            for item in queries
        ]

    def handle(self, state: CommandHandlerState) -> None:
        # State requirements
        assert state.twitter_client is not None

        # Getting the volume estimator
        volume_estimator = MonthlyTwitterCountEstimator(state.twitter_client)

        # Getting the rules to estimate
        rules = self.rules_to_estimate(state)

        # Saving volume for each rule
        vol_map = [(rule, volume_estimator.estimate(rule)) for rule in rules]

        # Optionally filtering
        min_volume = cast(Optional[int], state.command_args.get("min"))
        if min_volume:
            vol_map = [
                (rule, volume) for rule, volume in vol_map if volume > min_volume
            ]

        # Sorting and saving in OrderedDict
        state.volume_per_rule = OrderedDict(
            sorted(
                vol_map,
                key=lambda r: r[1],
                reverse=True,
            )
        )

        # Passing to the next handler
        super().handle(state)
