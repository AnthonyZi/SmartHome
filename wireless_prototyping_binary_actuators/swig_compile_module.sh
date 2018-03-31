swig -python $1.i
gcc -fpic -c $1.c $1_wrap.c -I/usr/include/python3.5
ld -shared $1.o $1_wrap.o -o _$1.so
