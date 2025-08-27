import re
import random
import json
import os
from streamlink.plugin import Plugin
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream

_url_re = re.compile(r"https?://(\w+\.)?stripchat\.com/(?P<username>[a-zA-Z0-9_-]+)")


class Stripchat(Plugin):
    @classmethod
    def can_handle_url(cls, url):
        return _url_re.match(url)

    def _get_streams(self):
        data = self.session.http.json(
            self.session.http.get(
                "https://stripchat.com/api/front/v2/models/username/{0}/cam".format(
                    _url_re.match(self.url).group("username")
                ),
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": self.url,
                },
            )
        )
        with open(
            os.path.dirname(os.path.realpath(__file__)) + "/debug.json", "w"
        ) as fp:
            fp.write(json.dumps(data, indent=4))

        self.logger.info("Stream live: {0}".format(data["user"]["user"]["isLive"]))
        self.logger.info("Stream status: {0}".format(data["user"]["user"]["status"]))
        self.logger.info(
            "Qualities available: {0}".format(
                ", ".join(data["cam"]["broadcastSettings"]["presets"]["default"])
            )
        )

        num = random.choice(
            [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "19",
                "20",
                "21",
                "22",
                "23",
                "24",
            ]
        )

        # https://edge-hls.doppiocdn.live/hls/62310556/master/62310556_auto.m3u8?playlistType=lowLatency
        # https://media-hls.doppiocdn.net/b-hls-10/62310556/62310556_1080p.m3u8?psch=v1&pkey=Zokee2OhPh9kugh4&playlistType=lowLatency
        # headers = {
        #     "Referer": self.url,
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
        # }
        # cookies = {"stripchat_com_sessionId": "...", "other cookie": "..."}

        if data["user"]["user"]["isLive"] is True:
            try:
                for s in HLSStream.parse_variant_playlist(
                    self.session,
                    "https://edge-hls.doppiocdn.live/hls/{0}/master/{0}_auto.m3u8".format(data["cam"]["streamName"]), # fmt: skip
                ).items():
                    self.logger.info("Stream: {0}".format(s))
                    yield s
            except IOError as err:
                stream = HLSStream(
                    self.session,
                    "https://media-hls.doppiocdn.live/b-hls-{0}/{1}/{1}_{2}.m3u8".format(num, data["cam"]["streamName"], data["cam"]["broadcastSettings"]["presets"]["default"][0]), # fmt: skip
                )
                self.logger.info("Stream: {0}".format(stream))
                yield "Auto", stream


__plugin__ = Stripchat
