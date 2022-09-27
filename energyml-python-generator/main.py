import argparse
import os
import re
import shutil
import sys

PATTERN = r"(from|import)\s+(?P<oldPkg>((?:(?!common|resqml|witsml|prodml))\w+\.)+)\.?(?P<pkg>common|resqml|witsml|prodml)v2\W"

def _rename_pkgs(v_common: str, v_resqml: str, v_witsml: str, v_prodml: str, src_folder: str, new_pkg_prefix: str="energyml"):
    new_pkg_path_prefix = new_pkg_prefix.replace('.', '/')
    new_pkg_import_prefix = new_pkg_prefix.replace('/', '.').replace("-", "_")
    if "." in new_pkg_import_prefix:
        new_pkg_import_prefix = new_pkg_import_prefix[new_pkg_import_prefix.index(".") + 1:]

    pattern_opc = r'org(?P<separator>[\./\\])openxmlformats[\./\\]schemas[\./\\]package[\./\\]pkg_2006[\./\\](metadata[\./\\])?(?P<package>relationships|content_types|core_properties)'
    
    pattern_opc_with_src = re.sub(r'[\./\\]', r'[\./\\]', src_folder) + rf"[\./\\]{pattern_opc}"

    opc_pkg = new_pkg_import_prefix

    print("PATTERN => ", pattern_opc_with_src)

    if v_resqml:
        v_resqml = v_resqml.replace(".", "_")
    if v_common:
        v_common = v_common.replace(".", "_")
    if v_witsml:
        v_witsml = v_witsml.replace(".", "_")
    if v_prodml:
        v_prodml = v_prodml.replace(".", "_")

    dict_version = {
        'common' : v_common,
        'resqml' : v_resqml,
        'witsml' : v_witsml,
        'prodml' : v_prodml,
    }

    print(v_common, " -- ", v_resqml, " -- ", v_witsml, " -- ", v_prodml, " -- ")


    folder_to_rename = {}
    for root, dirs, files in os.walk(src_folder):
        path = root.split(os.sep)
        root_path = root.replace("\\", "/")
        # print((len(path) - 1) * '---', os.path.basename(root))
        for directory in dirs:
            full_path = root.replace("\\", "/") + "/" + directory
            print(len(path) * '---', directory,  "-->", full_path)
            m_opc = re.match(pattern_opc_with_src, full_path)
            m = re.search(r"(?P<pkg>common|resqml|witsml|prodml)(v2)?", directory)
            if m is not None and m.group("pkg") is not None:
                folder_to_rename[f'{root_path}/{directory}'] = f'{new_pkg_path_prefix}/{m.group("pkg")}{dict_version[m.group("pkg")]}'
            if m_opc is not None :
                folder_to_rename[f'{root_path}/{directory}'] = f'{new_pkg_path_prefix}/{m_opc.group("package")}'
            else:
                print(full_path, "not match ", pattern_opc_with_src)

            # elif directory == "content_types" or directory == "core_properties" or directory == "relationships")
            if(root == src_folder and directory == "xml"):
                folder_to_rename[f'{root_path}/{directory}'] = f'{new_pkg_path_prefix}/xml'

        for file in files:
            file_content = None
            with open(root + "/" + file, "r") as f:
                file_content = f.read()

            if file_content is not None:

                m_all = list(re.finditer(PATTERN, file_content))
                # print(root + "/" + file, " _ ", type(file_content), " -- ", len(m_all))
                # print(file_content[:300])
                if len(m_all) > 0:
                    m = m_all[0]
                    if m is not None:
                        # print("old pkg", m.group('oldPkg'))
                        for pkg in dict_version:
                            file_content = re.sub(rf"{m.group('oldPkg')}{pkg}(v2)?", f"{new_pkg_prefix}.{pkg}{dict_version[pkg]}", file_content)

                file_content = re.sub(pattern_opc_with_src, new_pkg_import_prefix, file_content)
                file_content = re.sub(rf'({src_folder}.)?gen.xml.lang_value', rf'{new_pkg_import_prefix}.xml.lang_value', file_content)

                with open(root + "/" + file, "w") as f:
                    f.write(file_content)

    # print(folder_to_rename)

    for old_dir in folder_to_rename:
        shutil.move(old_dir, folder_to_rename[old_dir])

    for root, dirs, files in os.walk(src_folder):
        if re.match(rf'{src_folder}[\\/]?$', root):
            for directory in dirs:
                if re.match(rf'^(?:(?!common|resqml|witsml|prodml|{new_pkg_path_prefix}).+)', directory):
                    print("removing", directory)
                    shutil.rmtree(root + "/" + directory)

    folders = re.split(r"[/\\]", new_pkg_path_prefix)
    for i in range(len(folders)):
        with open(f"{'/'.join(folders[:i+1])}/__init__.py", 'w') as f_init:
            f_init.write("")

def rename_pkgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resqml", "-r",
        type=str,
        help='Resqml version',
    )
    parser.add_argument(
        "--common", "-c",
        type=str,
        help='common version',
    )
    parser.add_argument(
        "--witsml", "-w",
        type=str,
        help='witsml version',
    )
    parser.add_argument(
        "--prodml", "-p",
        type=str,
        help='prodml version',
    )
    parser.add_argument(
        "--src", "-s",
        type=str,
        help='source folder',
    )
    parser.add_argument(
        "--newFolder", "-o",
        type=str,
        help='source folder',
    )
    args = parser.parse_args()

    _rename_pkgs(args.common, args.resqml, args.witsml, args.prodml, args.src, args.newFolder)



if __name__ == "__main__":
    file_path = "sample/data/TriangulatedSetRepresentation_349ecd25-5db0-40c1-b179-b5316fbc754f.xml"
    
    from energyml.resqml2_2 import *

    from pathlib import Path
    from xsdata.formats.dataclass.parsers import XmlParser
    from xsdata.formats.dataclass.serializers.config import SerializerConfig
    from xsdata.formats.dataclass.serializers import XmlSerializer

    xml_string = Path(file_path).read_text()
    parser = XmlParser()
    # from energyml.resqml2_2 import TriangulatedSetRepresentation
    # order = parser.from_string(xml_string, TriangulatedSetRepresentation)
    # print(order)
    with open(file_path, 'rb') as f:
        obj = parser.from_bytes(f.read())

        print(list(obj.__dict__))
        serializer = XmlSerializer(config=SerializerConfig(
            pretty_print=True,
            xml_declaration=True,
            ignore_default_attributes=True,
            schema_location="urn books.xsd",
            no_namespace_schema_location=None,
        ))
        print(serializer.render(obj))
        print(obj.validate())
