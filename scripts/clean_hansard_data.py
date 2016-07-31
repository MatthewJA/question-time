"""Cleans Hansard data.

- Removes duplicates.
- Strips town names that are part of other words.
- Strips town names preceded by Ms or Mr.
"""

import re

from hansard import Hansard, db

words = re.compile(r'\w+')

for row in Hansard.query:
    texts = row.text.encode('ascii', 'ignore').split(b' | ')
    print(row.location, 'mentioned', len(texts), 'times')
    seen = set()
    to_remove = []
    for i, text in enumerate(texts):
        # Remove duplicates.
        if text in seen:
            to_remove.append(i)
            continue

        seen.add(text)

        # Remove component words.
        removed = False
        word_set = set(words.findall(text.lower().decode('ascii')))
        for part_loc in row.location.split():
            if part_loc not in word_set:
                to_remove.append(i)
                removed = True
                break

        if removed:
            continue

    to_remove.reverse()
    for i in to_remove:
        texts.pop(i)

    print('->', len(texts))

    row.text = b' | '.join(texts)
    row.hits = len(texts)
db.commit()
