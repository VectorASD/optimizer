def Lab2_5():
  page1_xml = """
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <TextView
        android:textSize="29dp"
        android:textColor="#80ffad"
        android:layout_gravity="center"
        android:id="@+id/textView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@string/text"/>
    <ImageView
        android:layout_gravity="center"
        android:id="@+id/imageView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:src="@drawable/img"
    />
</LinearLayout>
""".strip()

  page2_xml = """
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent">
    <ListView
        android:id="@+id/listView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"/>
</LinearLayout>
""".strip()

  tab_xml = """
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#ff00ff">
    <TabHost
        android:layout_gravity="center"
        android:id="@android:id/tabhost"
        android:layout_width="match_parent"
        android:layout_height="match_parent">
        <LinearLayout
            android:orientation="vertical"
            android:layout_width="match_parent"
            android:layout_height="match_parent">
            <TabWidget
                android:textColorPrimary="#0000FF"
                android:textColorSecondary="#00FF00"
                android:id="@android:id/tabs"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"/>
            <FrameLayout
                android:id="@android:id/tabcontent"
                android:layout_width="match_parent"
                android:layout_height="match_parent"/>
        </LinearLayout>
    </TabHost>
</LinearLayout>
""".strip()

  """
  TabHost tabHost = getTabHost();
        
        TabHost.TabSpec tabSpec = tabHost.newTabSpec("tag1");
        tabSpec.setContent(new Intent(this, one.class));
        tabSpec.setIndicator("Эбаут", getResources().getDrawable(R.drawable.a));
        tabHost.addTab(tabSpec);
        
        TabHost.TabSpec tabSpec2 = tabHost.newTabSpec("tag1");
        tabSpec2.setIndicator("Список операционных систем", getResources().getDrawable(R.drawable.b));
        tabSpec2.setContent(new Intent(this, two.class));
        tabHost.addTab(tabSpec2);
        
        TabHost.TabSpec tabSpec3 = tabHost.newTabSpec("tag2");
        tabSpec3.setIndicator("Метео сводка", getResources().getDrawable(R.drawable.c));
        tabSpec3.setContent(new Intent(this, three.class));
        tabHost.addTab(tabSpec3);
"""



  class handler:
    def onCreate(self, activity):
      #ctx = activity._m_getApplicationContext().cast(Context)
      print("onCreate", self, activity)

      tabHost = TabHost(activity)
      tabHost.addTab("navigation_tag", "Эбаут", ress.drawable("drawable/snow"), page1inst.intent())
      tabHost.addTab("navigation_tag2", "Список OS", ress.drawable("drawable/cloud"), page2inst.intent())
      tabHost.addTab("navigation_tag3", "Метео сводка", ress.drawable("drawable/hot"), page3inst.intent())

    def onStart(self): print("onStart")
    def onRestart(self): print("onRestart")
    def onResume(self): print("onResume")
    def onPause(self): print("onPause")
    def onStop(self): print("onStop")
    def onDestroy(self): print("onDestroy")
    def onTouchEvent(self, e):
      print("onTouchEvent", e)
      return True
    def onKeyDown(self, num, e):
      print("onKeyDown", num, e)
      return True
    def onKeyUp(self, num, e):
      print("onKeyUp", num, e)
      return True
    reverse = {
      "cr": onCreate,
      "st": onStart,
      "re": onRestart,
      "res": onResume,
      "pa": onPause,
      "sto": onStop,
      "de": onDestroy,
      "to": onTouchEvent,
      "kd": onKeyDown,
      "ku": onKeyUp,
    }

  rm = ResourceManager()
  print(rm)
  #rm.id("loled_id")
  #rm.id("meowed_id")
  #rm.id("woofed_id")
  #rm.string("meow", "woof")
  #rm.string("egg", "bomb")
  #rm.string("cat", "dog")
  rm.string("text", "Автор перед Вами 🤔🥳")
  #rm.string("human", "people")
  #rm.string("fox", "bear")
  #rm.drawable("name1", "path1.png", bytes((1, 2, 3, 4, 5)))
  #rm.drawable("name2", "path2.jpg", bytes((6, 7, 8)))
  #rm.drawable("name3", "path3.gif", bytes((0, 1, 0, 1, 0, 1, 0, 2)))
  #rm.drawable("name4", "path4.bmp", bytes((9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)))
  rm.drawable("img", "img.jpg", __resource("c.jpg"))
  rm.drawable("snow", "snow.png", __resource("snow.png"))
  rm.drawable("cloud", "cloud.png", __resource("cloud.png"))
  rm.drawable("warm", "warm.png", __resource("warm.png"))
  rm.drawable("hot", "hot.png", __resource("hot.png"))
  rm.xml("page1", "page1.xml", page1_xml)
  rm.xml("page2", "page2.xml", page2_xml)
  rm.xml("tab", "tab.xml", tab_xml)
  print(rm)
  ress = rm.release()
  ress.save("/sdcard/_myress.apk")
  ctx = ress.ctx
  print(ress, ctx)
  #print(hex(rm.get("id/imageView")))
  #print(hex(rm.get("+id/imageView")))
  #print(hex(rm.get("drawable/img")))

  class page1:
    def intent(self):
      return ress.intent("layout/page1", self)
    def onCreate(self, activity):
      print("onCreate (page1)", self, activity)
    reverse = {"cr": onCreate}

  class page2:
    def intent(self):
      return ress.intent("layout/page2", self)
    def onCreate(self, activity):
      self.reverse["sc"]() # setContentView
      print("onCreate (page2)", self, activity)
      listView = activity._m_findViewById(rm.get("id/listView").int)
      A = ArrayAdapter(ctx, R_layout._f_simple_list_item_1.int, ("Meow", "Woof", "Boom!")._a_Object)
      listView._mw_setAdapter(ListAdapter)(A)
    reverse = {"cr": onCreate}

  class page3:
    def __init__(self):
      cities = ('Невермира', 'Звездный Град', 'Кибертрон', 'Галактический Город', 'Альдеран', 'Небесный Оазис', 'Цитадель Чужих', 'Марсианская Колония', 'Далекий Колдовск', 'Атлантида Параллельная', 'Планета Пандора', 'Граничный Рубеж', 'Космический Лагерь', 'Титанов Город', 'Варшава-6', 'Звездный Путь', 'Амазония Галактическая', 'Краевая Звезда', 'Астральный город Небесный', 'Разговаривающий Планет', 'Химерийский Город', 'Новый Атлантис', 'Изгнанные Карлики', 'Галактический Лабиринт', 'Неопалимый Остров', 'Миранда-13', 'Утро Звезды', 'Вавилон-9', 'Терра Нескончаемая', 'Огненная Колония', 'Звёздные Врата', 'Пьяный Галактшат', 'Эхо Вселенной', 'Гармония Сфер', 'Новый Аполлон', 'Лунная Легенда', 'Кристальные Галакты', 'Долорис', 'Гиперборея', 'Омега-41', 'Станист Лагерь', 'Минеральный Планетарий', 'Чертоги Лун', 'Сонный Туман', 'Судьба Химер', 'Альфа-35', 'Квазарный Коловорот', 'Космическая Экспедиция', 'Древний Космос', 'Небесный Замок', 'Пандемониум', 'Галафа', 'Лазурный Трон', 'Палладиум', 'Зелёный Эдем', 'Монитор', 'Вечная Тьма', 'Полымя Галактик', 'Коллапсар', 'Виртуальное Созвездие', 'Драконий Рог', 'Бурлящий Поток', 'Непознанный Диванон', 'Королевство Вечной Ночи', 'Циклоноид', 'Химерии', 'Меридиан', 'Фаэтон', 'Звёздный Лидер', 'Жемчужный Гребень', 'Антипод', 'Черный Замок', 'Лордерон', 'Солнечная Орбита', 'Галактическая Пропасть', 'Зенитный Лагерь', 'Гайя-2', 'Звездный Райдер', 'Венера 6', 'Лунар 9', 'Тахомар', 'Подземный Поток', 'Взлетая Луна', 'Марсианская Колония', 'Аурория', 'Зиггурат Медины', 'Терра Невстреченная', 'Гейзенберг', 'Экспансия', 'Прадовия', 'Титания', 'Норвена', 'Зетная Спираль', 'Гибралтар', 'Хаосный Мир', 'Арктур-9', 'Нойромансия', 'Венерианская Станция', 'Странный Номер', 'Звёздное Облачко')
      shuffled_cities = shuffler(cities, 20)

      head = TableRow(ctx, ())
      head.addView(TextView(ctx, "Город"))
      head.addView_span(TextView(ctx, "Погода"), 2)
      table = TableLayout(ctx, (head,))
      addRow = table.addView

      for i in range(20):
        img = ImageView(ctx, icons[randint(0, 3)])
        tv = TextView(ctx, shuffled_cities[i])
        temp = randint(-1000, 1000)
        temp = ("%s °C" if temp < 0 else "+%s °C") % temp
        temp = TextView(ctx, temp)
        row = TableRow(ctx, (tv, img, temp))
        addRow(row._view)
      scroll = ScrollView(ctx, table)
      self.root = scroll._view

    def intent(self):
      return ress.intent("layout/page1", self)

    def onCreate(self, activity):
      print("onCreate (page3)", self, activity)
      return self.root
    reverse = {"cr": onCreate}

  class page4:
    def __init__(self):
      names = ("Зерон", "Лилия", "Крокус", "Ариэль", "Дариана", "Фауст", "Вивиана", "Никандор", "Ксения", "Юлиан", 
        "Альвиана", "Галаад", "Нэйра", "Яромир", "Эллада", "Мирон", "Василиса", "Амадей", "Савелий", "Левантий", 
        "Мелиссандра", "Эдгар", "Гвиллиам", "Мериана", "Родерик", "Надежда", "Арэн", "Элианора", "Рауль", 
        "Изольда", "Фелин", "Луиза", "Эстер", "Финнвер", "Ирида", "Люциан", "Эсмеральда", "Орест", "Равен", 
        "Магдалена", "Заратустра", "Ариадна", "Севиль", "Оливия", "Ланселот", "Аза", "Эмерик", "Сабрина", "Земфира", 
        "Анатоль", "Валентина", "Май", "Джеральд", "Янина", "Устин", "Леонель", "Элеонор", "Зара", "Артемида", 
        "Герман", "Лилиана", "Урсула", "Бальтазар", "Эсмиральда", "Орфей", "Нинель", "Лютас", "Ульяна", "Далия", 
        "Мириада", "Юстиниан", "Эллина", "Роланд", "Мериэль", "Исабель", "Всеволод", "Милена", "Эрен", "Раиса", 
        "Бернар", "Эла", "Адель", "Леннон", "Эрелин", "Стефания", "Эдгард", "Лавиния", "Кира", "Арлетт", "Эндимион")

      surnames = ("Звездобережный", "Лунносветов", "Тангардов", "Астраллан", "Гладиолусов", "Зефиросный", 
            "Няшев", "Светозаров", "Искроверст", "Аметистов", "Теневолнов", "Велестиянов", "Полудоров", 
            "Небоярцев", "Юношев", "Заревонос", "Фантаский", "Альфарбор", "Магистральнов", "Тайрантов", 
            "Звездолесьев", "Полумостов", "Арканистов", "Дальнигрив", "Кораблинский", "Драгонхартов", 
            "Звездовойнов", "Оранжевский", "Твайлин", "Земленаров", "Раздольин", "Арктичев", "Бликсолев", 
            "Чародейчук", "Солнечеви", "Летарьев", "Звездографов", "Магелкин", "Источников", "Озаревских", 
            "Русалюков", "Пламенский", "Грозозаров", "Хромолавров", "Серебренов", "Меченосов", "Ночекрылов", 
            "Златовников", "Леснесветов", "Зорькин", "Вуальнов", "Спокойнов", "Мистельберг", "БлагоКов", 
            "Лиловчук", "Скорпионосов", "Застольнов", "Полуночников", "Кардамонов", "Стремнов", "Арканилев",
            "Солнцеваров", "Туманных", "Мерцанинов", "Дивословов", "Вечернов", "Камнеунер", "Стихязаров", 
            "Огниллов", "Ветроярцев", "Мечтачев", "Штормовников", "Вишневнов", "Таиных", "Гравиков", 
            "Добрословов", "Кристалтаров", "Звезднеев", "Амброзианов", "Мольванов", "Спекторанов", "Кованцев", 
            "Астрондов", "Судьборев", "Октавинский", "Лунозоров", "Арканаров", "Метеорин", "Лунозвездев", 
            "Колдунцев", "Светозарев", "Ветрогардов", "Эклипсов", "Прозорлин", "Хромолесов", "Звездопень", 
            "Барбамельников", "Солнцепадов", "Тьмогрив", "Амарантов", "Вороннов")

      sql = MySQLite()

      table = TableLayout(ctx, ())
      scroll = ScrollView(ctx, HorizontalScrollView(ctx, table))

      def render():
        def toStr(text): return "%.2f" % text if type(text) is float else str(text)
        table.clear()
        addRow = table.addView
        for row in MODE():
          row = TableRow(ctx, (TextView(ctx, toStr(item)).setPadding(8) for item in row))
          addRow(row._view)
      def add(view):
        sql.add_row("%s %s" % (names[randint(0, 89)], surnames[randint(0, 100)]), frandom(10, 150), frandom(50, 300), randint(18, 100))
        render()
      def clear(view):
        sql.clear()
        render()
      MODE = None
      def set_mode(n):
        nonlocal MODE
        for i in range(3): btns[i + 2].setBG(0xff0000ff if i == n else 0xffffff00)
        MODE = (sql.read_all_rows, sql.read_sorted_by_ages, sql.read_sorted_by_ages_desc)[n]
        render()
      btns = (
         Button(ctx, "Add", OnClickListener(add)).setPadding(16),
         Button(ctx, "Clear", OnClickListener(clear)).setPadding(16),
         Button(ctx, "Main", OnClickListener(lambda _: set_mode(0))).setPadding(16),
         Button(ctx, "Age", OnClickListener(lambda _: set_mode(1))).setPadding(16),
         Button(ctx, "Age (desc)", OnClickListener(lambda _: set_mode(2))).setPadding(16),
      )
      set_mode(0)

      head = TableRow(ctx, btns)
      body = TableRow(ctx, ())
      body.addView_span(scroll, 5)
      root = TableLayout(ctx, (head, body))
      root.shrink_stretch()

      self.root = root._view

    def onCreate(self, activity):
      print("onCreate (page4)", self, activity)
      return self.root
    """
    def onDestroy(self):
      V = self.root
      #while V:
      #  print(V)
      #  V = V._m_getParent()
      V = self.root
      V._m_getParent().cast(ViewGroup)._m_removeView(V.cast(View))
      #print("$", V._m_getParent()) None! Ok!
    """
    reverse = {"cr": onCreate}

  icons = rm.get("drawable/snow"), rm.get("drawable/cloud"), rm.get("drawable/warm"), rm.get("drawable/hot")

  page1inst = page1()
  page2inst = page2()
  page3inst = page3()
  page4inst = page4()
  H = handler()

  def render(gui):
    gui.button(1, 8, 2, 2, 18, (lambda _: ress.tabActivity("layout/tab", H), ""))
    gui.button(4, 8, 2, 2, 18, (lambda _: ress.activity("layout/page1", page4inst), ""))
  return render





# https://developer.alexanderklimov.ru/android/layout/tablelayout.php
# После этой статьи уже не совсем ясно, кто составлял пример для третего раздела

from android.widget.ImageView import jImageView
from android.widget.TextView import jTextView
from android.widget.Button import jButton
from android.widget.TableRow import jTableRow
from android.widget.TableLayout import jTableLayout
from android.widget.ScrollView import jScrollView
from android.widget.HorizontalScrollView import jHorizontalScrollView
from android.widget.TableRow_._LayoutParams import TR_LayoutParams
from android.view.ViewGroup_._LayoutParams import VG_LayoutParams
from android.widget.TabHost_._TabSpec import TabSpec
from android.content.Intent import Intent
from android.widget.ArrayAdapter import ArrayAdapter
from android.widget.ListAdapter import ListAdapter

from android.graphics.Typeface import Typeface
from android.view.Gravity import Gravity
from android.view.View import View
from android.view.ViewGroup import ViewGroup
from android.R_._layout import R_layout
from android.content.ContentValues import jContentValues

from java.lang.CharSequence import CharSequence
from java.lang.Long import jLong
from java.lang.Double import jDouble

def shuffler(data, k):
  result = [None] * k
  pool = list(data)
  n1 = len(data) - 1
  for i in range(k):
    j = randint(0, n1)
    result[i] = pool[j]
    pool[j] = pool[n1]
    n1 -= 1
  return result

class ImageView:
  def __init__(self, ctx, rid):
    self._view = img = jImageView(ctx)
    self._setPadding = img._mw_setPadding(INT, INT, INT, INT)
    
    img._m_setImageResource(rid.int)
  def setPadding(self, p):
    p = p.int
    self._setPadding(p, p, p, p)
    return self

class TextView:
  def __init__(self, ctx, str):
    self._view = tv = jTextView(ctx)
    self.setText = setText = tv._mw_setText(CharSequence)
    self._setPadding = tv._mw_setPadding(INT, INT, INT, INT)

    tv._m_setTypeface(Typeface._f_SERIF, Typeface._f_BOLD.int)
    tv._m_setGravity(Gravity._f_CENTER.int)
    setText(str)
  def setPadding(self, p):
    p = p.int
    self._setPadding(p, p, p, p)
    return self

class Button:
  def __init__(self, ctx, str, OCL):
    self._view = btn = jButton(ctx)
    self.setText = setText = btn._mw_setText(CharSequence)
    self._setPadding = btn._mw_setPadding(INT, INT, INT, INT)
    self._setBackgroundColor = btn._mw_setBackgroundColor(INT)

    btn._m_setTypeface(Typeface._f_SERIF, Typeface._f_BOLD.int)
    btn._m_setGravity(Gravity._f_CENTER.int)
    btn._m_setOnClickListener(OCL)
    setText(str)
  def setPadding(self, p):
    p = p.int
    self._setPadding(p, p, p, p)
    return self
  def setBG(self, color):
    self._setBackgroundColor(color.int)
    return self

class TableRow:
  def __init__(self, ctx, views = ()):
    self._view = row = jTableRow(ctx)
    self._addView = row._mw_addView(View)
    self._addView2 = row._mw_addView(View, VG_LayoutParams)

    row._m_setGravity(Gravity._f_CENTER.int)
    for view in views: self.addView(view)
  def addView(self, view):
    self._addView(view._view)
  def addView_span(self, view, span):
    params = TR_LayoutParams()
    params._f_span = span.int
    self._addView2(view._view, params)

class TableLayout:
  def __init__(self, ctx, views = ()):
    self._view = table = jTableLayout(ctx)
    self.addView = addView = table._mw_addView(View)
    self.removeAllViews = table._mw_removeAllViews()

    for view in views: addView(view._view)
  def shrink_stretch(self):
    table = self._view
    table._m_setShrinkAllColumns(True) # Shrink - сжатие
    table._m_setStretchAllColumns(True) # Stretch - растягивание
  def clear(self):
    self.removeAllViews()

class ScrollView:
  def __init__(self, ctx, view = None):
    self._view = scroll = jScrollView(ctx)
    self.addView = addView = scroll._mw_addView(View)

    if view: addView(view._view)

class HorizontalScrollView:
  def __init__(self, ctx, view = None):
    self._view = scroll = jHorizontalScrollView(ctx)
    self.addView = addView = scroll._mw_addView(View)
    #scroll._m_setFillViewport(True)

    if view: addView(view._view)

class TabHost:
  def __init__(self, activity):
    tabHost = activity._m_getTabHost()
    self.newTabSpec = tabHost._mw_newTabSpec(str)
    self._addTab = tabHost._mw_addTab(TabSpec)

  def addTab(self, tag, name, icon, content):
    tabSpec = self.newTabSpec(tag)
    tabSpec._mw_setIndicator(CharSequence, Drawable)(name, icon)
    tabSpec._m_setContent(content)
    self._addTab(tabSpec)

class ContentValues:
  def __init__(self):
    self.me = me = jContentValues()
    self.puts = {
      str: me._mw_put(str, str),
      int: me._mw_put(str, jLong),
      float: me._mw_put(str, jDouble),
    }
  def put(self, key, value):
    self.puts[type(value)](key, value)

class MySQLite:
  def __init__(self):
    self.locker = MyLock()

    def onCreate(db): print("√ create:", db)
    def onUpdate(db, a, b): print("√ update:", db, "|", a, "->", b)

    sql = SQLite("Students.db", 1, onCreate, onUpdate)
    self.db = db = sql.db
    self.execSQL = db._mw_execSQL(str)
    self.rawQuery = db._mw_rawQuery(str, ()._a_String)
    self.insert = db._mw_insert(str, str, jContentValues)

    self.table_name = table_name = "stud_table"
    self.col_id = col_id = "id"
    self.col_name = col_name = "name"
    self.col_weight = col_weight = "weight"
    self.col_height = col_height = "height"
    self.col_age = col_age = "age"

    self.req_create = "CREATE TABLE IF NOT EXISTS %s (%s INTEGER PRIMARY KEY AUTOINCREMENT, %s TEXT, %s FLOAT, %s FLOAT, %s INTEGER);" % (table_name, col_id, col_name, col_weight, col_height, col_age)
    self.req_delete = "DROP TABLE IF EXISTS %s;" % table_name

  def new_table(self):
    with self.locker:
      self.execSQL(self.req_create)
  def clear(self):
    with self.locker:
      self.execSQL(self.req_delete)
      self.execSQL(self.req_create)

  def add_row(self, name, weight, height, age):
    cv = ContentValues()
    cv.put(self.col_name, name)
    cv.put(self.col_weight, weight)
    cv.put(self.col_height, height)
    cv.put(self.col_age, age)
    with self.locker: row_id = self.insert(self.table_name, None, cv.me)
    #print("New row id:", row_id)

  def cursor2table(self, cursor):
    cols = (i.int for i in range(cursor._m_getColumnCount()))
    namer = cursor._mw_getColumnName(INT)
    typer = cursor._mw_getType(INT)
    next = cursor._mw_moveToNext()

    rows = [(namer(i) for i in cols)]
    if not next():
      cursor._m_close()
      return rows
    types = (None, cursor._mw_getInt(INT), cursor._mw_getDouble(INT), cursor._mw_getString(INT))
    cycler = tuple(zip(cols, types[typer(i)] for i in cols))
    app = rows.append
    row = (f(i) for i, f in cycler)
    app(row)
    while next(): app((f(i) for i, f in cycler))
    cursor._m_close()
    return rows
  def read_all_rows(self):
    with self.locker:
      cursor = self.rawQuery("SELECT * FROM %s" % self.table_name, None)
      res = self.cursor2table(cursor)
    return res
  def read_sorted_by_ages(self):
    with self.locker:
      cursor = self.rawQuery("SELECT * FROM %s ORDER BY %s" % (self.table_name, self.col_age), None)
      res = self.cursor2table(cursor)
    return res
  def read_sorted_by_ages_desc(self):
    with self.locker:
      cursor = self.rawQuery("SELECT * FROM %s ORDER BY %s DESC" % (self.table_name, self.col_age), None)
      res = self.cursor2table(cursor)
    return res
