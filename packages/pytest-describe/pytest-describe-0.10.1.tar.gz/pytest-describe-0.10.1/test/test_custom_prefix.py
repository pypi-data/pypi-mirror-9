import py

pytest_plugins = 'pytester'

ini = """
[pytest]
describe_prefixes = foo bar
"""


def test_collect_custom_prefix(testdir):
    testdir.makeini(ini)

    a_dir = testdir.mkpydir('a_dir')
    a_dir.join('test_a.py').write(py.code.Source("""
        def foo_scope():
            def bar_context():
                def passes():
                    pass
    """))

    result = testdir.runpytest('--collectonly')
    print(result.outlines)
    assert result.stdout.lines[-7:-2] == [
        "collected 1 items",
        "<Module 'a_dir/test_a.py'>",
        "  <DescribeBlock 'foo_scope'>",
        "    <DescribeBlock 'bar_context'>",
        "      <Function 'passes'>",
    ]
