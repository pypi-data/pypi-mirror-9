if __name__ == "__main__":
    import os
    import functools
    a = os.path.join('a',
                     'b')

    def deco(func):
        @functools.wraps(func)
        def wrapper(*args):
            return func(*args)
        return wrapper

    @deco
    @deco
    @deco
    def foo(*args):
        return os.path.join(*args)

    foo(
        'a',
        'b'
    )

    None(
        'a',
        'b'
    ) # doh!

