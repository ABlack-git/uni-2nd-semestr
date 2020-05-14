from enum import IntEnum


class Card(IntEnum):
    UNTER_OF_ACORNS, UNTER_OF_LEAVES, \
    OBER_OF_ACORNS, OBER_OF_LEAVES, \
    KING_OF_ACORNS, KING_OF_LEAVES, \
    ACE_OF_ACORNS, ACE_OF_LEAVES = range(8)
