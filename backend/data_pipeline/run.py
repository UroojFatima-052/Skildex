"""Run the pipeline. Usage: python -m data_pipeline.run"""

from data_pipeline.clean import clean
from data_pipeline.sources import djinni

SOURCES = [djinni]


def main():
    for source in SOURCES:
        df = source.load()
        clean(df, source.SOURCE_NAME)


if __name__ == "__main__":
    main()