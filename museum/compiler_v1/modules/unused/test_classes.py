ACCESS_NOFLAGS      =     0x0 # аналогичен ACCESS_PRIVATE
ACCESS_PUBLIC       =     0x1 # class | field | method
ACCESS_PRIVATE      =     0x2 # class | field | method
ACCESS_PROTECTED    =     0x4 # class | field | method
ACCESS_STATIC       =     0x8 # class | field | method
ACCESS_FINAL        =    0x10 # class | field | method
# ACCESS_SUPER      =    0x20 # class |  ---  |  ----
ACCESS_SYNCHRONIZED =    0x20 #  ---  |  ---  | method
ACCESS_VOLATILE     =    0x40 #  ---  | field |  ----
ACCESS_BRIDGE       =    0x40 #  ---  |  ---  | method
ACCESS_TRANSIENT    =    0x80 #  ---  | field |  ----
ACCESS_VARARGS      =    0x80 #  ---  |  ---  | method
ACCESS_NATIVE       =   0x100 #  ---  |  ---  | method
ACCESS_INTERFACE    =   0x200 # class |  ---  |  ----
ACCESS_ABSTRACT     =   0x400 # class |  ---  | method
ACCESS_STRICT       =   0x800 #  ---  |  ---  | method
ACCESS_SYNTHETIC    =  0x1000 # class | field | method
ACCESS_ANNOTATION   =  0x2000 # class |  ---  |  ----
ACCESS_ENUM         =  0x4000 # class | field |  ----
ACCESS_UNKNOWN      =  0x8000 #  ---  |  ---  |  ----
ACCESS_CONSTRUCTOR  = 0x10000 #  ---  |  ---  | method (только и всегда <clinit> и <init>)
ACCESS_DECL_SYNC    = 0x20000 #  ---  |  ---  | method (работает также, как и обычный synchronized)

IS_STATIC_FIELD   = 0 # static or constructor (<clinit>)
IS_INSTANCE_FIELD = 1
IS_DIRECT_METHOD  = 2 # static or constructor (<init>)
IS_VIRTUAL_METHOD = 3





"""
Искусственно внедрил кодированнык значения (encoded values) во Wrap-класс:

.field static private check1:B = 10
.field static private check2:S = 3456
.field static private check3:I = 0x7f000000
.field static private check4:J = 0x7f00000012345678L
.field static private check5:F = 1e16f
.field static private check6:D = 1e250d
.field static private check7:Z = true
.field static private check8:C = 'у'
.field static private check9:Ljava/lang/String; = "Это строка! 👍🔨"
"""

wrap_class = ('Lpbi/secured/Wrap;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 # (), "GreatSource.java", (), # всё равно будет Unknown Source пишет в traceBack, как если бы я просто оставил None здесь
 (), None, (),
 (

  (IS_STATIC_FIELD, 'check1:B', ACCESS_STATIC | ACCESS_PRIVATE, (0, '0xa'), (), None, {}),
  (IS_STATIC_FIELD, 'check2:S', ACCESS_STATIC | ACCESS_PRIVATE, (2, '0xd80'), (), None, {}),
  (IS_STATIC_FIELD, 'check3:I', ACCESS_STATIC | ACCESS_PRIVATE, (4, '0x7f000000'), (), None, {}),
  (IS_STATIC_FIELD, 'check4:J', ACCESS_STATIC | ACCESS_PRIVATE, (6, '0x7f00000012345678'), (), None, {}),
  (IS_STATIC_FIELD, 'check5:F', ACCESS_STATIC | ACCESS_PRIVATE, (16, 1e16), (), None, {}),
  (IS_STATIC_FIELD, 'check6:D', ACCESS_STATIC | ACCESS_PRIVATE, (17, 1e250), (), None, {}),
  (IS_STATIC_FIELD, 'check7:Z', ACCESS_STATIC | ACCESS_PRIVATE, (31, True), (), None, {}),
  (IS_STATIC_FIELD, 'check8:C', ACCESS_STATIC | ACCESS_PRIVATE, (3, '0x443'), (), None, {}),
  (IS_STATIC_FIELD, 'check9:Ljava/lang/String;', ACCESS_STATIC | ACCESS_PRIVATE, (23, '"Это строка! 👍🔨"'), (), None, {}),

  (IS_INSTANCE_FIELD, 'data:J', ACCESS_PRIVATE, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'mul:J', ACCESS_PRIVATE, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'orig:J', ACCESS_PRIVATE, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'shift:J', ACCESS_PRIVATE, None, (), None, {}),
  (IS_DIRECT_METHOD, '<init>()V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (3, 1, 3, 9,
    ((112, 'Ljava/lang/Object;-><init>()V', (2,)),
     (22, 0, 0),
     (112, 'Lpbi/secured/Wrap;->first(J)V', (2, 0, 1)),
     (14,)
    ), ()), {}),
  (IS_DIRECT_METHOD, '<init>(J)V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (4, 3, 3, 7,
    ((112, 'Ljava/lang/Object;-><init>()V', (1,)),
     (112, 'Lpbi/secured/Wrap;->first(J)V', (1, 2, 3)),
     (14,)
    ), ()), {}),
  (IS_DIRECT_METHOD, 'first(J)V', ACCESS_PRIVATE, None, (),
   (6, 3, 3, 26,
    ((18, 0, 3),
     (19, 1, 32),
     (113, 'Lpbi/secured/Wrap;->randint(II)I', (0, 1)),
     (10, 0),
     (129, 0, 0),
     (90, (0, 3), 'Lpbi/secured/Wrap;->mul:J'),
     (19, 0, 10),
     (20, 1, 1000000),
     (113, 'Lpbi/secured/Wrap;->randint(II)I', (0, 1)),
     (10, 0),
     (129, 0, 0),
     (90, (0, 3), 'Lpbi/secured/Wrap;->shift:J'),
     (110, 'Lpbi/secured/Wrap;->set(J)V', (3, 4, 5)),
     (14,)
    ), ()), {}),
  (IS_DIRECT_METHOD, 'randint(II)I', ACCESS_STATIC | ACCESS_PRIVATE, None, (),
   (6, 2, 0, 13,
    ((113, 'Ljava/lang/Math;->random()D', ()),
     (11, 0),
     (145, 2, 5, 4),
     (216, (2, 2), 1),
     (131, 2, 2),
     (205, 0, 2),
     (138, 0, 0),
     (176, 0, 4),
     (15, 0)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'dec(J)V', ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Ljava/lang/Exception;'),)),), 'system'),),
   (6, 3, 3, 9,
    ((110, 'Lpbi/secured/Wrap;->secured_get()J', (3,)),
     (11, 0),
     (188, 0, 4),
     (110, 'Lpbi/secured/Wrap;->secured_set(J)V', (3, 0, 1)),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'get()J', ACCESS_PUBLIC, None, (),
   (5, 1, 0, 9,
    ((83, (0, 4), 'Lpbi/secured/Wrap;->data:J'),
     (83, (2, 4), 'Lpbi/secured/Wrap;->shift:J'),
     (188, 0, 2),
     (83, (2, 4), 'Lpbi/secured/Wrap;->mul:J'),
     (190, 0, 2),
     (16, 0)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'inc(J)V', ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Ljava/lang/Exception;'),)),), 'system'),),
   (6, 3, 3, 9,
    ((110, 'Lpbi/secured/Wrap;->secured_get()J', (3,)),
     (11, 0),
     (187, 0, 4),
     (110, 'Lpbi/secured/Wrap;->secured_set(J)V', (3, 0, 1)),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'secured_get()J', ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Ljava/lang/Exception;'),)),), 'system'),),
   (5, 1, 2, 19,
    ((110, 'Lpbi/secured/Wrap;->get()J', (4,)),
     (11, 0),
     (83, (2, 4), 'Lpbi/secured/Wrap;->orig:J'),
     (49, 2, 0, 2),
     (56, 2, 18, ':cond_12'),
     (34, 0, 'Ljava/lang/Exception;'),
     (26, 1, 'Нука живо удалил GG и не лезь в ОЗУ!!! XD'),
     (112, 'Ljava/lang/Exception;-><init>(Ljava/lang/String;)V', (0, 1)),
     (39, 0),
     (16, 0)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'secured_set(J)V', ACCESS_PUBLIC, None, (),
   (8, 3, 0, 19,
    ((83, (0, 5), 'Lpbi/secured/Wrap;->mul:J'),
     (189, 0, 6),
     (83, (2, 5), 'Lpbi/secured/Wrap;->mul:J'),
     (158, 2, 0, 2),
     (49, 2, 2, 6),
     (57, 2, 18, ':cond_12'),
     (83, (2, 5), 'Lpbi/secured/Wrap;->shift:J'),
     (187, 0, 2),
     (90, (0, 5), 'Lpbi/secured/Wrap;->data:J'),
     (90, (6, 5), 'Lpbi/secured/Wrap;->orig:J'),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'set(J)V', ACCESS_PUBLIC, None, (),
   (8, 3, 0, 11,
    ((83, (0, 5), 'Lpbi/secured/Wrap;->mul:J'),
     (189, 0, 6),
     (83, (2, 5), 'Lpbi/secured/Wrap;->shift:J'),
     (187, 0, 2),
     (90, (0, 5), 'Lpbi/secured/Wrap;->data:J'),
     (90, (6, 5), 'Lpbi/secured/Wrap;->orig:J'),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'yeah(J)Z', ACCESS_PUBLIC, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Ljava/lang/Exception;'),)),), 'system'),),
   (6, 3, 1, 12,
    ((110, 'Lpbi/secured/Wrap;->secured_get()J', (3,)),
     (11, 0),
     (49, 0, 0, 4),
     (58, 0, 10, ':cond_a'),
     (18, 0, 1),
     (15, 0),
     (18, 0, 0),
     (40, 9, ':goto_9')
    ), ()), {})
  )
)



arr_class = ('Lpbi/secured/Arr;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 (), None, (),
 ((IS_INSTANCE_FIELD, 'data:[Lpbi/secured/Wrap;', ACCESS_PRIVATE, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'size:Lpbi/secured/Wrap;', ACCESS_PRIVATE, None, (), None, {}),
  (IS_DIRECT_METHOD, '<init>(Lpbi/secured/Root;I)V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (7, 3, 3, 31,
    ((112, 'Ljava/lang/Object;-><init>()V', (4,)),
     (34, 0, 'Lpbi/secured/Wrap;'),
     (129, 2, 6),
     (112, 'Lpbi/secured/Wrap;-><init>(J)V', (0, 2, 3)),
     (91, (0, 4), 'Lpbi/secured/Arr;->size:Lpbi/secured/Wrap;'),
     (35, (0, 6), '[Lpbi/secured/Wrap;'),
     (91, (0, 4), 'Lpbi/secured/Arr;->data:[Lpbi/secured/Wrap;'),
     (18, 0, 0),
     (52, (0, 6), 19, ':cond_13'),
     (14,),
     (84, (1, 4), 'Lpbi/secured/Arr;->data:[Lpbi/secured/Wrap;'),
     (34, 2, 'Lpbi/secured/Wrap;'),
     (112, 'Lpbi/secured/Wrap;-><init>()V', (2,)),
     (77, 2, 1, 0),
     (216, (0, 0), 1),
     (40, 16, ':goto_10')
    ), ()), {}),
  (IS_DIRECT_METHOD, 'pack()Ljava/lang/String;', ACCESS_PRIVATE, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Ljava/lang/Exception;'),)),), 'system'),),
   (7, 1, 2, 36,
    ((84, (0, 6), 'Lpbi/secured/Arr;->size:Lpbi/secured/Wrap;'),
     (110, 'Lpbi/secured/Wrap;->secured_get()J', (0,)),
     (11, 0),
     (132, 1, 0),
     (35, (2, 1), '[Ljava/lang/String;'),
     (18, 0, 0),
     (52, (0, 1), 19, ':cond_13'),
     (26, 0, ','),
     (113, 'Ljava/lang/String;->join(Ljava/lang/CharSequence;[Ljava/lang/CharSequence;)Ljava/lang/String;', (0, 2)),
     (12, 0),
     (17, 0),
     (84, (3, 6), 'Lpbi/secured/Arr;->data:[Lpbi/secured/Wrap;'),
     (70, 3, 3, 0),
     (110, 'Lpbi/secured/Wrap;->secured_get()J', (3,)),
     (11, 4),
     (113, 'Ljava/lang/Long;->toString(J)Ljava/lang/String;', (4, 5)),
     (12, 3),
     (77, 3, 2, 0),
     (216, (0, 0), 1),
     (40, 10, ':goto_a')
    ), ()), {}),
  (IS_DIRECT_METHOD, 'print(Ljava/lang/String;)V', ACCESS_STATIC | ACCESS_PRIVATE, None, (),
   (1, 1, 1, 4,
    ((113, 'Lpbi/executor/Main;->print(Ljava/lang/Object;)V', (0,)),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'test()V', ACCESS_PUBLIC, None, (),
   (5, 1, 3, 88,
    ((34, 0, 'Ljava/lang/StringBuilder;'),
     (26, 1, 'size: '),
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (0, 1)),
     (84, (1, 4), 'Lpbi/secured/Arr;->size:Lpbi/secured/Wrap;'),
     (110, 'Lpbi/secured/Wrap;->get()J', (1,)),
     (11, 2),
     (110, 'Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;', (0, 2, 3)),
     (12, 0),
     (26, 1, ' '),
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (0, 1)),
     (12, 0),
     (84, (1, 4), 'Lpbi/secured/Arr;->size:Lpbi/secured/Wrap;'),
     (110, 'Lpbi/secured/Wrap;->secured_get()J', (1,)),
     (11, 2),
     (110, 'Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;', (0, 2, 3)),
     (12, 0),
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (0,)),
     (12, 0),
     (113, 'Lpbi/secured/Arr;->print(Ljava/lang/String;)V', (0,)),
     (34, 0, 'Ljava/lang/StringBuilder;'),
     (26, 1, 'data: '),
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (0, 1)),
     (112, 'Lpbi/secured/Arr;->pack()Ljava/lang/String;', (4,)),
     (12, 1),
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (0, 1)),
     (12, 0),
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (0,)),
     (12, 0),
     (113, 'Lpbi/secured/Arr;->print(Ljava/lang/String;)V', (0,)),
     (26, 0, '~~~~~~~~~~'),
     (113, 'Lpbi/secured/Arr;->print(Ljava/lang/String;)V', (0,)),
     (14,),
     (13, 0),
     (34, 1, 'Ljava/lang/StringBuilder;'),
     (26, 2, 'ERROR: '),
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (1, 2)),
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;', (1, 0)),
     (12, 0),
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (0,)),
     (12, 0),
     (113, 'Lpbi/secured/Arr;->print(Ljava/lang/String;)V', (0,)),
     (40, 67, ':goto_43')
    ), ((0, 67, (('Ljava/lang/Throwable;', 68),), None),)), {})
  )
)



class3_class = ('Lpbi/secured/Class3;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 (), None, (),
 ((IS_INSTANCE_FIELD, 'obj:Lpbi/secured/Arr;', ACCESS_PRIVATE, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'obj2:Lpbi/secured/Arr;', ACCESS_PRIVATE, None, (), None, {}),
  (IS_DIRECT_METHOD, '<init>(Lpbi/secured/Root;)V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (4, 2, 3, 21,
    ((112, 'Ljava/lang/Object;-><init>()V', (2,)),
     (34, 0, 'Lpbi/secured/Arr;'),
     (18, 1, 5),
     (112, 'Lpbi/secured/Arr;-><init>(Lpbi/secured/Root;I)V', (0, 3, 1)),
     (91, (0, 2), 'Lpbi/secured/Class3;->obj:Lpbi/secured/Arr;'),
     (34, 0, 'Lpbi/secured/Arr;'),
     (19, 1, 10),
     (112, 'Lpbi/secured/Arr;-><init>(Lpbi/secured/Root;I)V', (0, 3, 1)),
     (91, (0, 2), 'Lpbi/secured/Class3;->obj2:Lpbi/secured/Arr;'),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'test()V', ACCESS_PUBLIC, None, (),
   (2, 1, 1, 11,
    ((84, (0, 1), 'Lpbi/secured/Class3;->obj:Lpbi/secured/Arr;'),
     (110, 'Lpbi/secured/Arr;->test()V', (0,)),
     (84, (0, 1), 'Lpbi/secured/Class3;->obj2:Lpbi/secured/Arr;'),
     (110, 'Lpbi/secured/Arr;->test()V', (0,)),
     (14,)
    ), ()), {})
  )
)



class2_class = ('Lpbi/secured/Class2;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 (), None, (),
 ((IS_INSTANCE_FIELD, 'obj:Lpbi/secured/Class3;', ACCESS_PROTECTED, None, (), None, {}),
  (IS_DIRECT_METHOD, '<init>(Lpbi/secured/Root;)V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (3, 2, 2, 11,
    ((112, 'Ljava/lang/Object;-><init>()V', (1,)),
     (34, 0, 'Lpbi/secured/Class3;'),
     (112, 'Lpbi/secured/Class3;-><init>(Lpbi/secured/Root;)V', (0, 2)),
     (91, (0, 1), 'Lpbi/secured/Class2;->obj:Lpbi/secured/Class3;'),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'test()V', ACCESS_PUBLIC, None, (),
   (2, 1, 1, 6,
    ((84, (0, 1), 'Lpbi/secured/Class2;->obj:Lpbi/secured/Class3;'),
     (110, 'Lpbi/secured/Class3;->test()V', (0,)),
     (14,)
    ), ()), {})
  )
)



class1_class = ('Lpbi/secured/Class1;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 (), None, (),
 ((IS_STATIC_FIELD, 'HEX_DIGITS:[C', ACCESS_FINAL | ACCESS_STATIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'arr_00:[B', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'arr_01:[B', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'arr_1:[B', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'arr_2:[S', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'arr_4:[I', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'arr_8:[J', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'obj:Lpbi/secured/Class2;', ACCESS_PUBLIC, None, (), None, {}),
  (IS_DIRECT_METHOD, '<clinit>()V', ACCESS_CONSTRUCTOR | ACCESS_STATIC, None, (),
   (9, 0, 0, 292,
    ((18, 8, 3),
     (19, 7, 10),
     (18, 6, 5),
     (18, 5, 2),
     (18, 4, 1),
     (19, 0, 16),
     (35, (0, 0), '[C'),
     (38, 0, 272, ':array_110'),
     (105, 0, 'Lpbi/secured/Class1;->HEX_DIGITS:[C'),
     (35, (0, 8), '[B'),
     (79, 4, 0, 4),
     (79, 5, 0, 5),
     (105, 0, 'Lpbi/secured/Class1;->arr_00:[B'),
     (35, (0, 8), '[B'),
     (79, 4, 0, 4),
     (79, 5, 0, 5),
     (105, 0, 'Lpbi/secured/Class1;->arr_01:[B'),
     (19, 0, 13),
     (35, (0, 0), '[B'),
     (79, 4, 0, 4),
     (79, 5, 0, 5),
     (79, 6, 0, 8),
     (18, 1, 4),
     (79, 7, 0, 1),
     (19, 1, 126),
     (79, 1, 0, 6),
     (18, 1, 6),
     (19, 2, 127),
     (79, 2, 0, 1),
     (18, 1, 7),
     (18, 2, -1),
     (79, 2, 0, 1),
     (19, 1, 8),
     (18, 2, -2),
     (79, 2, 0, 1),
     (19, 1, 9),
     (18, 2, -5),
     (79, 2, 0, 1),
     (19, 1, -10),
     (79, 1, 0, 7),
     (19, 1, 11),
     (19, 2, -127),
     (79, 2, 0, 1),
     (19, 1, 12),
     (19, 2, -128),
     (79, 2, 0, 1),
     (105, 0, 'Lpbi/secured/Class1;->arr_1:[B'),
     (19, 0, 13),
     (35, (0, 0), '[S'),
     (81, 4, 0, 4),
     (81, 5, 0, 5),
     (81, 6, 0, 8),
     (18, 1, 4),
     (81, 7, 0, 1),
     (19, 1, 32766),
     (81, 1, 0, 6),
     (18, 1, 6),
     (19, 2, 32767),
     (81, 2, 0, 1),
     (18, 1, 7),
     (18, 2, -1),
     (81, 2, 0, 1),
     (19, 1, 8),
     (18, 2, -2),
     (81, 2, 0, 1),
     (19, 1, 9),
     (18, 2, -5),
     (81, 2, 0, 1),
     (19, 1, -10),
     (81, 1, 0, 7),
     (19, 1, 11),
     (19, 2, -32767),
     (81, 2, 0, 1),
     (19, 1, 12),
     (19, 2, -32768),
     (81, 2, 0, 1),
     (105, 0, 'Lpbi/secured/Class1;->arr_2:[S'),
     (19, 0, 13),
     (35, (0, 0), '[I'),
     (75, 4, 0, 4),
     (75, 5, 0, 5),
     (75, 6, 0, 8),
     (18, 1, 4),
     (75, 7, 0, 1),
     (20, 1, 2147483646),
     (75, 1, 0, 6),
     (18, 1, 6),
     (20, 2, 2147483647),
     (75, 2, 0, 1),
     (18, 1, 7),
     (18, 2, -1),
     (75, 2, 0, 1),
     (19, 1, 8),
     (18, 2, -2),
     (75, 2, 0, 1),
     (19, 1, 9),
     (18, 2, -5),
     (75, 2, 0, 1),
     (19, 1, -10),
     (75, 1, 0, 7),
     (19, 1, 11),
     (20, 2, -2147483647),
     (75, 2, 0, 1),
     (19, 1, 12),
     (21, 2, -2147483648),
     (75, 2, 0, 1),
     (105, 0, 'Lpbi/secured/Class1;->arr_4:[I'),
     (19, 0, 13),
     (35, (0, 0), '[J'),
     (22, 2, 1),
     (76, 2, 0, 4),
     (22, 2, 2),
     (76, 2, 0, 5),
     (22, 2, 5),
     (76, 2, 0, 8),
     (18, 1, 4),
     (22, 2, 10),
     (76, 2, 0, 1),
     (24, 2, 9223372036854775806, None),
     (76, 2, 0, 6),
     (18, 1, 6),
     (24, 2, 9223372036854775807, None),
     (76, 2, 0, 1),
     (18, 1, 7),
     (22, 2, -1),
     (76, 2, 0, 1),
     (19, 1, 8),
     (22, 2, -2),
     (76, 2, 0, 1),
     (19, 1, 9),
     (22, 2, -5),
     (76, 2, 0, 1),
     (22, 2, -10),
     (76, 2, 0, 7),
     (19, 1, 11),
     (24, 2, -9223372036854775807, -5e-324),
     (76, 2, 0, 1),
     (19, 1, 12),
     (25, 2, -9223372036854775808, -0.0),
     (76, 2, 0, 1),
     (105, 0, 'Lpbi/secured/Class1;->arr_8:[J'),
     (14,),
     (0, 0),
     (0, 3, 2, (48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70))
    ), ()), {}),
  (IS_DIRECT_METHOD, '<init>(Lpbi/secured/Root;)V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (3, 2, 2, 11,
    ((112, 'Ljava/lang/Object;-><init>()V', (1,)),
     (34, 0, 'Lpbi/secured/Class2;'),
     (112, 'Lpbi/secured/Class2;-><init>(Lpbi/secured/Root;)V', (0, 2)),
     (91, (0, 1), 'Lpbi/secured/Class1;->obj:Lpbi/secured/Class2;'),
     (14,)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'test()V', ACCESS_PUBLIC, None, (),
   (2, 1, 1, 6,
    ((84, (0, 1), 'Lpbi/secured/Class1;->obj:Lpbi/secured/Class2;'),
     (110, 'Lpbi/secured/Class2;->test()V', (0,)),
     (14,)
    ), ()), {})
  )
)



root_class = ('Lpbi/secured/Root;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 (), None, (),
 ((IS_INSTANCE_FIELD, 'obj:Lpbi/secured/Class1;', ACCESS_PUBLIC, None, (), None, {}),
  (IS_DIRECT_METHOD, '<init>()V', ACCESS_CONSTRUCTOR | ACCESS_PUBLIC, None, (),
   (2, 1, 2, 11,
    ((112, 'Ljava/lang/Object;-><init>()V', (1,)),
     (34, 0, 'Lpbi/secured/Class1;'),
     (112, 'Lpbi/secured/Class1;-><init>(Lpbi/secured/Root;)V', (0, 1)),
     (91, (0, 1), 'Lpbi/secured/Root;->obj:Lpbi/secured/Class1;'),
     (14,)
    ), ()), {}),
  (IS_DIRECT_METHOD, 'checker()V', ACCESS_STATIC | ACCESS_PUBLIC, None, (),
   (1, 0, 1, 9,
    ((34, 0, 'Lpbi/secured/Root;'),
     (112, 'Lpbi/secured/Root;-><init>()V', (0,)),
     (110, 'Lpbi/secured/Root;->test()V', (0,)),
     (14,)
    ), ()), {}),
  (IS_DIRECT_METHOD, 'sum(II)I', ACCESS_STATIC | ACCESS_PUBLIC, None, (),
   (3, 2, 0, 3,
    ((144, 0, 1, 2),
     # (144, 0, 0, 2), # для проверки, что вместо (a + b) будет действительно (a + 2b)
     (15, 0)
    ), ()), {}),
  (IS_VIRTUAL_METHOD, 'test()V', ACCESS_PUBLIC, None, (),
   (2, 1, 1, 6,
    ((84, (0, 1), 'Lpbi/secured/Root;->obj:Lpbi/secured/Class1;'),
     (110, 'Lpbi/secured/Class1;->test()V', (0,)),
     (14,)
    ), ()), {})
  )
)



# самая главная функция, части которой пойдут в целевой сборщик

processor = ('Lpbi/executor/Main;',
 ACCESS_PUBLIC,
 'Ljava/lang/Object;',
 (), None, (),
 ((IS_STATIC_FIELD, 'ESCAPE_JAVA:Lpbi/executor/unicode/CharSequenceTranslator;', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'ESCAPE_JAVA2:Lpbi/executor/unicode/CharSequenceTranslator;', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'Ellipsis:Lpbi/executor/types/EllipsisType;', ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'False:Lpbi/executor/types/pBoolean;', ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'FuI:Lpbi/executor/types/Base;', ACCESS_STATIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'FuT:Lpbi/executor/types/Base;', ACCESS_STATIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'JAVA_CTRL_CHARS_ESCAPE:Ljava/util/Map;', ACCESS_FINAL | ACCESS_STATIC | ACCESS_PUBLIC, None, (('Ldalvik/annotation/Signature;', ((28, 'value', ((23, '"Ljava/util/Map"'), (23, '"<"'), (23, '"Ljava/lang/CharSequence;"'), (23, '"Ljava/lang/CharSequence;"'), (23, '">;"'),)),), 'system'),), None, {}),
  (IS_STATIC_FIELD, 'None:Lpbi/executor/types/NoneType;', ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'NotImpl:Lpbi/executor/types/NotImplementedType;', ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'StopIteration:Lpbi/executor/exceptions/StopIteration;', ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'True:Lpbi/executor/types/pBoolean;', ACCESS_STATIC | ACCESS_PUBLIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'builtins_arr:[Lpbi/executor/types/Base;', ACCESS_STATIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'pool_arr:[Ljava/lang/String;', ACCESS_STATIC, None, (), None, {}),
  (IS_STATIC_FIELD, 'void_map:Ljava/util/Map;', ACCESS_STATIC | ACCESS_PRIVATE, None, (('Ldalvik/annotation/Signature;', ((28, 'value', ((23, '"Ljava/util/Map"'), (23, '"<"'), (23, '"Ljava/lang/String;"'), (23, '"Lpbi/executor/types/Base;"'), (23, '">;"'),)),), 'system'),), None, {}),
  (IS_INSTANCE_FIELD, 'builtins:[[I', ACCESS_NOFLAGS, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'consts:[Lpbi/executor/types/Base;', ACCESS_NOFLAGS, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'debug:Ljava/lang/Object;', ACCESS_NOFLAGS, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'defs:[Ljava/lang/Object;', ACCESS_NOFLAGS, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'globals:[Lpbi/executor/types/Base;', ACCESS_NOFLAGS, None, (), None, {}),
  (IS_INSTANCE_FIELD, 'last_method:I', ACCESS_NOFLAGS, None, (), None, {}),
  (IS_VIRTUAL_METHOD, 'method(Lpbi/executor/RegLocs;)Lpbi/executor/types/Base;', ACCESS_NOFLAGS, None, (('Ldalvik/annotation/Throws;', ((28, 'value', ((24, 'Lpbi/executor/exceptions/RuntimeError;'),)),), 'system'),),
   (34, 2, 5, 2912,
    ((8, 0, 33),                                  # move-object/from16 v0, p1
     (82, (0, 0), 'Lpbi/executor/RegLocs;->id:I'), # iget v0, v0, Lpbi/executor/RegLocs;->id:I
     (2, 20, 0),                                  # move/from16 v20, v0
     (2, 0, 20),                                  # move/from16 v0, v20
     (8, 1, 32),                                  # move-object/from16 v1, p0
     (89, (0, 1), 'Lpbi/executor/Main;->last_method:I'), # iput v0, v1, Lpbi/executor/Main;->last_method:I
     (8, 0, 33),                                  # move-object/from16 v0, p1
     (84, (9, 0), 'Lpbi/executor/RegLocs;->state:[Ljava/lang/Object;'), # iget-object v9, v0, Lpbi/executor/RegLocs;->state:[Ljava/lang/Object;
     (18, 3, 1),                                  # const/4 v3, 0x1
     (70, 3, 9, 3),                               # aget-object v3, v9, v3
     (31, 3, '[Ljava/lang/String;'),              # check-cast v3, [Ljava/lang/String;
     (18, 4, 3),                                  # const/4 v4, 0x3
     (70, 4, 9, 4),                               # aget-object v4, v9, v4
     (31, 4, '[I'),                               # check-cast v4, [I
     (18, 5, 4),                                  # const/4 v5, 0x4
     (70, 5, 9, 5),                               # aget-object v5, v9, v5
     (31, 5, '[[[I'),                             # check-cast v5, [[[I
     (19, 6, 9),                                  # const/16 v6, 0x9
     (70, 6, 9, 6),                               # aget-object v6, v9, v6
     (31, 6, '[I'),                               # check-cast v6, [I
     (8, 0, 33),                                  # move-object/from16 v0, p1
     (84, (0, 0), 'Lpbi/executor/RegLocs;->regs:[Lpbi/executor/types/Base;'), # iget-object v0, v0, Lpbi/executor/RegLocs;->regs:[Lpbi/executor/types/Base;
     (8, 21, 0),                                  # move-object/from16 v21, v0
     (8, 0, 33),                                  # move-object/from16 v0, p1
     (84, (0, 0), 'Lpbi/executor/RegLocs;->scope:Ljava/util/Map;'), # iget-object v0, v0, Lpbi/executor/RegLocs;->scope:Ljava/util/Map;
     (8, 22, 0),                                  # move-object/from16 v22, v0
     (18, 12, 0),                                 # const/4 v12, 0x0
     (18, 10, -1),                                # const/4 v10, -0x1
     (18, 7, 5),                                  # const/4 v7, 0x5
     (70, 7, 9, 7),                               # aget-object v7, v9, v7
     (31, 7, '[[I'),                              # check-cast v7, [[I
     (18, 8, 0),                                  # const/4 v8, 0x0
     (70, 23, 7, 8),                              # aget-object v23, v7, v8
     (18, 8, 1),                                  # const/4 v8, 0x1
     (70, 24, 7, 8),                              # aget-object v24, v7, v8
     (18, 8, 2),                                  # const/4 v8, 0x2
     (70, 25, 7, 8),                              # aget-object v25, v7, v8
     (18, 7, 6),                                  # const/4 v7, 0x6
     (70, 7, 9, 7),                               # aget-object v7, v9, v7
     (31, 7, '[Lpbi/executor/types/Base;'),       # check-cast v7, [Lpbi/executor/types/Base;
     (18, 8, 7),                                  # const/4 v8, 0x7
     (70, 8, 9, 8),                               # aget-object v8, v9, v8
     (31, 8, '[[I'),                              # check-cast v8, [[I
     (19, 11, 8),                                 # const/16 v11, 0x8
     (70, 9, 9, 11),                              # aget-object v9, v9, v11
     (31, 9, '[[[I'),                             # check-cast v9, [[[I
     (98, 15, 'Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;'), # sget-object v15, Lpbi/executor/Main;->True:Lpbi/executor/types/pBoolean;
     (98, 14, 'Lpbi/executor/Main;->False:Lpbi/executor/types/pBoolean;'), # sget-object v14, Lpbi/executor/Main;->False:Lpbi/executor/types/pBoolean;
     (98, 26, 'Lpbi/executor/Main;->void_map:Ljava/util/Map;'), # sget-object v26, Lpbi/executor/Main;->void_map:Ljava/util/Map;
     (98, 11, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v11, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
                                                  # :try_start_5c
                                                  # :goto_5c
     (68, 10, 4, 19),                             # aget v10, v4, v19
     (43, 10, 2702, ':pswitch_data_a8e'),         # packed-switch v10 :pswitch_data_a8e
                                                  # :pswitch_61  #0xa, 0x3d, 0x3f
     (34, 10, 'Lpbi/executor/exceptions/TypeError;'), # new-instance v10, Lpbi/executor/exceptions/TypeError;
     (34, 11, 'Ljava/lang/StringBuilder;'),       # new-instance v11, Ljava/lang/StringBuilder;
     (26, 13, '• code_'),                         # const-string v13, "• code_"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (11, 13)), # invoke-direct {v11, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (68, 13, 4, 19),                             # aget v13, v4, v19
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, ' не реализован!'),                 # const-string v13, " не реализован!"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (11,)), # invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 11),                                    # move-result-object v11
     (112, 'Lpbi/executor/exceptions/TypeError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/TypeError;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :try_end_7e
                                                  # :catch_7e
                                                  # .catch Ljava/lang/Throwable; {:try_start_5c .. :try_end_7e} :catch_7e
     (13, 10),                                    # move-exception v10
                                                  # :goto_7f
     (32, (11, 10), 'Lpbi/executor/exceptions/RuntimeError;'), # instance-of v11, v10, Lpbi/executor/exceptions/RuntimeError;
     (56, 11, 2517, ':cond_9d5'),                 # if-eqz v11, :cond_9d5
     (31, 10, 'Lpbi/executor/exceptions/RuntimeError;'), # check-cast v10, Lpbi/executor/exceptions/RuntimeError;
     (7, 11, 10),                                 # move-object v11, v10
                                                  # :goto_86
     (2, 0, 20),                                  # move/from16 v0, v20
     (2, 1, 19),                                  # move/from16 v1, v19
     (110, 'Lpbi/executor/exceptions/RuntimeError;->addStackRecord(II)V', (11, 0, 1)), # invoke-virtual {v11, v0, v1}, Lpbi/executor/exceptions/RuntimeError;->addStackRecord(II)V
     (84, (13, 11), 'Lpbi/executor/exceptions/RuntimeError;->err:Lpbi/executor/exceptions/PyException;'), # iget-object v13, v11, Lpbi/executor/exceptions/RuntimeError;->err:Lpbi/executor/exceptions/PyException;
     (57, 5, 2629, ':cond_a45'),                  # if-nez v5, :cond_a45
     (39, 11),                                    # throw v11
                                                  # :try_start_92
                                                  # :pswitch_92  #0x0
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (34, 13, 'Lpbi/executor/types/List;'),       # new-instance v13, Lpbi/executor/types/List;
     (68, 16, 24, 19),                            # aget v16, v24, v19
     (2, 0, 16),                                  # move/from16 v0, v16
     (112, 'Lpbi/executor/types/List;-><init>(I)V', (13, 0)), # invoke-direct {v13, v0}, Lpbi/executor/types/List;-><init>(I)V
     (77, 13, 21, 10),                            # aput-object v13, v21, v10
     (1, 10, 12),                                 # move v10, v12
                                                  # :cond_a0
                                                  # :goto_a0
     (216, (12, 19), 1),                          # add-int/lit8 v12, v19, 0x1
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (40, 92, ':goto_5c'),                        # goto :goto_5c
                                                  # :pswitch_a6  #0x1
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_start_a8
                                                  # :try_end_a8
                                                  # .catch Ljava/lang/Throwable; {:try_start_92 .. :try_end_a8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (57, 12, 203, ':cond_cb'),                   # if-nez v12, :cond_cb
     (34, 11, 'Lpbi/executor/exceptions/NameError;'), # new-instance v11, Lpbi/executor/exceptions/NameError;
     (34, 12, 'Ljava/lang/StringBuilder;'),       # new-instance v12, Ljava/lang/StringBuilder;
     (26, 13, "name 'regs:"),                     # const-string v13, "name 'regs:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (12, 13)), # invoke-direct {v12, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (12, 10)), # invoke-virtual {v12, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (12,)), # invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (11, 12)), # invoke-direct {v11, v12}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (39, 11),                                    # throw v11
                                                  # :catch_c7
     (13, 11),                                    # move-exception v11
     (1, 12, 10),                                 # move v12, v10
     (7, 10, 11),                                 # move-object v10, v11
     (40, 127, ':goto_7f'),                       # goto :goto_7f
                                                  # :cond_cb
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (70, 13, 21, 13),                            # aget-object v13, v21, v13
     (68, 16, 24, 19),                            # aget v16, v24, v19
     (2, 0, 16),                                  # move/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__setitem__(ILpbi/executor/types/Base;)V', (13, 0, 12)), # invoke-virtual {v13, v0, v12}, Lpbi/executor/types/Base;->__setitem__(ILpbi/executor/types/Base;)V
                                                  # :try_end_d6
                                                  # .catch Ljava/lang/Throwable; {:try_start_a8 .. :try_end_d6} :catch_c7
     (40, 160, ':goto_a0'),                       # goto :goto_a0
                                                  # :try_start_d7
                                                  # :pswitch_d7  #0x2
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (34, 13, 'Lpbi/executor/types/List;'),       # new-instance v13, Lpbi/executor/types/List;
     (112, 'Lpbi/executor/types/List;-><init>()V', (13,)), # invoke-direct {v13}, Lpbi/executor/types/List;-><init>()V
     (77, 13, 21, 10),                            # aput-object v13, v21, v10
     (1, 10, 12),                                 # move v10, v12
     (40, 160, ':goto_a0'),                       # goto :goto_a0
                                                  # :pswitch_e2  #0x3
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_e4
                                                  # :try_start_e4
                                                  # .catch Ljava/lang/Throwable; {:try_start_d7 .. :try_end_e4} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__iter__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__iter__()Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_ec
                                                  # .catch Ljava/lang/Throwable; {:try_start_e4 .. :try_end_ec} :catch_c7
     (40, 160, ':goto_a0'),                       # goto :goto_a0
                                                  # :pswitch_ed  #0x4
                                                  # :try_start_ed
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_ef
                                                  # :try_start_ef
                                                  # .catch Ljava/lang/Throwable; {:try_start_ed .. :try_end_ef} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;
                                                  # :try_end_f4
                                                  # .catch Ljava/lang/Throwable; {:try_start_ef .. :try_end_f4} :catch_c7
                                                  # .catch Lpbi/executor/exceptions/StopIteration; {:try_start_ef .. :try_end_f4} :catch_fa
     (12, 12),                                    # move-result-object v12
                                                  # :try_start_f5
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (77, 12, 21, 13),                            # aput-object v12, v21, v13
     (40, 160, ':goto_a0'),                       # goto :goto_a0
                                                  # :catch_fa
     (13, 12),                                    # move-exception v12
     (68, 12, 25, 19),                            # aget v12, v25, v19
                                                  # :try_end_fd
                                                  # .catch Ljava/lang/Throwable; {:try_start_f5 .. :try_end_fd} :catch_c7
     (144, 12, 12, 19),                           # add-int v12, v12, v19
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :try_start_104
                                                  # :pswitch_104  #0x5
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_108
                                                  # :try_end_108
                                                  # .catch Ljava/lang/Throwable; {:try_start_104 .. :try_end_108} :catch_7e
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 12, 21, 12),                            # aget-object v12, v21, v12
     (110, 'Lpbi/executor/types/Base;->__len()I', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__len()I
     (10, 12),                                    # move-result v12
     (55, (12, 13), 303, ':cond_12f'),            # if-le v12, v13, :cond_12f
     (34, 11, 'Lpbi/executor/exceptions/ValueError;'), # new-instance v11, Lpbi/executor/exceptions/ValueError;
     (34, 12, 'Ljava/lang/StringBuilder;'),       # new-instance v12, Ljava/lang/StringBuilder;
     (26, 16, 'too many values to unpack (expected '), # const-string v16, "too many values to unpack (expected "
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (12, 0)), # invoke-direct {v12, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (26, 13, ')'),                               # const-string v13, ")"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (12,)), # invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (112, 'Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V', (11, 12)), # invoke-direct {v11, v12}, Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V
     (39, 11),                                    # throw v11
                                                  # :cond_12f
     (53, (12, 13), 160, ':cond_a0'),             # if-ge v12, v13, :cond_a0
     (34, 11, 'Lpbi/executor/exceptions/ValueError;'), # new-instance v11, Lpbi/executor/exceptions/ValueError;
     (34, 16, 'Ljava/lang/StringBuilder;'),       # new-instance v16, Ljava/lang/StringBuilder;
     (26, 17, 'not enough values to unpack (expected '), # const-string v17, "not enough values to unpack (expected "
     (118, 16, 17, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V'), # invoke-direct/range {v16 .. v17}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (0, 13)), # invoke-virtual {v0, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 13),                                    # move-result-object v13
     (26, 16, ', got '),                          # const-string v16, ", got "
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (13, 0)), # invoke-virtual {v13, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 13),                                    # move-result-object v13
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (13, 12)), # invoke-virtual {v13, v12}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (26, 13, ')'),                               # const-string v13, ")"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (12,)), # invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (112, 'Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V', (11, 12)), # invoke-direct {v11, v12}, Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V
     (39, 11),                                    # throw v11
                                                  # :try_start_15a
                                                  # :pswitch_15a  #0x6
                                                  # :try_end_15a
                                                  # .catch Ljava/lang/Throwable; {:try_start_108 .. :try_end_15a} :catch_c7
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_15c
                                                  # :try_end_15c
                                                  # .catch Ljava/lang/Throwable; {:try_start_15a .. :try_end_15c} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (68, 16, 25, 19),                            # aget v16, v25, v19
     (2, 0, 16),                                  # move/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__getitem__(I)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__getitem__(I)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_16a
                                                  # .catch Ljava/lang/Throwable; {:try_start_15c .. :try_end_16a} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_16c
                                                  # :pswitch_16c  #0x7
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_16e
                                                  # :try_end_16e
                                                  # .catch Ljava/lang/Throwable; {:try_start_16c .. :try_end_16e} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__bool()Z', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__bool()Z
     (10, 12),                                    # move-result v12
     (57, 12, 160, ':cond_a0'),                   # if-nez v12, :cond_a0
     (68, 12, 24, 19),                            # aget v12, v24, v19
                                                  # :try_end_178
                                                  # .catch Ljava/lang/Throwable; {:try_start_16e .. :try_end_178} :catch_c7
     (144, 12, 12, 19),                           # add-int v12, v12, v19
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :pswitch_17f  #0x8
                                                  # :try_start_17f
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (57, 13, 416, ':cond_1a0'),                  # if-nez v13, :cond_1a0
     (34, 10, 'Lpbi/executor/exceptions/NameError;'), # new-instance v10, Lpbi/executor/exceptions/NameError;
     (34, 11, 'Ljava/lang/StringBuilder;'),       # new-instance v11, Ljava/lang/StringBuilder;
     (26, 13, "name 'regs:"),                     # const-string v13, "name 'regs:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (11, 13)), # invoke-direct {v11, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 12)), # invoke-virtual {v11, v12}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (11,)), # invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 11),                                    # move-result-object v11
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :cond_1a0
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_1a2
                                                  # :try_start_1a2
                                                  # .catch Ljava/lang/Throwable; {:try_start_17f .. :try_end_1a2} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->append(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->append(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
                                                  # :try_end_1a7
                                                  # .catch Ljava/lang/Throwable; {:try_start_1a2 .. :try_end_1a7} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_1a9  #0x9
                                                  # :try_start_1a9
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (144, 10, 10, 19),                           # add-int v10, v10, v19
     (2, 19, 10),                                 # move/from16 v19, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :pswitch_1b1  #0xb
     (34, 10, 'Ljava/lang/Exception;'),           # new-instance v10, Ljava/lang/Exception;
     (26, 11, '11 недопустим'),                   # const-string v11, "11 недопустим"
     (112, 'Ljava/lang/Exception;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :pswitch_1b9  #0xc
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_1bb
                                                  # :try_end_1bb
                                                  # .catch Ljava/lang/Throwable; {:try_start_1a9 .. :try_end_1bb} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (57, 12, 474, ':cond_1da'),                  # if-nez v12, :cond_1da
     (34, 11, 'Lpbi/executor/exceptions/NameError;'), # new-instance v11, Lpbi/executor/exceptions/NameError;
     (34, 12, 'Ljava/lang/StringBuilder;'),       # new-instance v12, Ljava/lang/StringBuilder;
     (26, 13, "name 'regs:"),                     # const-string v13, "name 'regs:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (12, 13)), # invoke-direct {v12, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (12, 10)), # invoke-virtual {v12, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (12,)), # invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (11, 12)), # invoke-direct {v11, v12}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (39, 11),                                    # throw v11
                                                  # :cond_1da
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (8, 1, 33),                                  # move-object/from16 v1, p1
     (110, 'Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V', (0, 1, 13, 12)), # invoke-virtual {v0, v1, v13, v12}, Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V
                                                  # :try_end_1e3
                                                  # .catch Ljava/lang/Throwable; {:try_start_1bb .. :try_end_1e3} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_1e5  #0xd
                                                  # :try_start_1e5
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_1e7
                                                  # :try_start_1e7
                                                  # .catch Ljava/lang/Throwable; {:try_start_1e5 .. :try_end_1e7} :catch_7e
     (34, 12, 'Lpbi/executor/types/Tuple;'),      # new-instance v12, Lpbi/executor/types/Tuple;
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (112, 'Lpbi/executor/types/Tuple;-><init>(Lpbi/executor/types/Base;)V', (12, 13)), # invoke-direct {v12, v13}, Lpbi/executor/types/Tuple;-><init>(Lpbi/executor/types/Base;)V
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_1f0
                                                  # .catch Ljava/lang/Throwable; {:try_start_1e7 .. :try_end_1f0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_1f2
                                                  # :pswitch_1f2  #0xe
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_1f8
                                                  # :try_start_1f8
                                                  # .catch Ljava/lang/Throwable; {:try_start_1f2 .. :try_end_1f8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__add__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__add__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_200
                                                  # .catch Ljava/lang/Throwable; {:try_start_1f8 .. :try_end_200} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_202
                                                  # :pswitch_202  #0xf
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_208
                                                  # :try_end_208
                                                  # .catch Ljava/lang/Throwable; {:try_start_202 .. :try_end_208} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__sub__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__sub__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_210
                                                  # .catch Ljava/lang/Throwable; {:try_start_208 .. :try_end_210} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_212  #0x10
                                                  # :try_start_212
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_218
                                                  # :try_start_218
                                                  # .catch Ljava/lang/Throwable; {:try_start_212 .. :try_end_218} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__mul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__mul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_220
                                                  # .catch Ljava/lang/Throwable; {:try_start_218 .. :try_end_220} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_222
                                                  # :pswitch_222  #0x11
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_228
                                                  # :try_start_228
                                                  # .catch Ljava/lang/Throwable; {:try_start_222 .. :try_end_228} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__matmul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__matmul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_230
                                                  # .catch Ljava/lang/Throwable; {:try_start_228 .. :try_end_230} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_232  #0x12
                                                  # :try_start_232
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_238
                                                  # :try_end_238
                                                  # .catch Ljava/lang/Throwable; {:try_start_232 .. :try_end_238} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__truediv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__truediv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_240
                                                  # .catch Ljava/lang/Throwable; {:try_start_238 .. :try_end_240} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_242  #0x13
                                                  # :try_start_242
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_248
                                                  # :try_start_248
                                                  # .catch Ljava/lang/Throwable; {:try_start_242 .. :try_end_248} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__mod__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__mod__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_250
                                                  # .catch Ljava/lang/Throwable; {:try_start_248 .. :try_end_250} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_252
                                                  # :pswitch_252  #0x14
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_258
                                                  # :try_end_258
                                                  # .catch Ljava/lang/Throwable; {:try_start_252 .. :try_end_258} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__and__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__and__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_260
                                                  # .catch Ljava/lang/Throwable; {:try_start_258 .. :try_end_260} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_262  #0x15
                                                  # :try_start_262
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_268
                                                  # :try_start_268
                                                  # .catch Ljava/lang/Throwable; {:try_start_262 .. :try_end_268} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__or__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__or__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_270
                                                  # .catch Ljava/lang/Throwable; {:try_start_268 .. :try_end_270} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_272
                                                  # :pswitch_272  #0x16
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_278
                                                  # :try_end_278
                                                  # .catch Ljava/lang/Throwable; {:try_start_272 .. :try_end_278} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__xor__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__xor__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_280
                                                  # .catch Ljava/lang/Throwable; {:try_start_278 .. :try_end_280} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_282
                                                  # :pswitch_282  #0x17
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_288
                                                  # :try_end_288
                                                  # .catch Ljava/lang/Throwable; {:try_start_282 .. :try_end_288} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__lshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__lshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_290
                                                  # .catch Ljava/lang/Throwable; {:try_start_288 .. :try_end_290} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_292  #0x18
                                                  # :try_start_292
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_298
                                                  # :try_start_298
                                                  # .catch Ljava/lang/Throwable; {:try_start_292 .. :try_end_298} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__rshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__rshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_2a0
                                                  # .catch Ljava/lang/Throwable; {:try_start_298 .. :try_end_2a0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_2a2  #0x19
                                                  # :try_start_2a2
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_2a8
                                                  # :try_start_2a8
                                                  # .catch Ljava/lang/Throwable; {:try_start_2a2 .. :try_end_2a8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__pow__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__pow__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_2b0
                                                  # .catch Ljava/lang/Throwable; {:try_start_2a8 .. :try_end_2b0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_2b2  #0x1a
                                                  # :try_start_2b2
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_2b8
                                                  # :try_start_2b8
                                                  # .catch Ljava/lang/Throwable; {:try_start_2b2 .. :try_end_2b8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__floordiv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__floordiv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_2c0
                                                  # .catch Ljava/lang/Throwable; {:try_start_2b8 .. :try_end_2c0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_2c2
                                                  # :pswitch_2c2  #0x1b
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_2c8
                                                  # :try_end_2c8
                                                  # .catch Ljava/lang/Throwable; {:try_start_2c2 .. :try_end_2c8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__lt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__lt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_2d0
                                                  # .catch Ljava/lang/Throwable; {:try_start_2c8 .. :try_end_2d0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_2d2  #0x1c
                                                  # :try_start_2d2
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_2d8
                                                  # :try_start_2d8
                                                  # .catch Ljava/lang/Throwable; {:try_start_2d2 .. :try_end_2d8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__gt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__gt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_2e0
                                                  # .catch Ljava/lang/Throwable; {:try_start_2d8 .. :try_end_2e0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_2e2
                                                  # :pswitch_2e2  #0x1d
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_2e8
                                                  # :try_end_2e8
                                                  # .catch Ljava/lang/Throwable; {:try_start_2e2 .. :try_end_2e8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__eq(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__eq(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_2f0
                                                  # .catch Ljava/lang/Throwable; {:try_start_2e8 .. :try_end_2f0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_2f2
                                                  # :pswitch_2f2  #0x1e
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_2f8
                                                  # :try_start_2f8
                                                  # .catch Ljava/lang/Throwable; {:try_start_2f2 .. :try_end_2f8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__ge(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__ge(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_300
                                                  # .catch Ljava/lang/Throwable; {:try_start_2f8 .. :try_end_300} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_302
                                                  # :pswitch_302  #0x1f
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_308
                                                  # :try_end_308
                                                  # .catch Ljava/lang/Throwable; {:try_start_302 .. :try_end_308} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__le(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__le(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_310
                                                  # .catch Ljava/lang/Throwable; {:try_start_308 .. :try_end_310} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_312  #0x20
                                                  # :try_start_312
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_318
                                                  # :try_end_318
                                                  # .catch Ljava/lang/Throwable; {:try_start_312 .. :try_end_318} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__ne(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (12, 13)), # invoke-virtual {v12, v13}, Lpbi/executor/types/Base;->__ne(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_320
                                                  # .catch Ljava/lang/Throwable; {:try_start_318 .. :try_end_320} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_322  #0x21
                                                  # :try_start_322
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_328
                                                  # :try_end_328
                                                  # .catch Ljava/lang/Throwable; {:try_start_322 .. :try_end_328} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__contains__(Lpbi/executor/types/Base;)Lpbi/executor/types/pBoolean;', (13, 12)), # invoke-virtual {v13, v12}, Lpbi/executor/types/Base;->__contains__(Lpbi/executor/types/Base;)Lpbi/executor/types/pBoolean;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_330
                                                  # .catch Ljava/lang/Throwable; {:try_start_328 .. :try_end_330} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_332
                                                  # :pswitch_332  #0x22
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_338
                                                  # :try_start_338
                                                  # .catch Ljava/lang/Throwable; {:try_start_332 .. :try_end_338} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (51, (12, 13), 833, ':cond_341'),            # if-ne v12, v13, :cond_341
     (7, 12, 15),                                 # move-object v12, v15
                                                  # :goto_33d
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_33f
                                                  # .catch Ljava/lang/Throwable; {:try_start_338 .. :try_end_33f} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_341
     (7, 12, 14),                                 # move-object v12, v14
     (40, 829, ':goto_33d'),                      # goto :goto_33d
                                                  # :pswitch_343  #0x23
                                                  # :try_start_343
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_345
                                                  # :try_end_345
                                                  # .catch Ljava/lang/Throwable; {:try_start_343 .. :try_end_345} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__bool()Z', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__bool()Z
     (10, 12),                                    # move-result v12
     (56, 12, 850, ':cond_352'),                  # if-eqz v12, :cond_352
     (7, 12, 14),                                 # move-object v12, v14
                                                  # :goto_34e
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_350
                                                  # .catch Ljava/lang/Throwable; {:try_start_345 .. :try_end_350} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_352
     (7, 12, 15),                                 # move-object v12, v15
     (40, 846, ':goto_34e'),                      # goto :goto_34e
                                                  # :pswitch_354  #0x24
                                                  # :try_start_354
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_35a
                                                  # :try_start_35a
                                                  # .catch Ljava/lang/Throwable; {:try_start_354 .. :try_end_35a} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__getitem__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__getitem__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_366
                                                  # .catch Ljava/lang/Throwable; {:try_start_35a .. :try_end_366} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_368  #0x25
                                                  # :try_start_368
     (70, 13, 8, 19),                             # aget-object v13, v8, v19
     (33, 0, 13),                                 # array-length v0, v13
     (2, 16, 0),                                  # move/from16 v16, v0
     (2, 0, 16),                                  # move/from16 v0, v16
     (35, (0, 0), '[Lpbi/executor/types/Base;'),  # new-array v0, v0, [Lpbi/executor/types/Base;
     (8, 17, 0),                                  # move-object/from16 v17, v0
     (18, 10, 0),                                 # const/4 v10, 0x0
                                                  # :goto_374
     (2, 0, 16),                                  # move/from16 v0, v16
     (52, (10, 0), 910, ':cond_38e'),             # if-lt v10, v0, :cond_38e
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_37a
                                                  # :try_start_37a
                                                  # .catch Ljava/lang/Throwable; {:try_start_368 .. :try_end_37a} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (8, 0, 17),                                  # move-object/from16 v0, v17
     (8, 1, 26),                                  # move-object/from16 v1, v26
     (110, 'Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;', (12, 0, 1)), # invoke-virtual {v12, v0, v1}, Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
     (2, 0, 20),                                  # move/from16 v0, v20
     (8, 1, 32),                                  # move-object/from16 v1, p0
     (89, (0, 1), 'Lpbi/executor/Main;->last_method:I'), # iput v0, v1, Lpbi/executor/Main;->last_method:I
                                                  # :try_end_38c
                                                  # .catch Ljava/lang/Throwable; {:try_start_37a .. :try_end_38c} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_38e
                                                  # :try_start_38e
     (68, 12, 13, 10),                            # aget v12, v13, v10
     (70, 18, 21, 12),                            # aget-object v18, v21, v12
     (77, 18, 17, 10),                            # aput-object v18, v17, v10
     (216, (10, 10), 1),                          # add-int/lit8 v10, v10, 0x1
     (40, 884, ':goto_374'),                      # goto :goto_374
                                                  # :pswitch_397  #0x26
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_399
                                                  # :try_end_399
                                                  # .catch Ljava/lang/Throwable; {:try_start_38e .. :try_end_399} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (70, 16, 7, 19),                             # aget-object v16, v7, v19
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__getattr__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__getattr__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_3a7
                                                  # .catch Ljava/lang/Throwable; {:try_start_399 .. :try_end_3a7} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_3a9  #0x27
                                                  # :try_start_3a9
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_3ab
                                                  # :try_start_3ab
                                                  # .catch Ljava/lang/Throwable; {:try_start_3a9 .. :try_end_3ab} :catch_7e
     (34, 12, 'Ljava/util/ArrayList;'),           # new-instance v12, Ljava/util/ArrayList;
     (112, 'Ljava/util/ArrayList;-><init>()V', (12,)), # invoke-direct {v12}, Ljava/util/ArrayList;-><init>()V
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (110, 'Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', (12, 13)), # invoke-virtual {v12, v13}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
     (34, 13, 'Lpbi/executor/types/List;'),       # new-instance v13, Lpbi/executor/types/List;
     (112, 'Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V', (13, 12)), # invoke-direct {v13, v12}, Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V
     (77, 13, 21, 10),                            # aput-object v13, v21, v10
                                                  # :try_end_3bc
                                                  # .catch Ljava/lang/Throwable; {:try_start_3ab .. :try_end_3bc} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_3be  #0x28
                                                  # :try_start_3be
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 16, 21, 12),                            # aget-object v16, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_3c8
                                                  # :try_start_3c8
                                                  # .catch Ljava/lang/Throwable; {:try_start_3be .. :try_end_3c8} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__setitem__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)V', (13, 0, 12)), # invoke-virtual {v13, v0, v12}, Lpbi/executor/types/Base;->__setitem__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)V
                                                  # :try_end_3cf
                                                  # .catch Ljava/lang/Throwable; {:try_start_3c8 .. :try_end_3cf} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_3d1  #0x29
                                                  # :try_start_3d1
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_start_3d7
                                                  # :try_end_3d7
                                                  # .catch Ljava/lang/Throwable; {:try_start_3d1 .. :try_end_3d7} :catch_7e
     (70, 12, 7, 19),                             # aget-object v12, v7, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__setattr__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)V', (13, 12, 0)), # invoke-virtual {v13, v12, v0}, Lpbi/executor/types/Base;->__setattr__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;)V
                                                  # :try_end_3e0
                                                  # .catch Ljava/lang/Throwable; {:try_start_3d7 .. :try_end_3e0} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_3e2  #0x2a
                                                  # :try_start_3e2
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (34, 13, 'Lpbi/executor/Wrapper;'),          # new-instance v13, Lpbi/executor/Wrapper;
     (68, 16, 24, 19),                            # aget v16, v24, v19
     (8, 0, 33),                                  # move-object/from16 v0, p1
     (2, 1, 16),                                  # move/from16 v1, v16
     (112, 'Lpbi/executor/Wrapper;-><init>(Lpbi/executor/RegLocs;I)V', (13, 0, 1)), # invoke-direct {v13, v0, v1}, Lpbi/executor/Wrapper;-><init>(Lpbi/executor/RegLocs;I)V
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (8, 1, 33),                                  # move-object/from16 v1, p1
     (110, 'Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V', (0, 1, 10, 13)), # invoke-virtual {v0, v1, v10, v13}, Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_3f9  #0x2b
     (98, 3, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v3, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
                                                  # :goto_3fb
     (17, 3),                                     # return-object v3
                                                  # :pswitch_3fc  #0x2c
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 3, 21, 12),                             # aget-object v3, v21, v12
     (40, 1019, ':goto_3fb'),                     # goto :goto_3fb
                                                  # :pswitch_401  #0x2d
     (70, 27, 8, 19),                             # aget-object v27, v8, v19
     (8, 0, 27),                                  # move-object/from16 v0, v27
     (33, 10, 0),                                 # array-length v10, v0
     (35, (0, 10), '[Lpbi/executor/types/Base;'), # new-array v0, v10, [Lpbi/executor/types/Base;
     (8, 16, 0),                                  # move-object/from16 v16, v0
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (33, 0, 0),                                  # array-length v0, v0
     (2, 28, 0),                                  # move/from16 v28, v0
     (18, 13, 0),                                 # const/4 v13, 0x0
     (68, 10, 24, 19),                            # aget v10, v24, v19
     (19, 17, 1),                                 # const/16 v17, 0x1
     (2, 0, 17),                                  # move/from16 v0, v17
     (51, (10, 0), 1163, ':cond_48b'),            # if-ne v10, v0, :cond_48b
     (18, 10, 0),                                 # const/4 v10, 0x0
     (2, 31, 10),                                 # move/from16 v31, v10
     (1, 10, 13),                                 # move v10, v13
     (2, 13, 31),                                 # move/from16 v13, v31
                                                  # :goto_41e
     (2, 0, 28),                                  # move/from16 v0, v28
     (52, (13, 0), 1088, ':cond_440'),            # if-lt v13, v0, :cond_440
     (35, (13, 10), '[Lpbi/executor/types/Base;'), # new-array v13, v10, [Lpbi/executor/types/Base;
                                                  # :try_end_424
                                                  # .catch Ljava/lang/Throwable; {:try_start_3e2 .. :try_end_424} :catch_7e
     (19, 17, 0),                                 # const/16 v17, 0x0
     (18, 10, 0),                                 # const/4 v10, 0x0
     (2, 18, 17),                                 # move/from16 v18, v17
     (2, 17, 10),                                 # move/from16 v17, v10
                                                  # :goto_42b
     (2, 0, 17),                                  # move/from16 v0, v17
     (2, 1, 28),                                  # move/from16 v1, v28
     (52, (0, 1), 1125, ':cond_465'),             # if-lt v0, v1, :cond_465
     (1, 10, 12),                                 # move v10, v12
     (7, 12, 13),                                 # move-object v12, v13
                                                  # :try_start_433
                                                  # :goto_433
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (34, 16, 'Lpbi/executor/types/Tuple;'),      # new-instance v16, Lpbi/executor/types/Tuple;
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (112, 'Lpbi/executor/types/Tuple;-><init>([Lpbi/executor/types/Base;)V', (0, 12)), # invoke-direct {v0, v12}, Lpbi/executor/types/Tuple;-><init>([Lpbi/executor/types/Base;)V
     (77, 16, 21, 13),                            # aput-object v16, v21, v13
                                                  # :try_end_43e
                                                  # .catch Ljava/lang/Throwable; {:try_start_433 .. :try_end_43e} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_440
                                                  # :try_start_440
     (68, 12, 27, 13),                            # aget v12, v27, v13
     (59, 12, 1118, ':cond_45e'),                 # if-gez v12, :cond_45e
     (223, (12, 12), -1),                         # xor-int/lit8 v12, v12, -0x1
     (70, 17, 21, 12),                            # aget-object v17, v21, v12
     (116, 17, 17, 'Lpbi/executor/types/Base;->__tuple2()Lpbi/executor/types/Tuple;'), # invoke-virtual/range {v17 .. v17}, Lpbi/executor/types/Base;->__tuple2()Lpbi/executor/types/Tuple;
     (12, 17),                                    # move-result-object v17
     (8, 0, 17),                                  # move-object/from16 v0, v17
     (84, (0, 0), 'Lpbi/executor/types/Tuple;->arr:[Lpbi/executor/types/Base;'), # iget-object v0, v0, Lpbi/executor/types/Tuple;->arr:[Lpbi/executor/types/Base;
     (8, 18, 0),                                  # move-object/from16 v18, v0
     (8, 0, 18),                                  # move-object/from16 v0, v18
     (33, 0, 0),                                  # array-length v0, v0
     (2, 18, 0),                                  # move/from16 v18, v0
     (144, 10, 10, 18),                           # add-int v10, v10, v18
     (77, 17, 16, 13),                            # aput-object v17, v16, v13
                                                  # :goto_45b
     (216, (13, 13), 1),                          # add-int/lit8 v13, v13, 0x1
     (40, 1054, ':goto_41e'),                     # goto :goto_41e
                                                  # :cond_45e
     (70, 17, 21, 12),                            # aget-object v17, v21, v12
     (216, (10, 10), 1),                          # add-int/lit8 v10, v10, 0x1
     (77, 17, 16, 13),                            # aput-object v17, v16, v13
     (40, 1115, ':goto_45b'),                     # goto :goto_45b
                                                  # :cond_465
     (68, 10, 27, 17),                            # aget v10, v27, v17
     (59, 10, 1156, ':cond_484'),                 # if-gez v10, :cond_484
     (70, 10, 16, 17),                            # aget-object v10, v16, v17
     (31, 10, 'Lpbi/executor/types/Tuple;'),      # check-cast v10, Lpbi/executor/types/Tuple;
     (84, (10, 10), 'Lpbi/executor/types/Tuple;->arr:[Lpbi/executor/types/Base;'), # iget-object v10, v10, Lpbi/executor/types/Tuple;->arr:[Lpbi/executor/types/Base;
     (33, 0, 10),                                 # array-length v0, v10
     (2, 29, 0),                                  # move/from16 v29, v0
     (19, 30, 0),                                 # const/16 v30, 0x0
     (2, 0, 30),                                  # move/from16 v0, v30
     (2, 1, 18),                                  # move/from16 v1, v18
     (2, 2, 29),                                  # move/from16 v2, v29
     (113, 'Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V', (10, 0, 13, 1, 2)), # invoke-static {v10, v0, v13, v1, v2}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V
     (144, 10, 18, 29),                           # add-int v10, v18, v29
                                                  # :goto_47f
     (216, (17, 17), 1),                          # add-int/lit8 v17, v17, 0x1
     (2, 18, 10),                                 # move/from16 v18, v10
     (40, 1067, ':goto_42b'),                     # goto :goto_42b
                                                  # :cond_484
     (216, (10, 18), 1),                          # add-int/lit8 v10, v18, 0x1
     (70, 29, 16, 17),                            # aget-object v29, v16, v17
     (77, 29, 13, 18),                            # aput-object v29, v13, v18
     (40, 1151, ':goto_47f'),                     # goto :goto_47f
                                                  # :cond_48b
     (18, 10, 0),                                 # const/4 v10, 0x0
                                                  # :goto_48c
     (2, 0, 28),                                  # move/from16 v0, v28
     (52, (10, 0), 1172, ':cond_494'),            # if-lt v10, v0, :cond_494
     (1, 10, 12),                                 # move v10, v12
     (8, 12, 16),                                 # move-object/from16 v12, v16
     (40, 1075, ':goto_433'),                     # goto :goto_433
                                                  # :cond_494
     (68, 12, 27, 10),                            # aget v12, v27, v10
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (77, 13, 16, 10),                            # aput-object v13, v16, v10
     (216, (10, 10), 1),                          # add-int/lit8 v10, v10, 0x1
     (40, 1164, ':goto_48c'),                     # goto :goto_48c
                                                  # :pswitch_49d  #0x2e
     (34, 11, 'Ljava/util/HashMap;'),             # new-instance v11, Ljava/util/HashMap;
     (112, 'Ljava/util/HashMap;-><init>()V', (11,)), # invoke-direct {v11}, Ljava/util/HashMap;-><init>()V
     (33, 13, 3),                                 # array-length v13, v3
     (18, 10, 0),                                 # const/4 v10, 0x0
                                                  # :goto_4a4
     (52, (10, 13), 1202, ':cond_4b2'),           # if-lt v10, v13, :cond_4b2
     (34, 10, 'Lpbi/executor/types/Type;'),       # new-instance v10, Lpbi/executor/types/Type;
     (70, 13, 8, 19),                             # aget-object v13, v8, v19
     (8, 0, 21),                                  # move-object/from16 v0, v21
     (112, 'Lpbi/executor/types/Type;-><init>([Lpbi/executor/types/Base;[ILjava/util/Map;)V', (10, 0, 13, 11)), # invoke-direct {v10, v0, v13, v11}, Lpbi/executor/types/Type;-><init>([Lpbi/executor/types/Base;[ILjava/util/Map;)V
     (7, 3, 10),                                  # move-object v3, v10
     (41, 1019, ':goto_3fb'),                     # goto/16 :goto_3fb
                                                  # :cond_4b2
     (70, 16, 3, 10),                             # aget-object v16, v3, v10
     (56, 16, 1215, ':cond_4bf'),                 # if-eqz v16, :cond_4bf
     (70, 17, 21, 10),                            # aget-object v17, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (8, 1, 17),                                  # move-object/from16 v1, v17
     (114, 'Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;', (11, 0, 1)), # invoke-interface {v11, v0, v1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
                                                  # :cond_4bf
     (216, (10, 10), 1),                          # add-int/lit8 v10, v10, 0x1
     (40, 1188, ':goto_4a4'),                     # goto :goto_4a4
                                                  # :pswitch_4c2  #0x2f
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (34, 13, 'Lpbi/executor/types/Dict;'),       # new-instance v13, Lpbi/executor/types/Dict;
     (112, 'Lpbi/executor/types/Dict;-><init>()V', (13,)), # invoke-direct {v13}, Lpbi/executor/types/Dict;-><init>()V
     (77, 13, 21, 10),                            # aput-object v13, v21, v10
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_4ce  #0x30
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (8, 1, 33),                                  # move-object/from16 v1, p1
     (110, 'Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V', (0, 1, 10, 11)), # invoke-virtual {v0, v1, v10, v11}, Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V
     (98, 11, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v11, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_4dc  #0x31
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_4de
                                                  # :try_end_4de
                                                  # .catch Ljava/lang/Throwable; {:try_start_440 .. :try_end_4de} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__raise__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__raise__()Lpbi/executor/types/Base;
                                                  # :try_end_4e3
                                                  # .catch Ljava/lang/Throwable; {:try_start_4de .. :try_end_4e3} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_4e5  #0x32
                                                  # :try_start_4e5
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (34, 13, 'Lpbi/executor/types/pSet;'),       # new-instance v13, Lpbi/executor/types/pSet;
     (112, 'Lpbi/executor/types/pSet;-><init>()V', (13,)), # invoke-direct {v13}, Lpbi/executor/types/pSet;-><init>()V
     (77, 13, 21, 10),                            # aput-object v13, v21, v10
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_4f1  #0x33
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_4f3
                                                  # :try_start_4f3
                                                  # .catch Ljava/lang/Throwable; {:try_start_4e5 .. :try_end_4f3} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__pos__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__pos__()Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_4fb
                                                  # .catch Ljava/lang/Throwable; {:try_start_4f3 .. :try_end_4fb} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_4fd
                                                  # :pswitch_4fd  #0x34
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_4ff
                                                  # :try_end_4ff
                                                  # .catch Ljava/lang/Throwable; {:try_start_4fd .. :try_end_4ff} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__neg__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__neg__()Lpbi/executor/types/Base;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_507
                                                  # .catch Ljava/lang/Throwable; {:try_start_4ff .. :try_end_507} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_509
                                                  # :pswitch_509  #0x35
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_end_50b
                                                  # :try_start_50b
                                                  # .catch Ljava/lang/Throwable; {:try_start_509 .. :try_end_50b} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__invert__()Lpbi/executor/types/BigInt;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__invert__()Lpbi/executor/types/BigInt;
     (12, 12),                                    # move-result-object v12
     (77, 12, 21, 10),                            # aput-object v12, v21, v10
                                                  # :try_end_513
                                                  # .catch Ljava/lang/Throwable; {:try_start_50b .. :try_end_513} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_515
                                                  # :pswitch_515  #0x36
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_517
                                                  # :try_end_517
                                                  # .catch Ljava/lang/Throwable; {:try_start_515 .. :try_end_517} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (110, 'Lpbi/executor/types/Base;->__enter__()Lpbi/executor/types/Base;', (13,)), # invoke-virtual {v13}, Lpbi/executor/types/Base;->__enter__()Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_521
                                                  # .catch Ljava/lang/Throwable; {:try_start_517 .. :try_end_521} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_523
                                                  # :pswitch_523  #0x37
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (32, (10, 11), 'Lpbi/executor/exceptions/PyException;'), # instance-of v10, v11, Lpbi/executor/exceptions/PyException;
     (56, 10, 1352, ':cond_548'),                 # if-eqz v10, :cond_548
     (7, 0, 11),                                  # move-object v0, v11
     (31, 0, 'Lpbi/executor/exceptions/PyException;'), # check-cast v0, Lpbi/executor/exceptions/PyException;
     (7, 10, 0),                                  # move-object v10, v0
     (98, 11, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v11, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (110, 'Lpbi/executor/exceptions/PyException;->__type__()Lpbi/executor/types/Type;', (10,)), # invoke-virtual {v10}, Lpbi/executor/exceptions/PyException;->__type__()Lpbi/executor/types/Type;
     (12, 16),                                    # move-result-object v16
     (98, 17, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v17, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (8, 1, 17),                                  # move-object/from16 v1, v17
     (110, 'Lpbi/executor/types/Base;->__exit__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0, 10, 1)), # invoke-virtual {v13, v0, v10, v1}, Lpbi/executor/types/Base;->__exit__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (110, 'Lpbi/executor/types/Base;->__bool()Z', (13,)), # invoke-virtual {v13}, Lpbi/executor/types/Base;->__bool()Z
     (10, 13),                                    # move-result v13
     (57, 13, 2696, ':cond_a88'),                 # if-nez v13, :cond_a88
     (84, (10, 10), 'Lpbi/executor/exceptions/PyException;->err:Lpbi/executor/exceptions/RuntimeError;'), # iget-object v10, v10, Lpbi/executor/exceptions/PyException;->err:Lpbi/executor/exceptions/RuntimeError;
     (39, 10),                                    # throw v10
                                                  # :cond_548
     (70, 10, 21, 12),                            # aget-object v10, v21, v12
     (98, 13, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v13, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (98, 16, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v16, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (98, 17, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v17, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (8, 1, 17),                                  # move-object/from16 v1, v17
     (110, 'Lpbi/executor/types/Base;->__exit__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (10, 13, 0, 1)), # invoke-virtual {v10, v13, v0, v1}, Lpbi/executor/types/Base;->__exit__(Lpbi/executor/types/Base;Lpbi/executor/types/Base;Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_55a  #0x38
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 10, 21, 12),                            # aget-object v10, v21, v12
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (31, 10, 'Lpbi/executor/types/pSet;'),       # check-cast v10, Lpbi/executor/types/pSet;
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (110, 'Lpbi/executor/types/pSet;->add(Lpbi/executor/types/Base;)Lpbi/executor/types/NoneType;', (10, 13)), # invoke-virtual {v10, v13}, Lpbi/executor/types/pSet;->add(Lpbi/executor/types/Base;)Lpbi/executor/types/NoneType;
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_56a  #0x39
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (77, 11, 21, 10),                            # aput-object v11, v21, v10
     (98, 11, 'Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;'), # sget-object v11, Lpbi/executor/Main;->None:Lpbi/executor/types/NoneType;
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_573  #0x3a
     (68, 10, 23, 19),                            # aget v10, v23, v19
                                                  # :try_start_575
                                                  # :try_end_575
                                                  # .catch Ljava/lang/Throwable; {:try_start_523 .. :try_end_575} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__bool()Z', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__bool()Z
     (10, 12),                                    # move-result v12
     (56, 12, 160, ':cond_a0'),                   # if-eqz v12, :cond_a0
     (68, 12, 24, 19),                            # aget v12, v24, v19
                                                  # :try_end_57f
                                                  # .catch Ljava/lang/Throwable; {:try_start_575 .. :try_end_57f} :catch_c7
     (144, 12, 12, 19),                           # add-int v12, v12, v19
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :pswitch_586  #0x3b
                                                  # :try_start_586
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (34, 13, 'Lpbi/executor/types/JavaWrap;'),   # new-instance v13, Lpbi/executor/types/JavaWrap;
     (70, 16, 7, 19),                             # aget-object v16, v7, v19
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (112, 'Lpbi/executor/types/JavaWrap;-><init>(Lpbi/executor/types/Base;)V', (13, 0)), # invoke-direct {v13, v0}, Lpbi/executor/types/JavaWrap;-><init>(Lpbi/executor/types/Base;)V
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (8, 1, 33),                                  # move-object/from16 v1, p1
     (110, 'Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V', (0, 1, 10, 13)), # invoke-virtual {v0, v1, v10, v13}, Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_59b  #0x3c
     (68, 10, 23, 19),                            # aget v10, v23, v19
     (68, 13, 24, 19),                            # aget v13, v24, v19
     (70, 13, 21, 13),                            # aget-object v13, v21, v13
     (77, 13, 21, 10),                            # aput-object v13, v21, v10
     (57, 13, 2696, ':cond_a88'),                 # if-nez v13, :cond_a88
     (34, 10, 'Lpbi/executor/exceptions/NameError;'), # new-instance v10, Lpbi/executor/exceptions/NameError;
     (34, 11, 'Ljava/lang/StringBuilder;'),       # new-instance v11, Ljava/lang/StringBuilder;
     (26, 13, "name 'regs:"),                     # const-string v13, "name 'regs:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (11, 13)), # invoke-direct {v11, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (68, 13, 24, 19),                            # aget v13, v24, v19
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (11,)), # invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 11),                                    # move-result-object v11
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :pswitch_5c2  #0x3e
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (84, (10, 0), 'Lpbi/executor/Main;->globals:[Lpbi/executor/types/Base;'), # iget-object v10, v0, Lpbi/executor/Main;->globals:[Lpbi/executor/types/Base;
     (68, 13, 24, 19),                            # aget v13, v24, v19
     (70, 10, 10, 13),                            # aget-object v10, v10, v13
     (57, 10, 1513, ':cond_5e9'),                 # if-nez v10, :cond_5e9
     (34, 10, 'Lpbi/executor/exceptions/NameError;'), # new-instance v10, Lpbi/executor/exceptions/NameError;
     (34, 11, 'Ljava/lang/StringBuilder;'),       # new-instance v11, Ljava/lang/StringBuilder;
     (26, 13, "name 'globals:"),                  # const-string v13, "name 'globals:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (11, 13)), # invoke-direct {v11, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (68, 13, 24, 19),                            # aget v13, v24, v19
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (11,)), # invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 11),                                    # move-result-object v11
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :cond_5e9
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (77, 10, 21, 13),                            # aput-object v10, v21, v13
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_5f0  #0x40
     (68, 10, 24, 19),                            # aget v10, v24, v19
     (113, 'Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;', (10,)), # invoke-static {v10}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
     (12, 10),                                    # move-result-object v10
     (8, 0, 22),                                  # move-object/from16 v0, v22
     (114, 'Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;', (0, 10)), # invoke-interface {v0, v10}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;
     (12, 10),                                    # move-result-object v10
     (31, 10, '[Lpbi/executor/types/Base;'),      # check-cast v10, [Lpbi/executor/types/Base;
     (68, 13, 25, 19),                            # aget v13, v25, v19
     (70, 10, 10, 13),                            # aget-object v10, v10, v13
     (57, 10, 1581, ':cond_62d'),                 # if-nez v10, :cond_62d
     (34, 10, 'Lpbi/executor/exceptions/NameError;'), # new-instance v10, Lpbi/executor/exceptions/NameError;
     (34, 11, 'Ljava/lang/StringBuilder;'),       # new-instance v11, Ljava/lang/StringBuilder;
     (26, 13, "name 'scope:"),                    # const-string v13, "name 'scope:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (11, 13)), # invoke-direct {v11, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (68, 13, 24, 19),                            # aget v13, v24, v19
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, ':'),                               # const-string v13, ":"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (68, 13, 25, 19),                            # aget v13, v25, v19
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (11,)), # invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 11),                                    # move-result-object v11
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :cond_62d
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (77, 10, 21, 13),                            # aput-object v10, v21, v13
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_634  #0x41
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_636
                                                  # :try_start_636
                                                  # .catch Ljava/lang/Throwable; {:try_start_586 .. :try_end_636} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;
                                                  # :try_end_63b
                                                  # .catch Lpbi/executor/exceptions/StopIteration; {:try_start_636 .. :try_end_63b} :catch_665
                                                  # .catch Ljava/lang/Throwable; {:try_start_636 .. :try_end_63b} :catch_c7
     (12, 12),                                    # move-result-object v12
                                                  # :try_start_63c
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (77, 12, 21, 13),                            # aput-object v12, v21, v13
     (110, 'Lpbi/executor/types/Base;->__len()I', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__len()I
     (10, 12),                                    # move-result v12
     (68, 13, 24, 19),                            # aget v13, v24, v19
     (55, (12, 13), 1650, ':cond_672'),           # if-le v12, v13, :cond_672
     (34, 11, 'Lpbi/executor/exceptions/ValueError;'), # new-instance v11, Lpbi/executor/exceptions/ValueError;
     (34, 12, 'Ljava/lang/StringBuilder;'),       # new-instance v12, Ljava/lang/StringBuilder;
     (26, 16, 'too many values to unpack (expected '), # const-string v16, "too many values to unpack (expected "
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (12, 0)), # invoke-direct {v12, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (26, 13, ')'),                               # const-string v13, ")"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (12,)), # invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (112, 'Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V', (11, 12)), # invoke-direct {v11, v12}, Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V
     (39, 11),                                    # throw v11
                                                  # :catch_665
     (13, 12),                                    # move-exception v12
     (70, 12, 8, 19),                             # aget-object v12, v8, v19
     (18, 13, 0),                                 # const/4 v13, 0x0
     (68, 12, 12, 13),                            # aget v12, v12, v13
     (144, 12, 12, 19),                           # add-int v12, v12, v19
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :cond_672
     (53, (12, 13), 160, ':cond_a0'),             # if-ge v12, v13, :cond_a0
     (34, 11, 'Lpbi/executor/exceptions/ValueError;'), # new-instance v11, Lpbi/executor/exceptions/ValueError;
     (34, 16, 'Ljava/lang/StringBuilder;'),       # new-instance v16, Ljava/lang/StringBuilder;
     (26, 17, 'not enough values to unpack (expected '), # const-string v17, "not enough values to unpack (expected "
     (118, 16, 17, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V'), # invoke-direct/range {v16 .. v17}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (0, 13)), # invoke-virtual {v0, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 13),                                    # move-result-object v13
     (26, 16, ', got '),                          # const-string v16, ", got "
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (13, 0)), # invoke-virtual {v13, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 13),                                    # move-result-object v13
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (13, 12)), # invoke-virtual {v13, v12}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (26, 13, ')'),                               # const-string v13, ")"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (12, 13)), # invoke-virtual {v12, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 12),                                    # move-result-object v12
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (12,)), # invoke-virtual {v12}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (112, 'Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V', (11, 12)), # invoke-direct {v11, v12}, Lpbi/executor/exceptions/ValueError;-><init>(Ljava/lang/String;)V
     (39, 11),                                    # throw v11
                                                  # :pswitch_69d  #0x42
                                                  # :try_start_69d
                                                  # :try_end_69d
                                                  # .catch Ljava/lang/Throwable; {:try_start_63c .. :try_end_69d} :catch_c7
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_69f
                                                  # :try_end_69f
                                                  # .catch Ljava/lang/Throwable; {:try_start_69d .. :try_end_69f} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (68, 16, 25, 19),                            # aget v16, v25, v19
     (2, 0, 16),                                  # move/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__getitem__(I)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__getitem__(I)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (8, 1, 33),                                  # move-object/from16 v1, p1
     (110, 'Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V', (0, 1, 12, 13)), # invoke-virtual {v0, v1, v12, v13}, Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V
                                                  # :try_end_6b2
                                                  # .catch Ljava/lang/Throwable; {:try_start_69f .. :try_end_6b2} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_6b4  #0x43
                                                  # :try_start_6b4
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_6b6
                                                  # :try_start_6b6
                                                  # .catch Ljava/lang/Throwable; {:try_start_6b4 .. :try_end_6b6} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__next__()Lpbi/executor/types/Base;
                                                  # :try_end_6bb
                                                  # .catch Ljava/lang/Throwable; {:try_start_6b6 .. :try_end_6bb} :catch_c7
                                                  # .catch Lpbi/executor/exceptions/StopIteration; {:try_start_6b6 .. :try_end_6bb} :catch_6c7
     (12, 12),                                    # move-result-object v12
                                                  # :try_start_6bc
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (8, 0, 32),                                  # move-object/from16 v0, p0
     (8, 1, 33),                                  # move-object/from16 v1, p1
     (110, 'Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V', (0, 1, 13, 12)), # invoke-virtual {v0, v1, v13, v12}, Lpbi/executor/Main;->set_var(Lpbi/executor/RegLocs;ILpbi/executor/types/Base;)V
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :catch_6c7
     (13, 12),                                    # move-exception v12
     (68, 12, 25, 19),                            # aget v12, v25, v19
                                                  # :try_end_6ca
                                                  # .catch Ljava/lang/Throwable; {:try_start_6bc .. :try_end_6ca} :catch_c7
     (144, 12, 12, 19),                           # add-int v12, v12, v19
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :try_start_6d1
                                                  # :pswitch_6d1  #0x44
     (70, 17, 9, 19),                             # aget-object v17, v9, v19
     (8, 0, 17),                                  # move-object/from16 v0, v17
     (33, 0, 0),                                  # array-length v0, v0
     (2, 18, 0),                                  # move/from16 v18, v0
     (34, 27, 'Ljava/util/ArrayList;'),           # new-instance v27, Ljava/util/ArrayList;
     (118, 27, 27, 'Ljava/util/ArrayList;-><init>()V'), # invoke-direct/range {v27 .. v27}, Ljava/util/ArrayList;-><init>()V
     (34, 28, 'Ljava/util/HashMap;'),             # new-instance v28, Ljava/util/HashMap;
     (118, 28, 28, 'Ljava/util/HashMap;-><init>()V'), # invoke-direct/range {v28 .. v28}, Ljava/util/HashMap;-><init>()V
     (18, 10, 0),                                 # const/4 v10, 0x0
     (2, 16, 10),                                 # move/from16 v16, v10
                                                  # :goto_6e5
     (2, 0, 16),                                  # move/from16 v0, v16
     (2, 1, 18),                                  # move/from16 v1, v18
     (52, (0, 1), 1806, ':cond_70e'),             # if-lt v0, v1, :cond_70e
     (116, 27, 27, 'Ljava/util/ArrayList;->size()I'), # invoke-virtual/range {v27 .. v27}, Ljava/util/ArrayList;->size()I
     (10, 10),                                    # move-result v10
     (35, (13, 10), '[Lpbi/executor/types/Base;'), # new-array v13, v10, [Lpbi/executor/types/Base;
     (8, 0, 27),                                  # move-object/from16 v0, v27
     (110, 'Ljava/util/ArrayList;->toArray([Ljava/lang/Object;)[Ljava/lang/Object;', (0, 13)), # invoke-virtual {v0, v13}, Ljava/util/ArrayList;->toArray([Ljava/lang/Object;)[Ljava/lang/Object;
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_6f8
                                                  # :try_start_6f8
                                                  # .catch Ljava/lang/Throwable; {:try_start_6d1 .. :try_end_6f8} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (8, 1, 28),                                  # move-object/from16 v1, v28
     (110, 'Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;', (0, 13, 1)), # invoke-virtual {v0, v13, v1}, Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
     (2, 0, 20),                                  # move/from16 v0, v20
     (8, 1, 32),                                  # move-object/from16 v1, p0
     (89, (0, 1), 'Lpbi/executor/Main;->last_method:I'), # iput v0, v1, Lpbi/executor/Main;->last_method:I
                                                  # :try_end_70c
                                                  # .catch Ljava/lang/Throwable; {:try_start_6f8 .. :try_end_70c} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_70e
                                                  # :cond_70e
     (70, 10, 17, 16),                            # aget-object v10, v17, v16
     (18, 13, 0),                                 # const/4 v13, 0x0
     (68, 29, 10, 13),                            # aget v29, v10, v13
     (18, 13, 1),                                 # const/4 v13, 0x1
     (68, 13, 10, 13),                            # aget v13, v10, v13
                                                  # :try_start_716
                                                  # :try_end_716
                                                  # .catch Ljava/lang/Throwable; {:try_start_70e .. :try_end_716} :catch_7e
     (70, 10, 21, 13),                            # aget-object v10, v21, v13
     (43, 29, 2902, ':pswitch_data_b56'),         # packed-switch v29 :pswitch_data_b56
     (216, (12, 29), -3),                         # add-int/lit8 v12, v29, -0x3
     (113, 'Ljava/lang/String;->valueOf(I)Ljava/lang/String;', (12,)), # invoke-static {v12}, Ljava/lang/String;->valueOf(I)Ljava/lang/String;
     (12, 12),                                    # move-result-object v12
     (8, 0, 28),                                  # move-object/from16 v0, v28
     (114, 'Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;', (0, 12, 10)), # invoke-interface {v0, v12, v10}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
                                                  # :goto_726
                                                  # :cond_726
     (216, (10, 16), 1),                          # add-int/lit8 v10, v16, 0x1
     (2, 16, 10),                                 # move/from16 v16, v10
     (1, 12, 13),                                 # move v12, v13
     (40, 1765, ':goto_6e5'),                     # goto :goto_6e5
                                                  # :pswitch_72c  #0x0
     (8, 0, 27),                                  # move-object/from16 v0, v27
     (110, 'Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', (0, 10)), # invoke-virtual {v0, v10}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
     (40, 1830, ':goto_726'),                     # goto :goto_726
                                                  # :catch_732
     (13, 10),                                    # move-exception v10
     (1, 12, 13),                                 # move v12, v13
     (41, 127, ':goto_7f'),                       # goto/16 :goto_7f
                                                  # :pswitch_736  #0x1
     (110, 'Lpbi/executor/types/Base;->iterator()Ljava/util/Iterator;', (10,)), # invoke-virtual {v10}, Lpbi/executor/types/Base;->iterator()Ljava/util/Iterator;
     (12, 12),                                    # move-result-object v12
                                                  # :goto_73a
     (114, 'Ljava/util/Iterator;->hasNext()Z', (12,)), # invoke-interface {v12}, Ljava/util/Iterator;->hasNext()Z
     (10, 10),                                    # move-result v10
     (56, 10, 1830, ':cond_726'),                 # if-eqz v10, :cond_726
     (114, 'Ljava/util/Iterator;->next()Ljava/lang/Object;', (12,)), # invoke-interface {v12}, Ljava/util/Iterator;->next()Ljava/lang/Object;
     (12, 10),                                    # move-result-object v10
     (31, 10, 'Lpbi/executor/types/Base;'),       # check-cast v10, Lpbi/executor/types/Base;
     (8, 0, 27),                                  # move-object/from16 v0, v27
     (110, 'Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', (0, 10)), # invoke-virtual {v0, v10}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
     (40, 1850, ':goto_73a'),                     # goto :goto_73a
                                                  # :pswitch_74c  #0x2
     (110, 'Lpbi/executor/types/Base;->__dict()Lpbi/executor/types/Dict;', (10,)), # invoke-virtual {v10}, Lpbi/executor/types/Base;->__dict()Lpbi/executor/types/Dict;
     (12, 10),                                    # move-result-object v10
     (110, 'Lpbi/executor/types/Dict;->get_dict()Ljava/util/Map;', (10,)), # invoke-virtual {v10}, Lpbi/executor/types/Dict;->get_dict()Ljava/util/Map;
     (12, 10),                                    # move-result-object v10
     (114, 'Ljava/util/Map;->entrySet()Ljava/util/Set;', (10,)), # invoke-interface {v10}, Ljava/util/Map;->entrySet()Ljava/util/Set;
     (12, 10),                                    # move-result-object v10
     (114, 'Ljava/util/Set;->iterator()Ljava/util/Iterator;', (10,)), # invoke-interface {v10}, Ljava/util/Set;->iterator()Ljava/util/Iterator;
     (12, 29),                                    # move-result-object v29
                                                  # :goto_75c
     (120, 29, 29, 'Ljava/util/Iterator;->hasNext()Z'), # invoke-interface/range {v29 .. v29}, Ljava/util/Iterator;->hasNext()Z
     (10, 10),                                    # move-result v10
     (56, 10, 1830, ':cond_726'),                 # if-eqz v10, :cond_726
     (120, 29, 29, 'Ljava/util/Iterator;->next()Ljava/lang/Object;'), # invoke-interface/range {v29 .. v29}, Ljava/util/Iterator;->next()Ljava/lang/Object;
     (12, 10),                                    # move-result-object v10
     (31, 10, 'Ljava/util/Map$Entry;'),           # check-cast v10, Ljava/util/Map$Entry;
     (114, 'Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;', (10,)), # invoke-interface {v10}, Ljava/util/Map$Entry;->getKey()Ljava/lang/Object;
     (12, 12),                                    # move-result-object v12
     (31, 12, 'Lpbi/executor/types/Base;'),       # check-cast v12, Lpbi/executor/types/Base;
     (32, (0, 12), 'Lpbi/executor/types/pString;'), # instance-of v0, v12, Lpbi/executor/types/pString;
     (2, 30, 0),                                  # move/from16 v30, v0
     (57, 30, 1916, ':cond_77c'),                 # if-nez v30, :cond_77c
     (34, 10, 'Lpbi/executor/exceptions/TypeError;'), # new-instance v10, Lpbi/executor/exceptions/TypeError;
     (26, 11, 'keywords must be strings'),        # const-string v11, "keywords must be strings"
     (112, 'Lpbi/executor/exceptions/TypeError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/TypeError;-><init>(Ljava/lang/String;)V
     (39, 10),                                    # throw v10
                                                  # :cond_77c
     (31, 12, 'Lpbi/executor/types/pString;'),    # check-cast v12, Lpbi/executor/types/pString;
     (84, (12, 12), 'Lpbi/executor/types/pString;->str:Ljava/lang/String;'), # iget-object v12, v12, Lpbi/executor/types/pString;->str:Ljava/lang/String;
     (114, 'Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;', (10,)), # invoke-interface {v10}, Ljava/util/Map$Entry;->getValue()Ljava/lang/Object;
     (12, 10),                                    # move-result-object v10
     (31, 10, 'Lpbi/executor/types/Base;'),       # check-cast v10, Lpbi/executor/types/Base;
     (8, 0, 28),                                  # move-object/from16 v0, v28
     (114, 'Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;', (0, 12, 10)), # invoke-interface {v0, v12, v10}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
                                                  # :try_end_78b
                                                  # .catch Ljava/lang/Throwable; {:try_start_716 .. :try_end_78b} :catch_732
     (40, 1884, ':goto_75c'),                     # goto :goto_75c
                                                  # :try_start_78c
                                                  # :pswitch_78c  #0x45
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_78e
                                                  # :try_start_78e
                                                  # .catch Ljava/lang/Throwable; {:try_start_78c .. :try_end_78e} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (110, 'Lpbi/executor/types/Base;->__iter__()Lpbi/executor/types/Base;', (13,)), # invoke-virtual {v13}, Lpbi/executor/types/Base;->__iter__()Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_798
                                                  # .catch Ljava/lang/Throwable; {:try_start_78e .. :try_end_798} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_79a  #0x46
                                                  # :try_start_79a
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_79c
                                                  # :try_start_79c
                                                  # .catch Ljava/lang/Throwable; {:try_start_79a .. :try_end_79c} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (34, 13, 'Lpbi/executor/types/Tuple;'),      # new-instance v13, Lpbi/executor/types/Tuple;
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (112, 'Lpbi/executor/types/Tuple;-><init>(Lpbi/executor/types/Base;)V', (13, 0)), # invoke-direct {v13, v0}, Lpbi/executor/types/Tuple;-><init>(Lpbi/executor/types/Base;)V
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_7a9
                                                  # .catch Ljava/lang/Throwable; {:try_start_79c .. :try_end_7a9} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_7ab  #0x47
                                                  # :try_start_7ab
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_7b1
                                                  # :try_start_7b1
                                                  # .catch Ljava/lang/Throwable; {:try_start_7ab .. :try_end_7b1} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__add__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__add__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_7bd
                                                  # .catch Ljava/lang/Throwable; {:try_start_7b1 .. :try_end_7bd} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_7bf  #0x48
                                                  # :try_start_7bf
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_7c5
                                                  # :try_start_7c5
                                                  # .catch Ljava/lang/Throwable; {:try_start_7bf .. :try_end_7c5} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__sub__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__sub__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_7d1
                                                  # .catch Ljava/lang/Throwable; {:try_start_7c5 .. :try_end_7d1} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_7d3  #0x49
                                                  # :try_start_7d3
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_start_7d9
                                                  # :try_end_7d9
                                                  # .catch Ljava/lang/Throwable; {:try_start_7d3 .. :try_end_7d9} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__mul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__mul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_7e5
                                                  # .catch Ljava/lang/Throwable; {:try_start_7d9 .. :try_end_7e5} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_7e7  #0x4a
                                                  # :try_start_7e7
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_7ed
                                                  # :try_start_7ed
                                                  # .catch Ljava/lang/Throwable; {:try_start_7e7 .. :try_end_7ed} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__matmul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__matmul__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_7f9
                                                  # .catch Ljava/lang/Throwable; {:try_start_7ed .. :try_end_7f9} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_7fb  #0x4b
                                                  # :try_start_7fb
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_start_801
                                                  # :try_end_801
                                                  # .catch Ljava/lang/Throwable; {:try_start_7fb .. :try_end_801} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__truediv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__truediv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_80d
                                                  # .catch Ljava/lang/Throwable; {:try_start_801 .. :try_end_80d} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_80f  #0x4c
                                                  # :try_start_80f
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_815
                                                  # :try_start_815
                                                  # .catch Ljava/lang/Throwable; {:try_start_80f .. :try_end_815} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__mod__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__mod__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_821
                                                  # .catch Ljava/lang/Throwable; {:try_start_815 .. :try_end_821} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_823
                                                  # :pswitch_823  #0x4d
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_829
                                                  # :try_start_829
                                                  # .catch Ljava/lang/Throwable; {:try_start_823 .. :try_end_829} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__and__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__and__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_835
                                                  # .catch Ljava/lang/Throwable; {:try_start_829 .. :try_end_835} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_837  #0x4e
                                                  # :try_start_837
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_83d
                                                  # :try_start_83d
                                                  # .catch Ljava/lang/Throwable; {:try_start_837 .. :try_end_83d} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__or__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__or__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_849
                                                  # .catch Ljava/lang/Throwable; {:try_start_83d .. :try_end_849} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_84b  #0x4f
                                                  # :try_start_84b
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_851
                                                  # :try_start_851
                                                  # .catch Ljava/lang/Throwable; {:try_start_84b .. :try_end_851} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__xor__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__xor__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_85d
                                                  # .catch Ljava/lang/Throwable; {:try_start_851 .. :try_end_85d} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_85f
                                                  # :pswitch_85f  #0x50
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_865
                                                  # :try_start_865
                                                  # .catch Ljava/lang/Throwable; {:try_start_85f .. :try_end_865} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__lshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__lshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_871
                                                  # .catch Ljava/lang/Throwable; {:try_start_865 .. :try_end_871} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_873  #0x51
                                                  # :try_start_873
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_879
                                                  # :try_start_879
                                                  # .catch Ljava/lang/Throwable; {:try_start_873 .. :try_end_879} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__rshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__rshift__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_885
                                                  # .catch Ljava/lang/Throwable; {:try_start_879 .. :try_end_885} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_887  #0x52
                                                  # :try_start_887
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_88d
                                                  # :try_start_88d
                                                  # .catch Ljava/lang/Throwable; {:try_start_887 .. :try_end_88d} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__pow__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__pow__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_899
                                                  # .catch Ljava/lang/Throwable; {:try_start_88d .. :try_end_899} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_89b
                                                  # :pswitch_89b  #0x53
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_8a1
                                                  # :try_start_8a1
                                                  # .catch Ljava/lang/Throwable; {:try_start_89b .. :try_end_8a1} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__floordiv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__floordiv__(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_8ad
                                                  # .catch Ljava/lang/Throwable; {:try_start_8a1 .. :try_end_8ad} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_8af  #0x54
                                                  # :try_start_8af
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_8b5
                                                  # :try_start_8b5
                                                  # .catch Ljava/lang/Throwable; {:try_start_8af .. :try_end_8b5} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__lt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__lt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_8c1
                                                  # .catch Ljava/lang/Throwable; {:try_start_8b5 .. :try_end_8c1} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_8c3  #0x55
                                                  # :try_start_8c3
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_start_8c9
                                                  # :try_end_8c9
                                                  # .catch Ljava/lang/Throwable; {:try_start_8c3 .. :try_end_8c9} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__gt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__gt(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_8d5
                                                  # .catch Ljava/lang/Throwable; {:try_start_8c9 .. :try_end_8d5} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_8d7  #0x56
                                                  # :try_start_8d7
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_start_8dd
                                                  # :try_end_8dd
                                                  # .catch Ljava/lang/Throwable; {:try_start_8d7 .. :try_end_8dd} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__eq(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__eq(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_8e9
                                                  # .catch Ljava/lang/Throwable; {:try_start_8dd .. :try_end_8e9} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_8eb
                                                  # :pswitch_8eb  #0x57
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_8f1
                                                  # :try_start_8f1
                                                  # .catch Ljava/lang/Throwable; {:try_start_8eb .. :try_end_8f1} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__ge(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__ge(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_8fd
                                                  # .catch Ljava/lang/Throwable; {:try_start_8f1 .. :try_end_8fd} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_8ff
                                                  # :pswitch_8ff  #0x58
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_905
                                                  # :try_start_905
                                                  # .catch Ljava/lang/Throwable; {:try_start_8ff .. :try_end_905} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__le(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__le(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_911
                                                  # .catch Ljava/lang/Throwable; {:try_start_905 .. :try_end_911} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_913  #0x59
                                                  # :try_start_913
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_919
                                                  # :try_start_919
                                                  # .catch Ljava/lang/Throwable; {:try_start_913 .. :try_end_919} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__ne(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;', (13, 0)), # invoke-virtual {v13, v0}, Lpbi/executor/types/Base;->__ne(Lpbi/executor/types/Base;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_925
                                                  # .catch Ljava/lang/Throwable; {:try_start_919 .. :try_end_925} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_927
                                                  # :pswitch_927  #0x5a
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_92d
                                                  # :try_start_92d
                                                  # .catch Ljava/lang/Throwable; {:try_start_927 .. :try_end_92d} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 16, 21, 10),                            # aget-object v16, v21, v10
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (110, 'Lpbi/executor/types/Base;->__contains__(Lpbi/executor/types/Base;)Lpbi/executor/types/pBoolean;', (0, 13)), # invoke-virtual {v0, v13}, Lpbi/executor/types/Base;->__contains__(Lpbi/executor/types/Base;)Lpbi/executor/types/pBoolean;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_939
                                                  # .catch Ljava/lang/Throwable; {:try_start_92d .. :try_end_939} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_93b
                                                  # :pswitch_93b  #0x5b
     (68, 12, 24, 19),                            # aget v12, v24, v19
     (70, 13, 21, 12),                            # aget-object v13, v21, v12
     (68, 10, 25, 19),                            # aget v10, v25, v19
                                                  # :try_end_941
                                                  # :try_start_941
                                                  # .catch Ljava/lang/Throwable; {:try_start_93b .. :try_end_941} :catch_7e
     (68, 16, 23, 19),                            # aget v16, v23, v19
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (51, (13, 12), 2380, ':cond_94c'),           # if-ne v13, v12, :cond_94c
     (7, 12, 15),                                 # move-object v12, v15
                                                  # :goto_948
     (77, 12, 21, 16),                            # aput-object v12, v21, v16
                                                  # :try_end_94a
                                                  # .catch Ljava/lang/Throwable; {:try_start_941 .. :try_end_94a} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_94c
     (7, 12, 14),                                 # move-object v12, v14
     (40, 2376, ':goto_948'),                     # goto :goto_948
                                                  # :try_start_94e
                                                  # :pswitch_94e  #0x5c
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_950
                                                  # :try_end_950
                                                  # .catch Ljava/lang/Throwable; {:try_start_94e .. :try_end_950} :catch_7e
     (68, 13, 23, 19),                            # aget v13, v23, v19
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Lpbi/executor/types/Base;->__bool()Z', (12,)), # invoke-virtual {v12}, Lpbi/executor/types/Base;->__bool()Z
     (10, 12),                                    # move-result v12
     (56, 12, 2399, ':cond_95f'),                 # if-eqz v12, :cond_95f
     (7, 12, 14),                                 # move-object v12, v14
                                                  # :goto_95b
     (77, 12, 21, 13),                            # aput-object v12, v21, v13
                                                  # :try_end_95d
                                                  # .catch Ljava/lang/Throwable; {:try_start_950 .. :try_end_95d} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_95f
     (7, 12, 15),                                 # move-object v12, v15
     (40, 2395, ':goto_95b'),                     # goto :goto_95b
                                                  # :pswitch_961  #0x5d
                                                  # :try_start_961
     (70, 13, 8, 19),                             # aget-object v13, v8, v19
     (33, 0, 13),                                 # array-length v0, v13
     (2, 16, 0),                                  # move/from16 v16, v0
     (2, 0, 16),                                  # move/from16 v0, v16
     (35, (0, 0), '[Lpbi/executor/types/Base;'),  # new-array v0, v0, [Lpbi/executor/types/Base;
     (8, 17, 0),                                  # move-object/from16 v17, v0
     (18, 10, 0),                                 # const/4 v10, 0x0
                                                  # :goto_96d
     (2, 0, 16),                                  # move/from16 v0, v16
     (52, (10, 0), 2441, ':cond_989'),            # if-lt v10, v0, :cond_989
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_973
                                                  # :try_start_973
                                                  # .catch Ljava/lang/Throwable; {:try_start_961 .. :try_end_973} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (8, 0, 17),                                  # move-object/from16 v0, v17
     (8, 1, 26),                                  # move-object/from16 v1, v26
     (110, 'Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;', (13, 0, 1)), # invoke-virtual {v13, v0, v1}, Lpbi/executor/types/Base;->__call__([Lpbi/executor/types/Base;Ljava/util/Map;)Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
     (2, 0, 20),                                  # move/from16 v0, v20
     (8, 1, 32),                                  # move-object/from16 v1, p0
     (89, (0, 1), 'Lpbi/executor/Main;->last_method:I'), # iput v0, v1, Lpbi/executor/Main;->last_method:I
                                                  # :try_end_987
                                                  # .catch Ljava/lang/Throwable; {:try_start_973 .. :try_end_987} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_989
                                                  # :try_start_989
     (68, 12, 13, 10),                            # aget v12, v13, v10
     (70, 18, 21, 12),                            # aget-object v18, v21, v12
     (77, 18, 17, 10),                            # aput-object v18, v17, v10
     (216, (10, 10), 1),                          # add-int/lit8 v10, v10, 0x1
     (40, 2413, ':goto_96d'),                     # goto :goto_96d
                                                  # :pswitch_992  #0x5e
     (34, 13, 'Ljava/util/ArrayList;'),           # new-instance v13, Ljava/util/ArrayList;
     (112, 'Ljava/util/ArrayList;-><init>()V', (13,)), # invoke-direct {v13}, Ljava/util/ArrayList;-><init>()V
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_end_999
                                                  # :try_start_999
                                                  # .catch Ljava/lang/Throwable; {:try_start_989 .. :try_end_999} :catch_7e
     (70, 12, 21, 10),                            # aget-object v12, v21, v10
     (110, 'Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z', (13, 12)), # invoke-virtual {v13, v12}, Ljava/util/ArrayList;->add(Ljava/lang/Object;)Z
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (34, 16, 'Lpbi/executor/types/List;'),       # new-instance v16, Lpbi/executor/types/List;
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (112, 'Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V', (0, 13)), # invoke-direct {v0, v13}, Lpbi/executor/types/List;-><init>(Ljava/util/ArrayList;)V
     (77, 16, 21, 12),                            # aput-object v16, v21, v12
                                                  # :try_end_9a9
                                                  # .catch Ljava/lang/Throwable; {:try_start_999 .. :try_end_9a9} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_9ab  #0x5f
                                                  # :try_start_9ab
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_9ad
                                                  # :try_end_9ad
                                                  # .catch Ljava/lang/Throwable; {:try_start_9ab .. :try_end_9ad} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (110, 'Lpbi/executor/types/Base;->__pos__()Lpbi/executor/types/Base;', (13,)), # invoke-virtual {v13}, Lpbi/executor/types/Base;->__pos__()Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_9b7
                                                  # .catch Ljava/lang/Throwable; {:try_start_9ad .. :try_end_9b7} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :try_start_9b9
                                                  # :pswitch_9b9  #0x60
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_9bb
                                                  # :try_end_9bb
                                                  # .catch Ljava/lang/Throwable; {:try_start_9b9 .. :try_end_9bb} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (110, 'Lpbi/executor/types/Base;->__neg__()Lpbi/executor/types/Base;', (13,)), # invoke-virtual {v13}, Lpbi/executor/types/Base;->__neg__()Lpbi/executor/types/Base;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_9c5
                                                  # .catch Ljava/lang/Throwable; {:try_start_9bb .. :try_end_9c5} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :pswitch_9c7  #0x61
                                                  # :try_start_9c7
     (68, 10, 24, 19),                            # aget v10, v24, v19
                                                  # :try_start_9c9
                                                  # :try_end_9c9
                                                  # .catch Ljava/lang/Throwable; {:try_start_9c7 .. :try_end_9c9} :catch_7e
     (68, 12, 23, 19),                            # aget v12, v23, v19
     (70, 13, 21, 10),                            # aget-object v13, v21, v10
     (110, 'Lpbi/executor/types/Base;->__invert__()Lpbi/executor/types/BigInt;', (13,)), # invoke-virtual {v13}, Lpbi/executor/types/Base;->__invert__()Lpbi/executor/types/BigInt;
     (12, 13),                                    # move-result-object v13
     (77, 13, 21, 12),                            # aput-object v13, v21, v12
                                                  # :try_end_9d3
                                                  # .catch Ljava/lang/Throwable; {:try_start_9c9 .. :try_end_9d3} :catch_c7
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_9d5
     (32, (11, 10), 'Ljava/lang/NullPointerException;'), # instance-of v11, v10, Ljava/lang/NullPointerException;
     (56, 11, 2550, ':cond_9f6'),                 # if-eqz v11, :cond_9f6
     (34, 10, 'Lpbi/executor/exceptions/NameError;'), # new-instance v10, Lpbi/executor/exceptions/NameError;
     (34, 11, 'Ljava/lang/StringBuilder;'),       # new-instance v11, Ljava/lang/StringBuilder;
     (26, 13, "name 'regs:"),                     # const-string v13, "name 'regs:"
     (112, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V', (11, 13)), # invoke-direct {v11, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (11, 12)), # invoke-virtual {v11, v12}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (26, 13, "' is not defined"),                # const-string v13, "' is not defined"
     (110, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;', (11, 13)), # invoke-virtual {v11, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 11),                                    # move-result-object v11
     (110, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;', (11,)), # invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 11),                                    # move-result-object v11
     (112, 'Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V', (10, 11)), # invoke-direct {v10, v11}, Lpbi/executor/exceptions/NameError;-><init>(Ljava/lang/String;)V
     (7, 11, 10),                                 # move-object v11, v10
     (41, 134, ':goto_86'),                       # goto/16 :goto_86
                                                  # :cond_9f6
     (32, (11, 10), 'Ljava/lang/StackOverflowError;'), # instance-of v11, v10, Ljava/lang/StackOverflowError;
     (56, 11, 2565, ':cond_a05'),                 # if-eqz v11, :cond_a05
     (34, 11, 'Lpbi/executor/exceptions/RecursionError;'), # new-instance v11, Lpbi/executor/exceptions/RecursionError;
     (110, 'Ljava/lang/Throwable;->getMessage()Ljava/lang/String;', (10,)), # invoke-virtual {v10}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;
     (12, 10),                                    # move-result-object v10
     (112, 'Lpbi/executor/exceptions/RecursionError;-><init>(Ljava/lang/String;)V', (11, 10)), # invoke-direct {v11, v10}, Lpbi/executor/exceptions/RecursionError;-><init>(Ljava/lang/String;)V
     (41, 134, ':goto_86'),                       # goto/16 :goto_86
                                                  # :cond_a05
     (18, 11, 2),                                 # const/4 v11, 0x2
     (35, (11, 11), '[Ljava/lang/Object;'),       # new-array v11, v11, [Ljava/lang/Object;
     (18, 13, 0),                                 # const/4 v13, 0x0
     (34, 16, 'Ljava/lang/StringBuilder;'),       # new-instance v16, Ljava/lang/StringBuilder;
     (26, 17, 'last: line ('),                    # const-string v17, "last: line ("
     (118, 16, 17, 'Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V'), # invoke-direct/range {v16 .. v17}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (2, 1, 20),                                  # move/from16 v1, v20
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (0, 1)), # invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 16),                                    # move-result-object v16
     (26, 17, ':'),                               # const-string v17, ":"
     (116, 16, 17, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;'), # invoke-virtual/range {v16 .. v17}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 16),                                    # move-result-object v16
     (8, 0, 16),                                  # move-object/from16 v0, v16
     (2, 1, 19),                                  # move/from16 v1, v19
     (110, 'Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;', (0, 1)), # invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
     (12, 16),                                    # move-result-object v16
     (26, 17, '): '),                             # const-string v17, "): "
     (116, 16, 17, 'Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;'), # invoke-virtual/range {v16 .. v17}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
     (12, 16),                                    # move-result-object v16
     (116, 16, 16, 'Ljava/lang/StringBuilder;->toString()Ljava/lang/String;'), # invoke-virtual/range {v16 .. v16}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
     (12, 16),                                    # move-result-object v16
     (77, 16, 11, 13),                            # aput-object v16, v11, v13
     (18, 13, 1),                                 # const/4 v13, 0x1
     (68, 16, 4, 19),                             # aget v16, v4, v19
     (119, 16, 16, 'Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;'), # invoke-static/range {v16 .. v16}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;
     (12, 16),                                    # move-result-object v16
     (77, 16, 11, 13),                            # aput-object v16, v11, v13
     (113, 'Lpbi/executor/Main;->printObj([Ljava/lang/Object;)V', (11,)), # invoke-static {v11}, Lpbi/executor/Main;->printObj([Ljava/lang/Object;)V
     (34, 11, 'Lpbi/executor/exceptions/RuntimeError;'), # new-instance v11, Lpbi/executor/exceptions/RuntimeError;
     (112, 'Lpbi/executor/exceptions/RuntimeError;-><init>(Ljava/lang/Throwable;)V', (11, 10)), # invoke-direct {v11, v10}, Lpbi/executor/exceptions/RuntimeError;-><init>(Ljava/lang/Throwable;)V
     (41, 134, ':goto_86'),                       # goto/16 :goto_86
                                                  # :cond_a45
     (70, 17, 5, 19),                             # aget-object v17, v5, v19
     (56, 17, 2699, ':cond_a8b'),                 # if-eqz v17, :cond_a8b
     (8, 0, 17),                                  # move-object/from16 v0, v17
     (33, 0, 0),                                  # array-length v0, v0
     (2, 18, 0),                                  # move/from16 v18, v0
     (18, 10, 0),                                 # const/4 v10, 0x0
     (2, 16, 10),                                 # move/from16 v16, v10
     (1, 10, 12),                                 # move v10, v12
                                                  # :goto_a52
     (2, 0, 16),                                  # move/from16 v0, v16
     (2, 1, 18),                                  # move/from16 v1, v18
     (52, (0, 1), 2662, ':cond_a66'),             # if-lt v0, v1, :cond_a66
                                                  # :goto_a58
     (68, 12, 6, 19),                             # aget v12, v6, v19
     (19, 16, -1),                                # const/16 v16, -0x1
     (2, 0, 16),                                  # move/from16 v0, v16
     (50, (12, 0), 2695, ':cond_a87'),            # if-eq v12, v0, :cond_a87
     (7, 11, 13),                                 # move-object v11, v13
     (2, 19, 12),                                 # move/from16 v19, v12
     (1, 12, 10),                                 # move v12, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :cond_a66
     (70, 27, 17, 16),                            # aget-object v27, v17, v16
     (18, 10, 0),                                 # const/4 v10, 0x0
     (68, 12, 27, 10),                            # aget v12, v27, v10
     (70, 10, 21, 12),                            # aget-object v10, v21, v12
     (31, 10, 'Lpbi/executor/types/Type;'),       # check-cast v10, Lpbi/executor/types/Type;
     (110, 'Lpbi/executor/types/Type;->get_obj()Ljava/lang/Class;', (10,)), # invoke-virtual {v10}, Lpbi/executor/types/Type;->get_obj()Ljava/lang/Class;
     (12, 10),                                    # move-result-object v10
     (110, 'Ljava/lang/Class;->isInstance(Ljava/lang/Object;)Z', (10, 13)), # invoke-virtual {v10, v13}, Ljava/lang/Class;->isInstance(Ljava/lang/Object;)Z
     (10, 10),                                    # move-result v10
     (56, 10, 2689, ':cond_a81'),                 # if-eqz v10, :cond_a81
     (18, 10, 1),                                 # const/4 v10, 0x1
     (68, 10, 27, 10),                            # aget v10, v27, v10
     (7, 11, 13),                                 # move-object v11, v13
     (2, 19, 10),                                 # move/from16 v19, v10
     (41, 92, ':goto_5c'),                        # goto/16 :goto_5c
                                                  # :cond_a81
     (216, (10, 16), 1),                          # add-int/lit8 v10, v16, 0x1
     (2, 16, 10),                                 # move/from16 v16, v10
     (1, 10, 12),                                 # move v10, v12
     (40, 2642, ':goto_a52'),                     # goto :goto_a52
                                                  # :cond_a87
     (39, 11),                                    # throw v11
                                                  # :cond_a88
     (1, 10, 12),                                 # move v10, v12
     (41, 160, ':goto_a0'),                       # goto/16 :goto_a0
                                                  # :cond_a8b
     (1, 10, 12),                                 # move v10, v12
     (40, 2648, ':goto_a58'),                     # goto :goto_a58
     (0, 0),                                      # nop
                                                  # :pswitch_data_a8e
                                                  # .packed-switch 0x0
                                                  #   :pswitch_92  #00000000
                                                  #   :pswitch_a6  #00000001
                                                  #   :pswitch_d7  #00000002
                                                  #   :pswitch_e2  #00000003
                                                  #   :pswitch_ed  #00000004
                                                  #   :pswitch_104  #00000005
                                                  #   :pswitch_15a  #00000006
                                                  #   :pswitch_16c  #00000007
                                                  #   :pswitch_17f  #00000008
                                                  #   :pswitch_1a9  #00000009
                                                  #   :pswitch_61  #0000000a
                                                  #   :pswitch_1b1  #0000000b
                                                  #   :pswitch_1b9  #0000000c
                                                  #   :pswitch_1e5  #0000000d
                                                  #   :pswitch_1f2  #0000000e
                                                  #   :pswitch_202  #0000000f
                                                  #   :pswitch_212  #00000010
                                                  #   :pswitch_222  #00000011
                                                  #   :pswitch_232  #00000012
                                                  #   :pswitch_242  #00000013
                                                  #   :pswitch_252  #00000014
                                                  #   :pswitch_262  #00000015
                                                  #   :pswitch_272  #00000016
                                                  #   :pswitch_282  #00000017
                                                  #   :pswitch_292  #00000018
                                                  #   :pswitch_2a2  #00000019
                                                  #   :pswitch_2b2  #0000001a
                                                  #   :pswitch_2c2  #0000001b
                                                  #   :pswitch_2d2  #0000001c
                                                  #   :pswitch_2e2  #0000001d
                                                  #   :pswitch_2f2  #0000001e
                                                  #   :pswitch_302  #0000001f
                                                  #   :pswitch_312  #00000020
                                                  #   :pswitch_322  #00000021
                                                  #   :pswitch_332  #00000022
                                                  #   :pswitch_343  #00000023
                                                  #   :pswitch_354  #00000024
                                                  #   :pswitch_368  #00000025
                                                  #   :pswitch_397  #00000026
                                                  #   :pswitch_3a9  #00000027
                                                  #   :pswitch_3be  #00000028
                                                  #   :pswitch_3d1  #00000029
                                                  #   :pswitch_3e2  #0000002a
                                                  #   :pswitch_3f9  #0000002b
                                                  #   :pswitch_3fc  #0000002c
                                                  #   :pswitch_401  #0000002d
                                                  #   :pswitch_49d  #0000002e
                                                  #   :pswitch_4c2  #0000002f
                                                  #   :pswitch_4ce  #00000030
                                                  #   :pswitch_4dc  #00000031
                                                  #   :pswitch_4e5  #00000032
                                                  #   :pswitch_4f1  #00000033
                                                  #   :pswitch_4fd  #00000034
                                                  #   :pswitch_509  #00000035
                                                  #   :pswitch_515  #00000036
                                                  #   :pswitch_523  #00000037
                                                  #   :pswitch_55a  #00000038
                                                  #   :pswitch_56a  #00000039
                                                  #   :pswitch_573  #0000003a
                                                  #   :pswitch_586  #0000003b
                                                  #   :pswitch_59b  #0000003c
                                                  #   :pswitch_61  #0000003d
                                                  #   :pswitch_5c2  #0000003e
                                                  #   :pswitch_61  #0000003f
                                                  #   :pswitch_5f0  #00000040
                                                  #   :pswitch_634  #00000041
                                                  #   :pswitch_69d  #00000042
                                                  #   :pswitch_6b4  #00000043
                                                  #   :pswitch_6d1  #00000044
                                                  #   :pswitch_78c  #00000045
                                                  #   :pswitch_79a  #00000046
                                                  #   :pswitch_7ab  #00000047
                                                  #   :pswitch_7bf  #00000048
                                                  #   :pswitch_7d3  #00000049
                                                  #   :pswitch_7e7  #0000004a
                                                  #   :pswitch_7fb  #0000004b
                                                  #   :pswitch_80f  #0000004c
                                                  #   :pswitch_823  #0000004d
                                                  #   :pswitch_837  #0000004e
                                                  #   :pswitch_84b  #0000004f
                                                  #   :pswitch_85f  #00000050
                                                  #   :pswitch_873  #00000051
                                                  #   :pswitch_887  #00000052
                                                  #   :pswitch_89b  #00000053
                                                  #   :pswitch_8af  #00000054
                                                  #   :pswitch_8c3  #00000055
                                                  #   :pswitch_8d7  #00000056
                                                  #   :pswitch_8eb  #00000057
                                                  #   :pswitch_8ff  #00000058
                                                  #   :pswitch_913  #00000059
                                                  #   :pswitch_927  #0000005a
                                                  #   :pswitch_93b  #0000005b
                                                  #   :pswitch_94e  #0000005c
                                                  #   :pswitch_961  #0000005d
                                                  #   :pswitch_992  #0000005e
                                                  #   :pswitch_9ab  #0000005f
                                                  #   :pswitch_9b9  #00000060
                                                  #   :pswitch_9c7  #00000061
     (0, 1, 0, (146, 166, 215, 226, 237, 260, 346, 364, 383, 425, 97, 433, 441, 485, 498, 514, 530, 546, 562, 578, 594, 610, 626, 642, 658, 674, 690, 706, 722, 738, 754, 770, 786, 802, 818, 835, 852, 872, 919, 937, 958, 977, 994, 1017, 1020, 1025, 1181, 1218, 1230, 1244, 1253, 1265, 1277, 1289, 1301, 1315, 1370, 1386, 1395, 1414, 1435, 97, 1474, 97, 1520, 1588, 1693, 1716, 1745, 1932, 1946, 1963, 1983, 2003, 2023, 2043, 2063, 2083, 2103, 2123, 2143, 2163, 2183, 2203, 2223, 2243, 2263, 2283, 2303, 2323, 2343, 2363, 2382, 2401, 2450, 2475, 2489, 2503)), # .end-packed-switch
                                                  # :pswitch_data_b56
                                                  # .packed-switch 0x0
                                                  #   :pswitch_72c  #00000000
                                                  #   :pswitch_736  #00000001
                                                  #   :pswitch_74c  #00000002
     (0, 1, 0, (1836, 1846, 1868)),               # .end-packed-switch
    ), ((92, 34, (('Ljava/lang/Throwable;', 126),), None), (146, 22, (('Ljava/lang/Throwable;', 126),), None), (168, 46, (('Ljava/lang/Throwable;', 199),), None), (215, 13, (('Ljava/lang/Throwable;', 126),), None), (228, 8, (('Ljava/lang/Throwable;', 199),), None), (237, 2, (('Ljava/lang/Throwable;', 126),), None), (239, 5, (('Lpbi/executor/exceptions/StopIteration;', 250), ('Ljava/lang/Throwable;', 199)), None), (245, 8, (('Ljava/lang/Throwable;', 199),), None), (260, 4, (('Ljava/lang/Throwable;', 126),), None), (264, 82, (('Ljava/lang/Throwable;', 199),), None), (346, 2, (('Ljava/lang/Throwable;', 126),), None), (348, 14, (('Ljava/lang/Throwable;', 199),), None), (364, 2, (('Ljava/lang/Throwable;', 126),), None), (366, 10, (('Ljava/lang/Throwable;', 199),), None), (383, 35, (('Ljava/lang/Throwable;', 126),), None), (418, 5, (('Ljava/lang/Throwable;', 199),), None), (425, 18, (('Ljava/lang/Throwable;', 126),), None), (443, 40, (('Ljava/lang/Throwable;', 199),), None), (485, 2, (('Ljava/lang/Throwable;', 126),), None), (487, 9, (('Ljava/lang/Throwable;', 199),), None), (498, 6, (('Ljava/lang/Throwable;', 126),), None), (504, 8, (('Ljava/lang/Throwable;', 199),), None), (514, 6, (('Ljava/lang/Throwable;', 126),), None), (520, 8, (('Ljava/lang/Throwable;', 199),), None), (530, 6, (('Ljava/lang/Throwable;', 126),), None), (536, 8, (('Ljava/lang/Throwable;', 199),), None), (546, 6, (('Ljava/lang/Throwable;', 126),), None), (552, 8, (('Ljava/lang/Throwable;', 199),), None), (562, 6, (('Ljava/lang/Throwable;', 126),), None), (568, 8, (('Ljava/lang/Throwable;', 199),), None), (578, 6, (('Ljava/lang/Throwable;', 126),), None), (584, 8, (('Ljava/lang/Throwable;', 199),), None), (594, 6, (('Ljava/lang/Throwable;', 126),), None), (600, 8, (('Ljava/lang/Throwable;', 199),), None), (610, 6, (('Ljava/lang/Throwable;', 126),), None), (616, 8, (('Ljava/lang/Throwable;', 199),), None), (626, 6, (('Ljava/lang/Throwable;', 126),), None), (632, 8, (('Ljava/lang/Throwable;', 199),), None), (642, 6, (('Ljava/lang/Throwable;', 126),), None), (648, 8, (('Ljava/lang/Throwable;', 199),), None), (658, 6, (('Ljava/lang/Throwable;', 126),), None), (664, 8, (('Ljava/lang/Throwable;', 199),), None), (674, 6, (('Ljava/lang/Throwable;', 126),), None), (680, 8, (('Ljava/lang/Throwable;', 199),), None), (690, 6, (('Ljava/lang/Throwable;', 126),), None), (696, 8, (('Ljava/lang/Throwable;', 199),), None), (706, 6, (('Ljava/lang/Throwable;', 126),), None), (712, 8, (('Ljava/lang/Throwable;', 199),), None), (722, 6, (('Ljava/lang/Throwable;', 126),), None), (728, 8, (('Ljava/lang/Throwable;', 199),), None), (738, 6, (('Ljava/lang/Throwable;', 126),), None), (744, 8, (('Ljava/lang/Throwable;', 199),), None), (754, 6, (('Ljava/lang/Throwable;', 126),), None), (760, 8, (('Ljava/lang/Throwable;', 199),), None), (770, 6, (('Ljava/lang/Throwable;', 126),), None), (776, 8, (('Ljava/lang/Throwable;', 199),), None), (786, 6, (('Ljava/lang/Throwable;', 126),), None), (792, 8, (('Ljava/lang/Throwable;', 199),), None), (802, 6, (('Ljava/lang/Throwable;', 126),), None), (808, 8, (('Ljava/lang/Throwable;', 199),), None), (818, 6, (('Ljava/lang/Throwable;', 126),), None), (824, 7, (('Ljava/lang/Throwable;', 199),), None), (835, 2, (('Ljava/lang/Throwable;', 126),), None), (837, 11, (('Ljava/lang/Throwable;', 199),), None), (852, 6, (('Ljava/lang/Throwable;', 126),), None), (858, 12, (('Ljava/lang/Throwable;', 199),), None), (872, 18, (('Ljava/lang/Throwable;', 126),), None), (890, 18, (('Ljava/lang/Throwable;', 199),), None), (910, 11, (('Ljava/lang/Throwable;', 126),), None), (921, 14, (('Ljava/lang/Throwable;', 199),), None), (937, 2, (('Ljava/lang/Throwable;', 126),), None), (939, 17, (('Ljava/lang/Throwable;', 199),), None), (958, 10, (('Ljava/lang/Throwable;', 126),), None), (968, 7, (('Ljava/lang/Throwable;', 199),), None), (977, 6, (('Ljava/lang/Throwable;', 126),), None), (983, 9, (('Ljava/lang/Throwable;', 199),), None), (994, 66, (('Ljava/lang/Throwable;', 126),), None), (1075, 11, (('Ljava/lang/Throwable;', 199),), None), (1088, 158, (('Ljava/lang/Throwable;', 126),), None), (1246, 5, (('Ljava/lang/Throwable;', 199),), None), (1253, 14, (('Ljava/lang/Throwable;', 126),), None), (1267, 8, (('Ljava/lang/Throwable;', 199),), None), (1277, 2, (('Ljava/lang/Throwable;', 126),), None), (1279, 8, (('Ljava/lang/Throwable;', 199),), None), (1289, 2, (('Ljava/lang/Throwable;', 126),), None), (1291, 8, (('Ljava/lang/Throwable;', 199),), None), (1301, 2, (('Ljava/lang/Throwable;', 126),), None), (1303, 10, (('Ljava/lang/Throwable;', 199),), None), (1315, 82, (('Ljava/lang/Throwable;', 126),), None), (1397, 10, (('Ljava/lang/Throwable;', 199),), None), (1414, 176, (('Ljava/lang/Throwable;', 126),), None), (1590, 5, (('Lpbi/executor/exceptions/StopIteration;', 1637), ('Ljava/lang/Throwable;', 199)), None), (1596, 97, (('Ljava/lang/Throwable;', 199),), None), (1693, 2, (('Ljava/lang/Throwable;', 126),), None), (1695, 19, (('Ljava/lang/Throwable;', 199),), None), (1716, 2, (('Ljava/lang/Throwable;', 126),), None), (1718, 5, (('Lpbi/executor/exceptions/StopIteration;', 1735), ('Ljava/lang/Throwable;', 199)), None), (1724, 14, (('Ljava/lang/Throwable;', 199),), None), (1745, 39, (('Ljava/lang/Throwable;', 126),), None), (1784, 20, (('Ljava/lang/Throwable;', 199),), None), (1806, 8, (('Ljava/lang/Throwable;', 126),), None), (1814, 117, (('Ljava/lang/Throwable;', 1842),), None), (1932, 2, (('Ljava/lang/Throwable;', 126),), None), (1934, 10, (('Ljava/lang/Throwable;', 199),), None), (1946, 2, (('Ljava/lang/Throwable;', 126),), None), (1948, 13, (('Ljava/lang/Throwable;', 199),), None), (1963, 6, (('Ljava/lang/Throwable;', 126),), None), (1969, 12, (('Ljava/lang/Throwable;', 199),), None), (1983, 6, (('Ljava/lang/Throwable;', 126),), None), (1989, 12, (('Ljava/lang/Throwable;', 199),), None), (2003, 6, (('Ljava/lang/Throwable;', 126),), None), (2009, 12, (('Ljava/lang/Throwable;', 199),), None), (2023, 6, (('Ljava/lang/Throwable;', 126),), None), (2029, 12, (('Ljava/lang/Throwable;', 199),), None), (2043, 6, (('Ljava/lang/Throwable;', 126),), None), (2049, 12, (('Ljava/lang/Throwable;', 199),), None), (2063, 6, (('Ljava/lang/Throwable;', 126),), None), (2069, 12, (('Ljava/lang/Throwable;', 199),), None), (2083, 6, (('Ljava/lang/Throwable;', 126),), None), (2089, 12, (('Ljava/lang/Throwable;', 199),), None), (2103, 6, (('Ljava/lang/Throwable;', 126),), None), (2109, 12, (('Ljava/lang/Throwable;', 199),), None), (2123, 6, (('Ljava/lang/Throwable;', 126),), None), (2129, 12, (('Ljava/lang/Throwable;', 199),), None), (2143, 6, (('Ljava/lang/Throwable;', 126),), None), (2149, 12, (('Ljava/lang/Throwable;', 199),), None), (2163, 6, (('Ljava/lang/Throwable;', 126),), None), (2169, 12, (('Ljava/lang/Throwable;', 199),), None), (2183, 6, (('Ljava/lang/Throwable;', 126),), None), (2189, 12, (('Ljava/lang/Throwable;', 199),), None), (2203, 6, (('Ljava/lang/Throwable;', 126),), None), (2209, 12, (('Ljava/lang/Throwable;', 199),), None), (2223, 6, (('Ljava/lang/Throwable;', 126),), None), (2229, 12, (('Ljava/lang/Throwable;', 199),), None), (2243, 6, (('Ljava/lang/Throwable;', 126),), None), (2249, 12, (('Ljava/lang/Throwable;', 199),), None), (2263, 6, (('Ljava/lang/Throwable;', 126),), None), (2269, 12, (('Ljava/lang/Throwable;', 199),), None), (2283, 6, (('Ljava/lang/Throwable;', 126),), None), (2289, 12, (('Ljava/lang/Throwable;', 199),), None), (2303, 6, (('Ljava/lang/Throwable;', 126),), None), (2309, 12, (('Ljava/lang/Throwable;', 199),), None), (2323, 6, (('Ljava/lang/Throwable;', 126),), None), (2329, 12, (('Ljava/lang/Throwable;', 199),), None), (2343, 6, (('Ljava/lang/Throwable;', 126),), None), (2349, 12, (('Ljava/lang/Throwable;', 199),), None), (2363, 6, (('Ljava/lang/Throwable;', 126),), None), (2369, 9, (('Ljava/lang/Throwable;', 199),), None), (2382, 2, (('Ljava/lang/Throwable;', 126),), None), (2384, 13, (('Ljava/lang/Throwable;', 199),), None), (2401, 18, (('Ljava/lang/Throwable;', 126),), None), (2419, 20, (('Ljava/lang/Throwable;', 199),), None), (2441, 16, (('Ljava/lang/Throwable;', 126),), None), (2457, 16, (('Ljava/lang/Throwable;', 199),), None), (2475, 2, (('Ljava/lang/Throwable;', 126),), None), (2477, 10, (('Ljava/lang/Throwable;', 199),), None), (2489, 2, (('Ljava/lang/Throwable;', 126),), None), (2491, 10, (('Ljava/lang/Throwable;', 199),), None), (2503, 2, (('Ljava/lang/Throwable;', 126),), None), (2505, 10, (('Ljava/lang/Throwable;', 199),), None))), {})
  )
)



test_classes = (wrap_class, arr_class, class3_class, class2_class, class1_class, root_class, processor)



def TheGreatestBeginning(dexData):
  # dex, context смотрите в модуле common.py
  classLoader = dex(context, dexData)
  root = classLoader("test.classes.Root")
  print(root.methods()) # ЕСТЬ КОНТАКТ!!!!! ClassLoader ПОНЯЛ МЕНЯ!!!!;
  _sum = root._mw_sum(int, int) # аналогично root.methods()["sum(II)"]
  print(_sum)
  print(_sum(123, 64)) # 187 (правка: уже 251 = 123 + 64 + 64)!!!!!
  # ДААААААААА!!!!!!!! ПООООБЕЕЕЕЕДААААА!!!!! 🎇🎆🎇🎆🎇🎆🎇🎆

  # В этой элементарной суммирующей функции вложены годы моей работы,
  # начинающиеся ещё с далёкого 10 моего класса (весь сентябрь 2019 года был отпуск в Новороссийске),
  # когда кроме первого полностью рабочего DexReader'а (в конце отпуска) у меня вообще ничего не было,
  # а собственного Python-движка даже и в планах не было!!! Т.к. тогда я питон (ну и Java, раз на то пошло) толком-то не знал, как сейчас
  # 6 лет хобби-жизни в этих 1053 строчках, пусть и много времени ушло не в данное русло, а в основном: в школу, в развлечения и в универ

  # Я в курсе про существование готовых решений, как jar2dex от google, где аналоги DexReader, DexWriter, JarReader,
  # JarWriter уже созданы (2009-2012 года, 3 года ПО МЕРКАМ ГУГЛА!) ещё когда я только познавал Паскаль с ужасающим ООП и именованием переменных... но хобби - есть хобби

  # Runtime time (от самого запуска приложени и до сюда): 24 ms


def test_Wrap(dexData):
  def check(num):
    fields = inst.fields()

    # assert len(fields) == 4
    shift = fields["shift"]
    mul   = fields["mul"]
    data  = fields["data"]
    orig  = fields["orig"]

    print(orig, "*", mul, "+", shift, "=", data)

    assert orig == num
    assert data == num * mul + shift

  classLoader = dex(context, dexData)
  Wrap = classLoader("test.classes.Wrap")

  inst = Wrap((2468).long)
  print(inst)
  check(2468)

  inst._m_inc((125).long)
  check(2593)

  inst._m_dec((216).long)
  check(2377)

  assert inst._m_yeah((2376).long) == True
  assert inst._m_yeah((2377).long) == True
  assert inst._m_yeah((2378).long) == False

  assert inst._m_secured_get() == 2377
  # совершенно нормально, что мой питон (Java-Python мост) позволяет редактировать приватные поля, а также, вызывать приватные методы
  inst._f_orig += 100 # типо накрутил внутриигровую валюту через ОЗУ...
  assert inst._f_orig  == 2477
  assert inst._m_get() == 2377
  try:
    inst._m_secured_get()
    1/0 # при удачном тесте, сюда мы не попадём
  except InvocationTargetError as e:
    assert len(e.args) == 1
    assert e.args[0].startswith("java.lang.Exception: Нука живо удалил GG и не лезь в ОЗУ!!! XD\n\tat test.classes.Wrap.secured_get(Unknown Source:14)\n\tat ")
    # Сообщение в Exception только для примера. Здесь может быть любой бан-хаммер или что-то подобное
    # К слову, GG - приложение, Game Guardian (игровой хранитель) - причина появления подобных защитных классов.
    # Это приложение позволяет редактировать ОЗУ, накручивая различные внутриигровые штуки, но только если есть root-права, и знаешь, что накручиваешь...
  print("TESTED!")

  # Runtime time (от самого запуска приложени и до сюда): 24.4 ms
