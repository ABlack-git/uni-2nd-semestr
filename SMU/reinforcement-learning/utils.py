from carddeck import BlackjackHand, Rank


def hand_has_active_ace(hand: BlackjackHand) -> bool:
    has_ace = False
    value = 0
    for card in hand.cards:
        if card.rank is Rank.ACE:
            has_ace = True
        value += card.value()
    return has_ace and value + 10 <= 21
