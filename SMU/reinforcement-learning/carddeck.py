# in this file you can find a model for card, card deck and player hand

from enum import Enum
import numpy as np


class Suit(Enum):
    """ Enum that declares the suit of cards. """
    # for Czechs: krizova
    CLUB = 1
    # karova
    DIAMOND = 2
    # srdcova
    HEART = 3
    # pikova
    SPADES = 4


class Rank(Enum):
    """ Enum that shows the rank of a card. """
    # eso
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    # spodek
    JACK = 11  # 10
    QUEEN = 12  # 10
    KING = 13  # 10


class Card:
    """ Card object. Each card has suit and rank. For example spades ten. """

    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def value(self) -> int:
        """
        Gets value of the card. Ace is counted 1, face cards 10.

        :rtype int
        :returns Value of the card in blackjack. Ace is 1, face cards 10, others by their rank.
        """
        if self.rank.value > 10:
            return 10
        return self.rank.value

    def __repr__(self) -> str:
        return self.suit.name + ' ' + self.rank.name


class CardDeck:
    """
    A standard card deck with 52 cards.
    There are all possible suit and rank combinations.
    """

    def __init__(self):
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))

    def shuffle(self, np_random=np.random) -> None:
        """ Shuffles the deck. """
        np_random.shuffle(self.cards)

    def draw_card(self) -> Card:
        """
        Removes a single card from the deck and returns it.
        :return: The card located on the top of the deck.
        :rtype: Card
        """
        return self.cards.pop()


class BlackjackHand:
    """
    Player's hand. Follows the blackjack setting.
    """

    def __init__(self):
        self.cards = []

    def draw_card(self, deck: CardDeck) -> None:
        """
        Takes one card from the deck and puts it into the player's hand.
        :param deck: The deck to draw from
        """
        self.cards.append(deck.draw_card())

    def value(self) -> int:
        """
        Gets the value of the hand. Value is a sum of values of all cards
        in the deck. If there is an ace, it can be counted 1 or 11. 11 is
        used only if the final sum does not exceed 21.
        :return: Value of the hand.
        :rtype: int
        """
        ace = False
        hand_value: int = 0
        for card in self.cards:
            if card.rank is Rank.ACE:
                ace = True
            hand_value += card.value()

        if ace and hand_value + 10 <= 21:
            hand_value = hand_value + 10
        return hand_value

    def is_bust(self) -> int:
        """
        Hand is bust if the value is more than 21. This is equivalent to
        loosing a blackjack game.

        :return: True if the value is more than 21, False otherwise.
        :rtype: int
        """
        return self.value() > 21

    def __str__(self):
        return str(self.cards) + " (" + str(self.value()) + ")"
