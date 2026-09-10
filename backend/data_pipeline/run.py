import sys

from data_pipeline.clean import clean
from data_pipeline.sources import djinni, ats

SOURCES = {"djinni": djinni, "ats": ats}


def main():
    names = sys.argv[1:] or list(SOURCES)
    for name in names:
        source = SOURCES[name]
        clean(source.load(), source.SOURCE_NAME)


if __name__ == "__main__":
    main()