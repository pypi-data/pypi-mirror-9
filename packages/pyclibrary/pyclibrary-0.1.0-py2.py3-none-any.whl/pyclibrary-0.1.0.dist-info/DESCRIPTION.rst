PyCLibrary includes 1) a pure-python C parser and
2) an automation library that uses C header file definitions to simplify the
use of c bindings. The C parser currently processes all macros, typedefs,
structs, unions, enums, function prototypes, and global variable declarations,
and can evaluate typedefs down to their fundamental C types +
pointers/arrays/function signatures. Pyclibrary can automatically build c
structs/unions and perform type conversions when calling functions via
cdll/windll.

