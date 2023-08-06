#!/usr/bin/python
# -*- coding: UTF-8 -*-
from re import search
from onesheet.TimeBasedMetadata import TimeBasedMetadata
from abc import ABCMeta

class VideoMetadata(TimeBasedMetadata):
    __metaclass__ = ABCMeta

    def __init__(self, filename):
        TimeBasedMetadata.__init__(self, filename)


    def __convertFrameToNDF(self, aFrameNumber):
        pass

    def __convertFrameToDF(self, aFrameNumber):
        pass

    def __sizeofHuman(self, num):
        num = int(num)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    @property
    def videoCodec(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return stream.getAttribute("codec_name")

    @property
    def videoCodecLongName(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return stream.getAttribute("codec_long_name")
    @property
    def videoCodecTagString(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return stream.getAttribute("codec_tag_string")


    @property
    def videoCodecTag(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return stream.getAttribute("codec_tag")

    @property
    def videoFrameRate(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    top = float(stream.getAttribute("r_frame_rate").split('/')[0])
                    bottom = float(stream.getAttribute("r_frame_rate").split('/')[1])

                    return top/bottom


    @property
    def videoColorSpace(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    if stream.getAttribute("color_space"):
                        return str(stream.getAttribute("color_space"))
        pass

    @property
    def videoColorDepth(self):
        # TODO Make videoColorDepth method useful
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                if stream.getAttribute("codec_long_name") == "Uncompressed 4:2:2 10-bit":
                    return 10
                else:
                    return str(stream.getAttribute("bits_per_raw_sample"))


        pass

    @property
    def videoColorSampling(self):
        # TODO Make VideoColorSampling method useful
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    if stream.getAttribute("codec_long_name") == "Uncompressed 4:2:2 10-bit":
                        return '4:2:2'
                    else:
                        return 'unknown'
        pass

    @property
    def videoBitRate(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return int(stream.getAttribute("bit_rate"))

    @property
    def videoBitRateH(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return self.__sizeofHuman(int(stream.getAttribute("bit_rate")))+"/s"

    @property
    def videoResolution(self):
            for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    height = stream.getAttribute("height")
                    width = stream.getAttribute("width")
                    return width + " x " + height

    @property
    def videoResolutionHeight(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return int(stream.getAttribute("height"))

    @property
    def videoResolutionWidth(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return int(stream.getAttribute("width"))

    @property
    def videoAspectRatio(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
                if stream.getAttribute("codec_type") == "video":
                    return str(stream.getAttribute("display_aspect_ratio"))
