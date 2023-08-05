"""
Tests the compiler module
"""
import os
import re
import pytest
from open_cobol_ide import system
from open_cobol_ide.compilers import (
    GnuCobolCompiler, get_file_type)
from open_cobol_ide.enums import FileType, GnuCobolStandard
from open_cobol_ide.settings import Settings


def test_extensions():
    exts = GnuCobolCompiler().extensions
    if system.windows:
        assert exts[0] == '.exe'
        assert exts[1] == '.dll'
    else:
        assert exts[0] == ''
        assert exts[1] == '.so'


def test_is_working():
    assert GnuCobolCompiler().is_working()


def test_get_version():
    prog = re.compile(r'^\d.\d.\d$')
    assert prog.match(GnuCobolCompiler().get_version()) is not None


@pytest.mark.parametrize('path, ftype', [
    ('test/testfiles/TEST-PRINTER.cbl', FileType.EXECUTABLE),
    ('test/testfiles/VIRTUAL-PRINTER.cbl', FileType.MODULE),
])
def test_get_file_type(path, ftype):
    assert get_file_type(path) == ftype


@pytest.mark.parametrize('file_type, expected', [
    (FileType.EXECUTABLE, '.exe' if system.windows else ''),
    (FileType.MODULE, '.dll' if system.windows else '.so'),
])
def test_type_extension(file_type, expected):
    assert GnuCobolCompiler().extension_for_type(file_type) == expected


exe_ext = GnuCobolCompiler().extension_for_type(FileType.EXECUTABLE)
dll_ext = GnuCobolCompiler().extension_for_type(FileType.MODULE)


@pytest.mark.parametrize('free, std, ftype, expected_opts', [
    (False, GnuCobolStandard.default, FileType.EXECUTABLE, [
        '-x',
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + exe_ext),
        '-std=default'
    ]),
    (True, GnuCobolStandard.default, FileType.EXECUTABLE, [
        '-x',
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + exe_ext),
        '-std=default',
        '-free'
    ]),
    (False, GnuCobolStandard.default, FileType.MODULE, [
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + dll_ext),
        '-std=default'
    ]),
    (True, GnuCobolStandard.default, FileType.MODULE, [
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + dll_ext),
        '-std=default',
        '-free'
    ]),
    (False, GnuCobolStandard.mf, FileType.EXECUTABLE, [
        '-x',
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + exe_ext),
        '-std=mf'
    ]),
    (True, GnuCobolStandard.mf, FileType.EXECUTABLE, [
        '-x',
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + exe_ext),
        '-std=mf',
        '-free'
    ]),
    (False, GnuCobolStandard.mf, FileType.MODULE, [
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + dll_ext),
        '-std=mf'
    ]),
    (True, GnuCobolStandard.mf, FileType.MODULE, [
        '-o', '%s' % os.path.join('bin', 'HelloWorld' + dll_ext),
        '-std=mf',
        '-free'
    ])
])
def test_make_command_exe(free, std, ftype, expected_opts):
    compiler = GnuCobolCompiler()
    settings = Settings()
    settings.free_format = free
    settings.cobol_standard = std
    pgm, options = compiler.make_command(['HelloWorld.cbl'], ftype)
    assert pgm == 'cobc'
    for o, eo in zip(options, expected_opts):
        assert o == eo
    settings.free_format = free
    settings.cobol_standard = GnuCobolStandard.default
    settings.free_format = False


@pytest.mark.parametrize('path, ftype, expected_results, output_file_path', [
    ('test/testfiles/HelloWorld.cbl', FileType.EXECUTABLE, (0, []),
     'test/testfiles/bin/HelloWorld' + exe_ext),
    ('test/testfiles/MALFORMED.cbl', FileType.EXECUTABLE,
     (1,
      [('syntax error, unexpected CONFIGURATION, expecting "end of file"', 2,
        10, 0, None, None, 'MALFORMED.cbl')]), ''),
])
def test_compile(path, ftype, expected_results, output_file_path):
    results = GnuCobolCompiler().compile(path, ftype)
    assert results[0] == expected_results[0]
    assert len(results[1]) >= len(expected_results[1])
    if output_file_path:
        assert os.path.exists(output_file_path)
        os.remove(output_file_path)


@pytest.mark.parametrize('filename, expected_results', [
    ('test/testfiles/HelloWorld.cbl', []),
    ('test/testfiles/TEST-PRINTER.cbl',
     ['test/testfiles/VIRTUAL-PRINTER.cbl'] if system.linux else
     ['test/testfiles/VIRTUAL-PRINTER.cbl',
      'test/testfiles/VIRTUAL-PRINTER.CBL'])
])
def test_get_dependencies(filename, expected_results):
    results = GnuCobolCompiler().get_dependencies(filename)
    assert results == expected_results
