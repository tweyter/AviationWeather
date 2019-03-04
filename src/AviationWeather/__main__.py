import sys

from AviationWeather import calculations, converter


def calc():
    calculations.main()


def conv():
    converter.main(sys.argv)
