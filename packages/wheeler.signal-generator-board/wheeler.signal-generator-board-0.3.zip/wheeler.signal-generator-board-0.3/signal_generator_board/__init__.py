from path_helpers import path


def package_path():
    return path(__file__).parent


def get_sketch_directory():
    '''
    Return directory containing the `signal_generator_board` Arduino sketch.
    '''
    return package_path().joinpath('Arduino', 'signal_generator_board')


def get_includes():
    '''
    Return directories containing the `signal_generator_board` Arduino header
    files.

    Modules that need to compile against `signal_generator_board` should use this
    function to locate the appropriate include directories.

    Notes
    =====

    For example:

        import signal_generator_board
        ...
        print ' '.join(['-I%s' % i for i in signal_generator_board.get_includes()])
        ...

    '''
    import base_node
    return [get_sketch_directory()] + base_node.get_includes()


def get_sources():
    '''
    Return `signal_generator_board` Arduino source file paths.

    Modules that need to compile against `signal_generator_board` should use this
    function to locate the appropriate source files to compile.

    Notes
    =====

    For example:

        import signal_generator_board
        ...
        print ' '.join(signal_generator_board.get_sources())
        ...

    '''
    sources = []
    for p in get_includes():
        sources += path(p).files('*.c*')
    return sources


def get_firmwares():
    '''
    Return `signal_generator_board` compiled Arduino hex file paths.

    This function may be used to locate firmware binaries that are available
    for flashing to [Arduino Uno][1] boards.

    [1]: http://arduino.cc/en/Main/arduinoBoardUno
    '''
    return [f.abspath() for f in
            package_path().joinpath('firmware').walkfiles('*.hex')]
