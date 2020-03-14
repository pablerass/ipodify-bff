# -*- coding: utf-8 -*-
"""ipodify BFF main."""
import sys

from ipodify_bff.app import app


def main():
    """Launch app."""
    app.run()


if __name__ == "__main__":
    sys.exit(main())
