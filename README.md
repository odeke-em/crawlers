Crawlers for various websites mostly news providers
====================================================

Basic idea, fetch content of a web-page and examine

the text present, extracting matching keywords/text

eg by file extension name or domain.

Once links are extracted, if files, they are

downloaded, or queued up on the cloud for workers to

actually perform the downloads.

+ To use the local based downloader:

    ++ Works on any version of Python >= 2.X

    python fileDownloader.py

+ To use the cloud based job queuer:

    ++ So far built for Python3.X

    python3 targetForCloud.py
