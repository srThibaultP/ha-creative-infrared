"""Media player platform for the Creative infrared integration."""

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import SOURCES, CreativeStageV2Code
from .entity import CreativeIrEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the soundbar media player."""
    async_add_entities([CreativeIrMediaPlayer(entry)])


class CreativeIrMediaPlayer(CreativeIrEntity, MediaPlayerEntity, RestoreEntity):
    """Creative IR media player.

    IR is one-way and the soundbar has a single power toggle that it also
    flips on its own (auto standby, HDMI CEC), so the power state is not
    tracked: the entity stays on and both turn on and turn off send the power
    key. Mute and source are assumed from the last command sent and restored
    across restarts.
    """

    _attr_name = None
    _attr_assumed_state = True
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_source_list = list(SOURCES)
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the soundbar media player."""
        super().__init__(entry, unique_id_suffix="media_player")
        self._attr_state = MediaPlayerState.ON
        self._attr_is_volume_muted = False

    async def async_added_to_hass(self) -> None:
        """Restore the assumed state."""
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) is None:
            return
        self._attr_is_volume_muted = bool(last.attributes.get("is_volume_muted"))
        if (source := last.attributes.get("source")) in SOURCES:
            self._attr_source = source

    async def _press(self, code: CreativeStageV2Code) -> None:
        await self._send_code(code)
        self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        """Press the power key (it toggles)."""
        await self._send_code(CreativeStageV2Code.POWER)

    async def async_turn_off(self) -> None:
        """Press the power key (it toggles)."""
        await self._send_code(CreativeStageV2Code.POWER)

    async def async_volume_up(self) -> None:
        """Send volume up."""
        self._attr_is_volume_muted = False
        await self._press(CreativeStageV2Code.VOLUME_UP)

    async def async_volume_down(self) -> None:
        """Send volume down."""
        self._attr_is_volume_muted = False
        await self._press(CreativeStageV2Code.VOLUME_DOWN)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute or unmute (the mute button toggles)."""
        if mute != self._attr_is_volume_muted:
            self._attr_is_volume_muted = mute
            await self._press(CreativeStageV2Code.MUTE)

    async def async_media_play(self) -> None:
        """Send play/pause."""
        self._attr_state = MediaPlayerState.PLAYING
        await self._press(CreativeStageV2Code.PLAY_PAUSE)

    async def async_media_pause(self) -> None:
        """Send play/pause."""
        self._attr_state = MediaPlayerState.PAUSED
        await self._press(CreativeStageV2Code.PLAY_PAUSE)

    async def async_media_next_track(self) -> None:
        """Send next track."""
        await self._press(CreativeStageV2Code.NEXT)

    async def async_media_previous_track(self) -> None:
        """Send previous track."""
        await self._press(CreativeStageV2Code.PREVIOUS)

    async def async_select_source(self, source: str) -> None:
        """Press the source button."""
        self._attr_source = source
        await self._press(SOURCES[source])
