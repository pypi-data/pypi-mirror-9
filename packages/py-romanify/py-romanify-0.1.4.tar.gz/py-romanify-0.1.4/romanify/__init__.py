#!/usr/bin/env python
"""
Roman/arabic number convertor.

    * arabic2roman(number)
    * roman2arabic(number)
"""

ROMANS = dict(
    I=1,
    V=5,
    X=10,
    L=50,
    C=100,
    D=500,
    M=1000)

ARABIC = dict((item, key) for key, item in ROMANS.items())

def arabic2roman(number):
    """
    Convert arabic number to roman.
    """
    def grammar(number, low, mid, high):
        """
        Inner function for common convert.
        """
        ret = ""
        if number == 9:
            ret = ARABIC[low] + ARABIC[high]
        elif number == 8:
            ret = ARABIC[mid] + ARABIC[low] * 3
        elif number == 7:
            ret = ARABIC[mid] + ARABIC[low] * 2
        elif number == 6:
            ret = ARABIC[mid] + ARABIC[low]
        elif number == 5:
            ret = ARABIC[mid]
        elif number == 4:
            ret = ARABIC[low] + ARABIC[mid]
        elif number == 3:
            ret = ARABIC[low] * 3
        elif number == 2:
            ret = ARABIC[low] * 2
        elif number == 1:
            ret = ARABIC[low]
        return ret

    number = int(number)
    roman = ARABIC[1000] * int(number / 1000)
    number %= 1000
    roman += grammar(int(number / 100), 100, 500, 1000)
    number %= 100
    roman += grammar(int(number / 10), 10, 50, 100)
    number %= 10
    roman += grammar(number, 1, 5, 10)
    return roman


def roman2arabic(number):
    """
    Convert roman number to arabic.
    """
    def grammar(last_char, iterator, low, mid, high):
        """
        Inner function for common convert.
        """
        number = 0
        try:
            if last_char == mid:
                number = ROMANS[mid]
                last_char = next(iterator)
                if last_char == low:
                    number += ROMANS[low]
                    last_char = next(iterator)
                    if last_char == low:
                        number += ROMANS[low]
                        last_char = next(iterator)
                        if last_char == low:
                            number += ROMANS[low]
                            last_char = next(iterator)
            elif last_char == low:
                number = ROMANS[low]
                last_char = next(iterator)
                if last_char == high:
                    number += ROMANS[high] - 2 * ROMANS[low]
                    last_char = next(iterator)
                elif last_char == mid:
                    number += ROMANS[mid] - 2 * ROMANS[low]
                    last_char = next(iterator)
                elif last_char == low:
                    number += ROMANS[low]
                    last_char = next(iterator)
                    if last_char == low:
                        number += ROMANS[low]
                        last_char = next(iterator)
        except StopIteration:
            last_char = None

        return last_char, number

    iterator = iter(number.upper())
    arabic = 0
    try:
        last_char = next(iterator)
        while last_char == 'M':
            arabic += ROMANS[last_char]
            last_char = next(iterator)
    except StopIteration:
        return arabic

    last_char, partial_number = grammar(last_char, iterator, 'C', 'D', 'M')
    arabic += partial_number
    if last_char is not None:
        last_char, partial_number = grammar(last_char, iterator, 'X', 'L', 'C')
        arabic += partial_number
        if last_char is not None:
            last_char, partial_number = grammar(last_char, iterator, 'I', 'V', 'X')
            arabic += partial_number
            if last_char is not None:
                raise ValueError("Not a proper roman numeral")

    return arabic

