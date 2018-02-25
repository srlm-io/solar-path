#!/usr/bin/python3.6


import math
from datetime import datetime

import pytz
from PIL import Image, ImageDraw, ImageFont
from pysolar import radiation, solar

tz = pytz.timezone("US/Pacific")

position = [48.06288, -118.1776]  # shopside

dates = [
    [2017, 12, 21],  # shortest day of the year
    [2018, 6, 21]  # longest day of the year
]

im = Image.open("shopside_working.jpg")

center_x = 1629
center_y = 1193

deg_15 = 3041
deg_10 = 3114

radius = 10

draw = ImageDraw.Draw(im, 'RGBA')
draw.ellipse(
    (center_x - radius, center_y - radius,
     center_x + radius, center_y + radius),
    fill=(128, 0, 0, 256))

draw.ellipse(
    (deg_10 - radius, center_y - radius,
     deg_10 + radius, center_y + radius),
    fill=(128, 0, 0, 256))


def calculateDistance(elevation):
    deg_15_pixels = deg_15 - center_x
    deg_10_pixels = deg_10 - center_x

    m = (deg_15_pixels - deg_10_pixels) / 5

    b = deg_15_pixels - m * 15

    return m * elevation + b


def calculateX(distance_pixel, azimuth):
    return math.cos((180 - azimuth) * math.pi / 180) * distance_pixel


def calculateY(distance_pixel, azimuth):
    return -math.sin((180 - azimuth) * math.pi / 180) * distance_pixel


font = ImageFont.truetype("Waree.ttf", 16)


for date in dates:
    previous_solar_center_x = None
    previous_solar_center_y = None

    print('-----------------------------------------------------')
    print(date)
    print('{:10} {:20} {:20} {}'.format('time', 'elevation', 'azimuth', 'radiation_w_m2'))

    for hour in range(0, 24):
        for minute in [0, 15, 30, 45]:
            sample_time = tz.localize(datetime(*date, hour, minute, 0), is_dst=None)
            elevation = solar.get_altitude(*position, sample_time)
            # Move the 0 point to the north
            azimuth = (540 - solar.get_azimuth(*position, sample_time)) % 360
            radiation_w_m2 = radiation.get_radiation_direct(sample_time, elevation)

            print('{:10} {:20} {:20} {}'.format(sample_time.strftime('%H:%M %Z'), elevation, azimuth, radiation_w_m2))

            if elevation < 0:
                previous_solar_center_x = None
                previous_solar_center_y = None
                continue

            distance_pixel = calculateDistance(elevation)
            elevation_pixel = calculateX(distance_pixel, azimuth)
            azimuth_pixel = calculateY(distance_pixel, azimuth)

            # radius = radiation_w_m2 / 20
            #
            # if radius > 50:
            #     radius = 50

            # TODO have the width of the line be an average of previous and current point (otherwise we lag a bit
            step_solar_center_x = center_x - elevation_pixel
            step_solar_center_y = center_y + azimuth_pixel

            width = (radiation_w_m2 - 250) / 5

            if width < 0:
                continue

            if previous_solar_center_x is not None and previous_solar_center_y is not None:
                draw.line([
                    (previous_solar_center_x, previous_solar_center_y),
                    (step_solar_center_x, step_solar_center_y)],
                    width=math.floor(width), fill=(256, 0, 0, 128))

            # draw.ellipse((center_x - radius - elevation_pixel, center_y - radius + azimuth_pixel,
            #              center_x + radius - elevation_pixel, center_y + radius + azimuth_pixel), fill=(128, 0, 0, 128))

            # radius = 3
            # draw.ellipse((center_x - radius - elevation_pixel, center_y - radius + azimuth_pixel,
            #               center_x + radius - elevation_pixel, center_y + radius + azimuth_pixel), fill=256)

            text_x = center_x - elevation_pixel + 10
            text_y = center_y + azimuth_pixel - 16

            # draw.line([(text_x, text_y), (text_x+50, text_y)], width=15, fill=(128, 128, 128, 128))

            draw.text((text_x, text_y), sample_time.strftime('%H:%M %Z'), (255, 255, 255), font=font)

            previous_solar_center_x = step_solar_center_x
            previous_solar_center_y = step_solar_center_y


im.save("output.png")
