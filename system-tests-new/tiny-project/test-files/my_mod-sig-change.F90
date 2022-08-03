
MODULE my_mod

CONTAINS

SUBROUTINE mod_func ()

    INTEGER :: foo
    PRINT *, foo

END SUBROUTINE mod_func

SUBROUTINE mod_func2 ()

    INTEGER :: bar = 2
    PRINT *, bar

END SUBROUTINE mod_func2

END MODULE my_mod
