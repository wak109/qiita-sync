import os
import random
import string
import pytest
from pathlib import Path
from typing import Generator, List

from qiita_sync.qiita_sync import QiitaArticle, qsync_argparse
from qiita_sync.qiita_sync import DEFAULT_ACCESS_TOKEN_FILE, DEFAULT_INCLUDE_BLOB, DEFAULT_EXCLUDE_BLOB
from qiita_sync.qiita_sync import git_get_default_branch, qsync_init
from qiita_sync.qiita_sync import markdown_code_block_split, markdown_code_inline_split, markdown_replace_text
from qiita_sync.qiita_sync import markdown_replace_link, markdown_replace_image

from pytest_mock.plugin import MockerFixture

markdown_1 = """
# section

LinkTest1: [dlink](markdown_2.md)
LinkTest2: [dlink](https://example.com/markdown/markdown_2.md)

`````shell
Short sequence of backticks
```
#LinkTest   [LinkTest](LintTest.md)
#ImageTest ![ImageTest](image/ImageTest.png)
`````

## sub-section

ImageTest1: ![ImageTest](img/ImageTest.png)
ImageTest2: ![ImageTest](img/ImageTest.png description)
ImageTest3: ![ImageTest](http://example.com/img/ImageTest.png img/ImageTest.png)

"""

markdown_2 = """
<!--
title: test
tags:  test
id:    123457689
-->

# test
"""

markdown_3 = """
# section

LinkTest1: [dlink](https://qiita.com/qiita_id/items/123457689)
LinkTest2: [dlink](https://example.com/markdown/markdown_2.md)

`````shell
Short sequence of backticks
```
#LinkTest   [LinkTest](LintTest.md)
#ImageTest ![ImageTest](image/ImageTest.png)
`````

## sub-section

ImageTest1: ![ImageTest](https://raw.githubusercontent.com/wak109/qiita-sync/main/img/ImageTest.png)
ImageTest2: ![ImageTest](HTTPS://raw.githubusercontent.com/wak109/qiita-sync/main/img/ImageTest.png description)
ImageTest3: ![ImageTest](http://example.com/img/ImageTest.png img/ImageTest.png)
"""


def markdown_find_line(text: str, keyword: str) -> List[str]:
    return [line[len(keyword):].strip() for line in text.splitlines() if line.startswith(keyword)]


def generate_random_name(length: int) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_tmpfile_fixture(content: str):
    filename = generate_random_name(16)

    @pytest.fixture
    def _(tmpdir) -> Generator[str, None, None]:
        tmpfile = tmpdir.join(filename)

        try:
            with tmpfile.open("w") as f:
                f.write(content)
            yield str(tmpfile)
        finally:
            tmpfile.remove()

    return _


def generate_file_fixture(content: str, filename: str):

    @pytest.fixture
    def _() -> Generator[str, None, None]:
        filepath = Path(filename)

        try:
            filepath.write_text(content)
            yield str(filename)
        finally:
            filepath.unlink()

    return _


markdown_1_fixture = generate_file_fixture(markdown_1, "markdown_1.md")
markdown_2_fixture = generate_file_fixture(markdown_2, "markdown_2.md")
markdown_3_fixture = generate_file_fixture(markdown_3, "markdown_3.md")
markdown_1_tmp_fixture = generate_tmpfile_fixture(markdown_1)


def test_qsync_argparse():
    args = qsync_argparse().parse_args("download .".split())

    assert args.target == "."
    assert args.include == DEFAULT_INCLUDE_BLOB
    assert args.exclude == DEFAULT_EXCLUDE_BLOB
    assert args.token == DEFAULT_ACCESS_TOKEN_FILE


def test_git_get_default_branch():
    assert git_get_default_branch() == "main"


def test_QiitaArticle_fromFile(markdown_1_tmp_fixture):
    doc = QiitaArticle.fromFile(Path(markdown_1_tmp_fixture))
    assert doc.data.title == markdown_find_line(markdown_1, '# ')[0]


def test_markdown_code_block_split():
    assert ''.join(markdown_code_block_split(markdown_1)) == markdown_1


@pytest.mark.parametrize(
    "text, num, idx, item",
    [
        (r"Hey `aaa` hoho", 3, 1, '`aaa`'),  # normal
        (r"Hey ``aa`a`bb`` hoho", 3, 0, 'Hey '),  # backtick
        (r"Hey ```aa`a``bb\```` hoho ````bb`日本語````", 4, 1, r"```aa`a``bb\```"),  # CJK character
        (r"```aa\`日本語\``bb``` hoho `bbbb` ccc", 4, 1, " hoho ")
    ])
def test_markdown_code_inline_split(text, num, idx, item):
    assert len(markdown_code_inline_split(text)) == num
    assert markdown_code_inline_split(text)[idx] == item


def test_markdown_replace_text():
    assert markdown_replace_text(lambda x: "x", markdown_1)[1] != "x"


@pytest.mark.parametrize("text, func, replaced", [(r"[](hello)", lambda x: x + x, r"[](hellohello)"),
                                                  (r"[日本語](hello world)", lambda x: x + x, r"[日本語](hellohello world)"),
                                                  (r"![日本語](hello world)", lambda x: x + x, r"![日本語](hello world)")])
def test_markdown_replace_link(text, func, replaced):
    assert markdown_replace_link(func, text) == replaced


@pytest.mark.parametrize("text, func, replaced",
                         [(r"![](hello)", lambda x: x + x, r"![](hellohello)"),
                          (r"aaa [日本語](hello world)", lambda x: x + x, r"aaa [日本語](hello world)"),
                          (r"aaa![日本語](hello world)", lambda x: x + x, r"aaa![日本語](hellohello world)")])
def test_markdown_replace_image(text, func, replaced):
    assert markdown_replace_image(func, text) == replaced


def test_QiitaSync_instance(mocker: MockerFixture):
    mocker.patch('qiita_sync.qiita_sync.qsync_get_access_token', return_value=os.environ['QIITA_ACCESS_TOKEN'])
    args = qsync_argparse().parse_args("download .".split())
    qsync = qsync_init(args)
    assert qsync.qiita_id == "wak109"


'''
def test_getQiitaFormat(markdown_1_fixture, markdown_2_fixture):
    markdown_1_path = Path(markdown_1_fixture) 
    QiitaArticle.fromFile(Path(markdown_2_fixture))

    converted = QsyncArticle(None, QiitaArticle.fromFile(
        markdown_1_path), markdown_1_path, GitRepository.getInstance(), "qiita_id").getQiitaFormat().article.body

    assert markdown_find_line(converted, 'LinkTest1:')[0] == '[dlink](https://qiita.com/qiita_id/items/123457689)'
    assert markdown_find_line(converted, 'LinkTest2:')[0] == '[dlink](https://example.com/markdown/markdown_2.md)'
    assert markdown_find_line(
        converted,
        'ImageTest1:')[0] == '![ImageTest](https://raw.githubusercontent.com/wak109/qiita-sync/main/img/ImageTest.png)'
    assert markdown_find_line(
        converted, 'ImageTest2:'
    )[0] == '![ImageTest](https://raw.githubusercontent.com/wak109/qiita-sync/main/img/ImageTest.png description)'
    assert markdown_find_line(
        converted, 'ImageTest3:')[0] == '![ImageTest](http://example.com/img/ImageTest.png img/ImageTest.png)'


def test_getLocalFormat(markdown_3_fixture, markdown_2_fixture):
    markdown_3_path = Path(markdown_3_fixture) 
    QiitaArticle.fromFile(Path(markdown_2_fixture))

    converted = QsyncArticle(None, QiitaArticle.fromFile(
        markdown_3_path), markdown_3_path, GitRepository.getInstance(), "qiita_id").getLocalFormat().article.body

    print(converted)
'''
