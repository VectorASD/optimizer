import os
import zipfile

def create_zip(paths, zip_filename, compression_level=9):
  with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zip_file:
    for path, pathInZip in paths:
      zip_file.write(path, pathInZip)

os.chdir(os.path.dirname(__file__))

paths = (
  ("PMY.py", None),
  ("packToZip.py", None),
  ("modules/myGL.py", None),
  ("modules/myGLclasses.py", None),
  ("modules/rbxmReader.py", None),
  ("modules/rbxmMeshReader.py", None),
  ("modules/rbxmLoader.py", None),
  ("modules/myGL31.py", None),
  ("modules/myGLtext.py", None),
  ("modules/random.py", None),
  ("modules/common.py", None),
  ("modules/planetEngine.py", None),
  ("modules/myGLnoise.py", None),

  ("resources/textures.png", None),
  ("resources/avatar.rbxm", None),
  ("resources/skybox_labeled.png", None),
  ("resources/skybox_space.webp", None),
  ("resources/SolarSystem.rbxm", None),
  ("resources/emoji2.txt", None),
  ("resources/CourseWork.rbxm", None),
  ("resources/fire.png", None),

  ("EulerRotators.py", None),
  ("resources/emoji.txt", None),
  ("emoji.py", None),
)

zip_filename = "PMY_name.zip"
create_zip(paths, zip_filename, compression_level=9)
print(f"Архив {zip_filename} успешно создан! ;'-}}")
