# qiita-sync

![pytest](https://github.com/ryokat3/qiita-sync/actions/workflows/pytest.yml/badge.svg)
![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/ryokat3/qiita-sync/Python%20Test/main)
![Codecov branch](https://img.shields.io/codecov/c/github/ryokat3/qiita-sync/main)
![GitHub](https://img.shields.io/github/license/ryokat3/qiita-sync)

qiita-sync is a python command line tool that can synchronize your local markdown files with Qiita articles.


# Get Started

## Requirement

- Qiita Account
- GitHub repository
- Python (v3.7 or higher)
- qiita-sync

## Preparation

### Qiita Access Token

1. Generate your access token

   1. Open [Qiita Account Applications](https://qiita.com/settings/applications)
   2. Click "Generate new token"
   3. Copy the access token displayed.

2. Make your access token available as environment variable QIITA_ACCESS_TOKEN

   Your access token must be availble as environment varialbe **QIITA_ACCESS_TOKEN** whenever
   you execute qiita-sync. You need to make the access token secret, not to make it available in public.

3. (Optional) Check if your access token is valid
 
   Your qiita account information will be displayed with the command below.

   ```bash
   curl -sH "Authorization: Bearer $(echo ${QIITA_ACCESS_TOKEN})" https://qiita.com/api/v2/authenticated_user | python -m json.tool
   ```

### Install qiita-sync

1. Check the python version

   Check if the Python version is 3.7 or higher with the command below

   ```bash
   python --version
   ```

2. Install qiita-sync

   ```bash
   pip install qiita-sync
   ```

### Download your Qiita articles

Change the directory to your git repository, and execute the command below to download your Qiita articles.

```bash
qiita_sync sync .
```

### (Optional) Change filenames of your Qiita articles

The file name of downloaded Qiita articles are like `a5b5328c93bad615c5b2.md` whose naming convention is "<Qiita-Article-ID>.md".
However you can rename those files and can move to any subdirectories within the git repository directory.


# Editing

qiita-sync has some rules/features for Qiita article files to make them synchronized with Qiita site.

## Article Header

Each downloaded articles has a header. This header is automatically generated when downloaded from Qiita site.
And, it is automatically removed when uploaded to Qiita site.

You can cange `title` and `tags` as you like. However **you must not remove `id`**.
It's a key information for synchronization with Qiita site.

```markdown
<!--
title: Python development environment with pyenv + venv + poetry (Ubuntu 21.10)
tags:  python,ubuntu
id:    a5b5328c93bad615c5b2
-->
```

But, you don't need `id` in the header when you create new articles.

```markdown
<!--
title: No id is necessary in the header when you create new articles
tags:  qiita-sync
-->
```

## Links to your Qiita articles

You can write a link to another your Qiita article as a relative file path like below.

```markdown
<!-- An example of link to another Qiita article -->
[My Article](../my-article.md)
```

This link will be automatically changed to the URL when uploaded to Qiita site.
And, it will be automatically changed to the relative file path when downloaded from Qiita site.

```markdown
<!-- An example of link to another Qiita article -->
[My Article](https://qiita.com/ryokat3/items/a5b5328c93bad615c5b2)
```

## Link to image files

You can write a link to an image file as a relative file path like below.

```markdown
<!-- An example of link to image file 'earth.png' -->
![My Image](../image/earth.png)
```

This link will be automatically changed to the URL when uploaded to Qiita site.
And, it will be automatically changed to the relative file path when downloaded from Qiita site.

```markdown
<!-- An example of link to image file 'earth.png' -->
![My Image](https://raw.githubusercontent.com/ryokat3/qiita-articles/main/image/earth.png)
```

# Note

- Supported Python version is 3.7 or higher because "future feature annotations is not defined" as of 3.6
