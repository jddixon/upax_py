#!/usr/bin/env python3

import mistune

MD_ = "[link to Consensus](https://en.wikipedia.org/wiki/Consensus_%28computer_science%29)"

OUTPUT_ = mistune.markdown(MD_)
print(OUTPUT_)
