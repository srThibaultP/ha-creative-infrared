"""Constants for the Creative infrared integration."""

from enum import IntEnum

DOMAIN = "creative_infrared"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
DEFAULT_NAME = "Creative Stage V2"

# NEC extended address of the Creative Stage V2 remote
NEC_ADDRESS = 0xA4BF


class CreativeStageV2Code(IntEnum):
    """NEC command bytes of the Creative Stage V2 remote."""

    POWER = 0x40
    MUTE = 0x18
    TV_ARC_USB = 0x10
    OPT_AUX = 0x19
    BLUETOOTH = 0x12
    VOLUME_UP = 0x16
    VOLUME_DOWN = 0x1A
    NEXT = 0x50
    PREVIOUS = 0x51
    PLAY_PAUSE = 0x13
    SURROUND = 0x2A
    RESET = 0x3A
    DIALOG = 0x4A
    MORE = 0x11
    LESS = 0x4C
    BASS_TREBLE = 0x1C


# Source buttons; each one toggles between the two inputs printed on it
SOURCES: dict[str, CreativeStageV2Code] = {
    "TV ARC / USB": CreativeStageV2Code.TV_ARC_USB,
    "OPT / AUX": CreativeStageV2Code.OPT_AUX,
    "Bluetooth": CreativeStageV2Code.BLUETOOTH,
}
