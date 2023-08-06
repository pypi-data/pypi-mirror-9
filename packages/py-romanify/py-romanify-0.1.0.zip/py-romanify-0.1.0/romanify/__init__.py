
ROMANS = dict(
I=1,
V=5,
X=10,
L=50,
C=100,
D=500,
M=1000)

ARABIC = dict((item, key) for key, item in ROMANS.items())

def arabic2romans(number):
    def grammar(number, low, mid, high):
        if number == 9:
            return ARABIC[low] + ARABIC[high]
        elif number == 8:
            return ARABIC[mid] + ARABIC[low] * 3
        elif number == 7:
            return ARABIC[mid] + ARABIC[low] * 2
        elif number == 6:
            return ARABIC[mid] + ARABIC[low]
        elif number == 5:
            return ARABIC[mid]
        elif number == 4:
            return ARABIC[low] + ARABIC[mid]
        elif number == 3:
            return ARABIC[low] * 3
        elif number == 2:
            return ARABIC[low] * 2
        elif number == 1:
            return ARABIC[low]
        return ""

    roman = ARABIC[1000] * (number / 1000)
    number %= 1000
    roman += grammar((number / 100), 100, 500, 1000)
    number %= 100
    roman += grammar((number / 10), 10, 50, 100)
    number %= 10
    roman += grammar(number, 1, 5, 10)
    return roman



def romans2arabic(number):
    def grammar(c, iterator, low, mid, high):
        number = 0
        try:
            if c is None:
                raise StopIteration

            if c == mid:
                number += ROMANS[mid]
                c = iterator.next()
                if c == low:
                    number += ROMANS[low]
                    c = iterator.next()
                    if c == low:
                        number += ROMANS[low]
                        c = iterator.next()
                        if c == low:
                            number += ROMANS[low]
                            c = iterator.next()
            elif c == low:
                number += ROMANS[low]
                c = iterator.next()
                if c == high:
                    number += ROMANS[high] - 2 * ROMANS[low]
                    c = iterator.next()
                elif c == mid:
                    number += ROMANS[mid] - 2 * ROMANS[low]
                    c = iterator.next()
                elif c == low:
                    number += ROMANS[low]
                    c = iterator.next()
                    if c == low:
                        number += ROMANS[low]
                        c = iterator.next()
        except StopIteration:
            return None, number
        else:
            return c, number

    iterator = iter(number)
    arabic = 0
    c = iterator.next()
    try:
        while c == 'M':
            arabic += ROMANS[c]
            c = iterator.next()
    except StopIteration:
        pass
    else:
        c, partial_number = grammar(c, iterator, 'C', 'D', 'M')
        arabic += partial_number
        if c is not None:
            c, partial_number = grammar(c, iterator, 'X', 'L', 'C')
            arabic += partial_number
            if c is not None:
                c, partial_number = grammar(c, iterator, 'I', 'V', 'X')
                arabic += partial_number
                if c is not None:
                    raise ValueError("Not a proper roman numeral")

    return arabic

