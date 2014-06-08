import zook
import decimal


def set_values(ss, attr, values):
    for i, v in enumerate(values):
        setattr(ss[i], attr, v)

def test(cost, provides, bids, asks):
    print('-' * 100)
    session = zook.Session()
    session.debug = True
    session.start_from_phase = 2

    ss = []
    index = 1
    while index <= 6:
        s = zook.Subject(session)
        s.name = str(index)
        ss.append(s)
        index += 1

    for s in ss:
        s.set_state('waiting')


    session.start()
    session.period.cost = decimal.Decimal(str(cost))
    group = list(session.period.groups.values())[0]

    set_values(ss, 'my_provide', provides)
    set_values(ss, 'my_bid', bids)
    set_values(ss, 'my_ask', asks)

    while session.period.key < 1:
        if group.is_finished_period:
            session.phase.next_period()
        else:
            group.next_stage()
        for s in ss:
            s.set_state('waiting')

print('\nTest 1')
test(
    3,
    (0.5, 0.5, 0.5, 0.5, 0.5, 0),
    (0.4, 0.5, 0.6, 0.5, 0.6, 0.7),
    (0.4, 0.5, 0.6, 0.3, 0.4, 0.3)
    )

print('\nTest 2')
test(
    3,
    (0.5, 0.5, 0.5, 0.5, 1, 0),
    (0.4, 0.5, 0.6, 0.5, 0.3, 0.7),
    (0.4, 0.5, 0.6, 0.6, 0.5, 0.3)
    )

print('\nTest 3')
test(
    3,
    (0.5, 0.5, 0.5, 0, 1, 0),
    (0.4, 0.5, 0.6, 0.5, 0.3, 0.6),
    (0.4, 0.5, 0.7, 0.6, 0.5, 0.3)
    )

print('\nTest 4')
test(
    3,
    (0.5, 1.5, 1, 0, 1, 0),
    (0.4, 0.5, 0.6, 0.3, 0.6, 0.7),
    (0.2, 0.5, 0.6, 0.6, 0.5, 0.3)
    )

print('\nTest 5')
test(
    3,
    (0.5, 0, 0, 0, 0, 0),
    (0.3, 0.5, 0.6, 0.5, 0.6, 0.8),
    (0.4, 0.5, 0.7, 0.6, 0.6, 0.3)
    )

print('\nTest 11')
test(
    5.5,
    (0.5, 0.5, 0.5, 0.5, 0.5, 0),
    (0.7, 1, 1.2, 0.9, 0.9, 1.1),
    (0.7, 0.9, 1.1, 0.5, 0.8, 1)
    )

print('\nTest 12')
test(
    5.5,
    (0.5, 0.5, 0.5, 0.5, 1, 0),
    (0.6, 1, 1.2, 0.9, 0.7, 1.1),
    (0.7, 1, 1.2, 0.6, 0.8, 1.1)
    )

print('\nTest 13')
test(
    5.5,
    (0.5, 0.5, 0.5, 0, 1, 0),
    (0.5, 1, 1.2, 0.9, 0.7, 1.1),
    (0.7, 1, 1.2, 0.6, 0.9, 1.1),
    )

print('\nTest 14')
test(
    5.5,
    (0.5, 1.5, 1, 0, 1, 0),
    (0.6, 1, 1.2, 0.9, 0.8, 1.1),
    (0.7, 0.9, 1.2, 0.6, 0.8, 1),
    )

print('\nTest 15')
test(
    5.5,
    (0.5, 0, 0, 0, 0, 0),
    (0.3, 1.1, 1.3, 1, 0.9, 1.2),
    (0.8, 1, 1.2, 0.6, 0.9, 1.1)
    )