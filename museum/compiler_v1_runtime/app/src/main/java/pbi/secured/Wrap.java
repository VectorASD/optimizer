package pbi.secured;

public class Wrap {
  private static int randint(int a, int b) {
    return (int) (Math.random() * (b - a + 1)) + a;
  }
  
  private long mul, shift, data, orig;
  
  public Wrap() { first(0); }
  public Wrap(long i) { first(i); }
  
  private void first(long i) {
    mul = randint(3, 32);
    shift = randint(10, 1000000);
    set(i);
  }
  
  public void set(long i) {
    data = i * mul + shift;
    orig = i;
  }
  public void secured_set(long i) {
    long i2 = i * mul;
    if (i2 / mul == i) {
      data = i2 + shift;
      orig = i;
    }
  }
  public long get() {
    return (data - shift) / mul;
  }
  public long secured_get() throws Exception {
    long res = get();
    if (res != orig) throw new Exception("Нука живо удалил GG и не лезь в ОЗУ!!! XD");
    return res;
  }
  
  public void inc(long i) throws Exception {
    secured_set(secured_get() + i);
  }
  public void dec(long i) throws Exception {
    secured_set(secured_get() - i);
  }
  public boolean yeah(long i) throws Exception {
    return secured_get() >= i;
  }
}

/*
Класс защищённой переменной long. by VectorASD ;'-}}}
Позволяет реализовать безопасную механику магазина.

Основные методы на примере магазина:
• конструктор(i) и secured_set(i) позволяют установить количество монет.
• secured_get() - узнать количество монет или послать за юзание читов.
• inc(i) - прибавить i-ое количество монет за заслуги.
• yeah(i) - проверить, хватает ли монет на товар стоимостью i-монет.
• dec(i) - отнять i-ое количество монет за покупку товара и выдать товар.
  Перед ним юзаем dec(i)

Все Exception данного класса можно заменить на дочерний класс от Exception
  для корректной работы try-catch-конструкции, чтобы не всё подряд ловила,
  а только бан-хаммер (вызов ошибки из secured_get) данного класса ;'-}

Взлом в рамках GG (Game_Guardian-чит):
• переписываем в этом классе first так, чтобы mul был всегда = 1, а shift = 0.
• потом выпиливаем проверку orig, да и саму переменную orig.

Взлом в рамках мода:
• создаём обёртку для классов этого типа, чтобы обернуть методы secured_set
  и secured_get в методы get и set.
• если нужно взломать массив классов этого типа, то get может выдавать строку
  ",".join(всех гетнутые long), а сеттер парсить строку, проверяя на то,
   что количество "," не нарушену, да и числа никуда не выходят.

Границы long:
• max = 2^63-1 = 9223372036854775807
• min = -2^63 = -9223372036854775808
• max + 1 = min (переполнение вверх), т.е. max + 1 < max
• min - 1 = max (переполнение вниз), т.е. min - 1 > min
• для большей информации, чекаем кодирование чисел ДОПОЛНИТЕЛЬНЫМ КОДОМ
  и как устроен сумматор чисел под копотом ;'-}

Безопасные границы данного защитного класса:
• shift не влияет, а mul - да.
• max_mul = 32
• max = (2^63-1) // max_mul = 288230376151711743
• min = (-2^63) // max_mul = -288230376151711744
• если long будет ЗА этими пределами, то secured_set проигнорит set,
  т.к. i * mul / mul ≠ i в рамках long из-за переполнения!!!!!

Пруфы границ на питоне:
>>> m = 2 ** 63 - 1
>>> m // 32 * 32 > m
False (всё в порядке)
>>> (m + 1) // 32 * 32 > m
True (long заехал за шарики...)
>>> m = -2**63
>>> m // 32 * 32 < m
False (всё норм)
>>> (m - 1) // 32 * 32 < m
True (long заехал за шарики...)
*/