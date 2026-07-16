import json
import os

def main():
    manifest_path = '.release-please-manifest.json'
    output_path = 'version_info.txt'
    
    version = "0.1.1" # Fallback 

    if os.path.exists(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            version = json.load(f).get(".", version)
            
    parts = version.split('-')[0].split('.')
    v_tuple = f"{parts[0]}, {parts[1]}, {parts[2]}, 0"
    
    template = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v_tuple}),
    prodvers=({v_tuple}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'Tugamer89'),
        StringStruct('FileDescription', 'AC Virtual Engineer Server'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'ac_virtual_engineer'),
        StringStruct('LegalCopyright', 'Copyright (c) 2026'),
        StringStruct('OriginalFilename', 'ac_virtual_engineer.exe'),
        StringStruct('ProductName', 'AC Virtual Engineer'),
        StringStruct('ProductVersion', '{version}')])
      ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
        
    print(f"File {output_path} successfully generated for the version {version}")

if __name__ == '__main__':
    main()
