#!/usr/bin/env python
# encoding: utf-8

import webbrowser
from Naked.toolshed.system import stderr, stdout

docs_dict = {
    "docs": "http://doxx.org",
    "blog": "http://things.doxx.org",
    "updates": "https://twitter.com/doxxapp",
    "source": "https://github.com/chrissimpkins/doxx",
    "pr": "https://github.com/doxx-repo",
    "browse": "http://doxx.org/commands/browse/",
    "build": "http://doxx.org/commands/build/",
    "clean": "http://doxx.org/commands/clean/",
    "make": "http://doxx.org/commands/make/",
    "pack": "http://doxx.org/commands/pack/",
    "pull": "http://doxx.org/commands/pull/",
    "pullkey": "http://doxx.org/commands/pullkey/",
    "search": "http://doxx.org/commands/search/",
    "unpack": "http://doxx.org/commands/unpack/",
    "whatis": "http://doxx.org/commands/whatis/",
    "syntax": "http://doxx.org/usage/syntax/",
    "template": "http://doxx.org/usage/templates/",
    "key": "http://doxx.org/usage/keys/",
    "archive": "http://doxx.org/usage/archives/",
    "changes": "http://doxx.org/more/changelog/"
}

docs_message_dict = {
    "docs": "doxx main documentation page",
    "blog": "doxx blog",
    "updates": "doxx Twitter updates feed",
    "source": "doxx Github repository",
    "pr": "doxx Package Repository",
    "browse": "browse command documentation",
    "build": "build command documentation",
    "clean": "clean command documentation",
    "make": "make command documentation",
    "pack": "pack command documentation",
    "pull": "pull command documentation",
    "pullkey": "pullkey command documentation",
    "search": "search command documentation",
    "unpack": "unpack command documentation",
    "whatis": "whatis command documentation",
    "syntax": "syntax documentation",
    "template": "template file documentation",
    "key": "key file documentation",
    "archive": "project archive documentation",
    "changes": "doxx changelog"    
}

def browse_docs(query):
    """browse doxx documentation and associated websites by query term in default web browser"""
    normalized_query = query.lower()
    available_queries = docs_dict.keys()
    if normalized_query in available_queries:
        webbrowser.open(docs_dict[normalized_query])
        if normalized_query in docs_message_dict.keys():
            stdout("[*] doxx: Opening the " + docs_message_dict[normalized_query])
    else:
        new_query = sounds_like(normalized_query)  # attempt to match using other common terms
        if new_query in available_queries:
            webbrowser.open(docs_dict[new_query])  # open the new query term that resulted from the sounds_like function
            if new_query in docs_message_dict.keys():
                stdout("[*] doxx: Opening the " + docs_message_dict[new_query])            
        else:
            stderr("[!] doxx: Unable to find a page for your query.  The available queries are:", exit=0)
            stderr(" ", exit=0)
            for available_query in sorted(available_queries):
                stderr(available_query, exit=0)
            
        
def sounds_like(query):
    """Match common query terms to the actual key mapping value in the URL dictionary"""
    docs_list = ['documentation', 'help', 'doxx.org']
    blog_list = ['things', 'tutorials', 'tuts']
    updates_list = ['twitter', 'feed', 'update', 'news', 'whatsnew']
    source_list = ['sourcecode', 'code', 'modules', 'repository']
    pr_list = ['packagerepo', 'package-repo', 'packages']
    template_list = ['templates']
    key_list = ['keys']
    archive_list = ['archives']
    changes_list = ['changelog']
    
    if query in docs_list:
        return 'docs'
    elif query in blog_list:
        return 'blog'
    elif query in updates_list:
        return 'updates'
    elif query in source_list:
        return 'source'
    elif query in pr_list:
        return 'pr'
    elif query in template_list:
        return 'template'
    elif query in key_list:
        return 'key'
    elif query in archive_list:
        return 'archive'
    elif query in changes_list:
        return 'changes'
    else:
        return query  # if it wasn't changed, just return the original query
    