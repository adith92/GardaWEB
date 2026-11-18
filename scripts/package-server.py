"""Create a separate private server distribution; never mix core into viewer installers."""
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

version = "0.14.0"
platform, binary, license_file, destination = sys.argv[1:]
source=Path('projects/garda/ai-core')
dest=Path(destination);dest.mkdir(parents=True,exist_ok=True)
name=f'GARDA-Server-{platform}-{version}.zip'
with zipfile.ZipFile(dest/name,'w',zipfile.ZIP_DEFLATED) as z:
    for file in (source/'garda_ai').glob('*.py'):
        z.write(file,'garda_ai/'+file.name)
    for file in (source/'requirements-unified.txt',source/'requirements-providers.txt',source/'README_UNIFIED.md'):
        z.write(file,file.name)
    for file in Path('infra/unified').glob('*'):
        if file.suffix in ('.ps1','.service','.md','.sh'):
            z.write(file,file.name)
    for file in Path('dist').rglob('*'):
        if file.is_file():z.write(file,'web/'+file.relative_to('dist').as_posix())
    engine=Path(binary)
    z.write(engine,'bin/'+engine.name)
    z.write(license_file,'bin/MEDIAMTX-LICENSE.txt')
    z.writestr('bin/engine.json',json.dumps({'version':'1.21.4','source':'https://github.com/bluenviron/mediamtx',
        'source_commit':'e65f9411a56b19076a0dfde1fb4a59414bdf642c','binary':engine.name,
        'sha256':hashlib.sha256(engine.read_bytes()).hexdigest()},indent=2))
with zipfile.ZipFile(dest/name) as z:
    assert not z.testzip()
    assert all(not any(s in name.lower() for s in ('.key','.p12','.pfx','.keystore','cameras.encrypted','server-settings.json','templates/')) for name in z.namelist())
print(name,hashlib.sha256((dest/name).read_bytes()).hexdigest())
