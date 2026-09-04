face2delta = (
  ( 0, +1,  0), # top    / верх   (+Y)
  ( 0,  0, +1), # south  / юг     (+Z)
  (-1,  0,  0), # west   / запад  (-X)
  ( 0,  0, -1), # north  / север  (-Z)
  (+1,  0,  0), # east   / восток (+X)
  ( 0, -1,  0), # bottom / дно    (-Y)
)
ids_for_build = 0, 1, 2, 3, 4, 5, 6, 10, 11
priorities = (
  0, # (id:0) воздух
  2, # (id:1) стена
  2, # (id:2) дорожка
  1, # (id:3) вход
  1, # (id:4) выход
  2, # (id:5) односторонник 1
  2, # (id:6) односторонник 2
  2, # (id:7) односторонник 3
  2, # (id:8) туман
  0, # (id:9) "что это?"
  2, # (id:10) защищённая дорожка
  2, # (id:11) телепортатор
)
can_walk   = {2, 5, 6, 7, 10, 11} # на чём можно ходить
can_walk_2 = {0, 3, 4, 8}          # в чём можно ходить

ChunkSX = ChunkSY = ChunkSZ = 8
ChunkSXm1, ChunkSYm1, ChunkSZm1 = ChunkSX - 1, ChunkSY - 1, ChunkSZ - 1

can_walk   = tuple(i in can_walk   for i in range(12)) # set to tuple
can_walk_2 = tuple(i in can_walk_2 for i in range(12)) # set to tuple



def can_stand(level):
  get_chunk = level.getchunk
  graph = {}
  min_y = float("inf")
  for (my_x, my_y, my_z), chunk in level.chunks.items():
    min_y = min(min_y, my_y)
    data = chunk.data
    top_chunk = get_chunk(my_x, my_y + 1, my_z).data
    my_x *= ChunkSX
    my_y *= ChunkSY
    my_z *= ChunkSZ
    for x, y, z in Chunk.pos_cube:
      if can_walk[data[y][z][x]]:
        y += 1
        top = data[y][z][x] if y < ChunkSY else top_chunk[0][z][x]
        if can_walk_2[top]:
          graph[(my_x + x, my_y + y, my_z + z)] = []
  return graph, min_y

def can_move(level, graph, min_y):
  get_chunk = level.getchunk
  for pos in graph:
    graph_add = graph[pos].append
    x, y, z = pos
    # print(x, y, z)
    Y = divmod(y, ChunkSY)
    for dx, dz in ((-1, 0), (0, 1), (1, 0), (0, -1)):
      chunk_x, _x = divmod(dx + x, ChunkSX)
      chunk_z, _z = divmod(dz + z, ChunkSZ)
      chunk_y, _y = Y
      data = get_chunk(chunk_x, chunk_y, chunk_z).data
      # print("   ", dx, dz)
      while chunk_y >= min_y:
        id = data[_y][_z][_x] 
        # print("       ", chunk_y * ChunkSY + _y, id)
        if can_walk[id]:
          # local to global coordinates
          _y += chunk_y * ChunkSY
          height = y - _y
          if not height: break
          _x += chunk_x * ChunkSX
          _z += chunk_z * ChunkSZ
          pos = _x, _y + 1, _z
          # print("   ", dx, dz, "->", pos, pos in graph)
          graph_add(pos)
          break
        elif not can_walk_2[id]: break

        if _y: _y -= 1
        else:
          chunk_y -= 1
          _y = ChunkSYm1
          data = get_chunk(chunk_x, chunk_y, chunk_z).data

def print_graph(level, graph):
  renderer = level.renderer
  m = renderer.arrowed_markers
  level.set_hook(m.recalc, m.clear)

  def yeah():
    add_arrow = m.add_arrow
    for pos, arr in graph.items():
      for pos2 in arr:
        add_arrow(pos, pos2)
  Thread(yeah).start()

def test_level(level):
  graph, min_y = can_stand(level)
  can_move(level, graph, min_y)
  # print(graph)
  print_graph(level, graph)
