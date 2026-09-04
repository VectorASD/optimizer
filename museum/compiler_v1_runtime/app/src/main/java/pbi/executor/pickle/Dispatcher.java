package pbi.executor.pickle;

import java.io.IOException;
import pbi.executor.exceptions.PicklingError;
import pbi.executor.types.Base;

public abstract class Dispatcher {
  // есть везде и всегда
  public static final byte PROTO            = (byte) 0x80; // identify pickle protocol
  public static final byte STOP             = '.';         // every pickle ends with STOP

  // есть только там, где меморизация
  public static final byte BINGET           = 'h';         // push item from memo on stack; index is 1-byte arg
  public static final byte LONG_BINGET      = 'j';         // push item from memo on stack; index is 4-byte arg
  public static final byte BINPUT           = 'q';         // store stack top in memo; index is 1-byte arg
  public static final byte LONG_BINPUT      = 'r';         //  store stack top in memo; index is 4-byte arg
  public static final byte MEMOIZE          = (byte) 0x94; // store top of the stack in memo

  // пакетная штука
  public static final byte FRAME            = (byte) 0x95; // indicate the beginning of a new frame

  // None
  public static final byte NONE             = 'N';         // push None

  // bool
  public static final byte NEWTRUE          = (byte) 0x88; // push True
  public static final byte NEWFALSE         = (byte) 0x89; // push False

  // int
  public static final byte BININT1          = 'K';         // push 1-byte unsigned int
  public static final byte BININT2          = 'M';         // push 2-byte unsigned int
  public static final byte BININT           = 'J';         // push four-byte signed int
  public static final byte LONG1            = (byte) 0x8a; // push long from < 256 bytes
  public static final byte LONG4            = (byte) 0x8b; // push really big long

  // float
  public static final byte BINFLOAT         = 'G';         // push float; arg is 8-byte float encoding

  // bytes
  public static final byte BINBYTES         = 'B';         // push bytes; counted binary string argument
  public static final byte SHORT_BINBYTES   = 'C';         // push bytes; counted binary string argument < 256 bytes
  public static final byte BINBYTES8        = (byte) 0x8e; // push very long bytes string

  // str
  public static final byte BINUNICODE       = 'X';         // push Unicode string; counted UTF-8 string argument
  public static final byte SHORT_BINUNICODE = (byte) 0x8c; // push short string; UTF-8 length < 256 bytes
  public static final byte BINUNICODE8      = (byte) 0x8d; // push very long string

  // tuple | reduce
  public static final byte POP              = '0';         // discard topmost stack item
  // tuple | list | dict | set | frozenset
  public static final byte MARK             = '(';         // push special markobject on stack
  // tuple | frozenset
  public static final byte POP_MARK         = '1';         // discard stack top through topmost markobject

  // tuple
  public static final byte EMPTY_TUPLE      = ')';         // push empty tuple
  public static final byte TUPLE1           = (byte) 0x85; // build 1-tuple from stack top
  public static final byte TUPLE2           = (byte) 0x86; // build 2-tuple from two topmost stack items
  public static final byte TUPLE3           = (byte) 0x87; // build 3-tuple from three topmost stack items
  public static final byte TUPLE            = 't';         // build tuple from topmost stack items

  public static final byte[] tuplesize2code = {EMPTY_TUPLE, TUPLE1, TUPLE2, TUPLE3};

  // list
  public static final byte EMPTY_LIST       = ']';         // push empty list
  public static final byte APPEND           = 'a';         // append stack top to list below it
  public static final byte APPENDS          = 'e';         // extend list on stack by topmost stack slice

  // dict
  public static final byte EMPTY_DICT       = '}';         // push empty dict
  public static final byte SETITEM          = 's';         // add key+value pair to dict
  public static final byte SETITEMS         = 'u';         // modify dict by adding topmost key+value pairs

  // global | build | reduce
  public static final byte BUILD            = 'b';         // call __setstate__ or __dict__.update()
  public static final byte GLOBAL           = 'c';         // push self.find_class(modname, name); 2 string args
  public static final byte STACK_GLOBAL     = (byte) 0x93; // same as GLOBAL but using names on the stacks
  public static final byte REDUCE           = 'R';         // apply callable to argtuple, both on stack

  // set
  public static final byte EMPTY_SET        = (byte) 0x8f; // push empty set on the stack
  public static final byte ADDITEMS         = (byte) 0x90; // modify set by adding topmost stack items

  public abstract void pickle(Pickler pickler, Base obj) throws IOException, PicklingError;
}
