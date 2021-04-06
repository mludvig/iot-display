from lib.split_image import get_chunks

def test_get_chunks():
    lst = list(range(20))
    chunks = list(get_chunks(lst, 3))
    assert len(chunks) == 7
    assert chunks[0] == [ 0, 1, 2 ]
    assert chunks[-1] == [ 18, 19 ]

