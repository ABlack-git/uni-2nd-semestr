from typing import Dict

DELIMITER: str = "_"
valueToNumber: Dict[int, str] = {14: "ACE",
                                 13: "KING",
                                 12: "OBER",
                                 11: "UNTER",
                                 10: "TEN",
                                 9: "NINE",
                                 8: "EIGHT",
                                 7: "SEVEN",
                                 6: "SIX",
                                 5: "FIVE",
                                 4: "FOUR",
                                 3: "THREE",
                                 2: "TWO"}

strToValue: Dict[str, int] = {"ACE": 14,
                              "KING": 13,
                              "OBER": 12,
                              "UNTER": 11,
                              "TEN": 10,
                              "NINE": 9,
                              "EIGHT": 8,
                              "SEVEN": 7,
                              "SIX": 6,
                              "FIVE": 5,
                              "FOUR": 4,
                              "THREE": 3,
                              "TWO": 2
                              }
