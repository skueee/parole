import abc
import sys
from dataclasses import dataclass

if sys.platform == "linux":
    from dbus_next.aio import MessageBus
else:
    MessageBus = None


class NoMPRISException(Exception):
    def __init__(self):
        super().__init__(
            "MPRIS was not found on your system\nIf you are not on Linux, this error is intended"
        )


class MPRISNotConnectedException(Exception):
    def __init__(self):
        super().__init__("The MPRIS client is not connected")


@dataclass
class TrackMetadata:
    active: bool
    title: str | None = None
    album: str | None = None
    artist: str | None = None


class BaseMediaProvider(abc.ABC):
    @abc.abstractmethod
    async def init(self):
        """Initialize the provider"""

    async def get_metadata(self) -> TrackMetadata | None:
        """Fetch current song details."""


class LinuxMediaProvider(BaseMediaProvider):
    def __init__(self):
        self.bus = None

    async def init(self):
        if not self.bus:
            return await self.connect()

    async def connect(self):
        if not MessageBus:
            raise NoMPRISException
        try:
            # Connect to the Linux Session D-Bus
            self.bus = await MessageBus().connect()
            return True
        except Exception:  # noqa: BLE001
            raise NoMPRISException

    async def get_active_player_name(self) -> str | None:
        if not self.bus:
            raise MPRISNotConnectedException

        introspection = await self.bus.introspect(
            "org.freedesktop.DBus", "/org/freedesktop/DBus"
        )

        dbus_obj = self.bus.get_proxy_object(
            "org.freedesktop.DBus", "/org/freedesktop/DBus", introspection
        )
        dbus_iface = dbus_obj.get_interface("org.freedesktop.DBus")
        names = await dbus_iface.call_list_names()

        for name in names:
            if name.startswith("org.mpris.MediaPlayer2."):
                return name
        return None

    async def get_metadata(self) -> TrackMetadata:
        player_name = await self.get_active_player_name()
        if not player_name:
            return TrackMetadata(active=False)

        introspection = await self.bus.introspect(
            player_name, "/org/mpris/MediaPlayer2"
        )
        obj = self.bus.get_proxy_object(
            player_name, "/org/mpris/MediaPlayer2", introspection
        )

        props = obj.get_interface("org.freedesktop.DBus.Properties")

        metadata_variant = await props.call_get(
            "org.mpris.MediaPlayer2.Player", "Metadata"
        )

        metadata = metadata_variant.value

        artist_var = metadata.get("xesam:artist", [None])
        title_var = metadata.get("xesam:title", None)
        album_var = metadata.get("xesam:album", None)

        title = title_var.value if title_var else None
        album = album_var.value if album_var else None
        artist = None
        try:
            artist = artist_var.value[0]
        except AttributeError:
            artist = artist_var[0]

        return TrackMetadata(
            active=True,
            title=title,
            album=album,
            artist=artist,
        )


class PlatformNotSupportedError(Exception):
    def __init__(self, platform: str) -> None:
        super().__init__(f"Platform not supported: {platform}")


_cached_provider: BaseMediaProvider | None = None


def get_provider() -> BaseMediaProvider:
    global _cached_provider
    if _cached_provider is None:
        if sys.platform == "linux":
            _cached_provider = LinuxMediaProvider()
        else:
            raise PlatformNotSupportedError(sys.platform)
    return _cached_provider
