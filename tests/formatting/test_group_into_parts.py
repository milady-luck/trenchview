from trenchview.formatting import group_into_parts


def test_even_break():
    max_len = 10
    s = ("a" * max_len) + "\n\n" + ("b" * max_len)

    assert group_into_parts(s, max_len) == ["a" * max_len, "b" * max_len]


def test_uneven_break():
    max_len = 10
    s = ("a" * 4) + "\n\n" + ("b" * 5) + "\n\n" + ("c" * 9)

    assert group_into_parts(s, max_len) == [("a" * 4), ("b" * 5), ("c" * 9)]


def test_even_combine():
    max_len = 10
    s = ("a" * 4) + "\n\n" + ("b" * 3)

    assert group_into_parts(s, max_len) == [s]


def test_split_single_group():
    max_len = 10
    s = ("a" * 8) + "\n\n" + ("b" * 11)

    assert group_into_parts(s, max_len) == [("a" * 8), ("b" * 10), "b"]
