# coding: utf-8

import urllib.request
import urllib.parse
from lxml import html
from bs4 import BeautifulSoup
import textwrap
from mini_templates import Tmp


class MiniReadability:
    def __init__(self, url):
        self._url = url

    def get_article_bs(self):
        article_text = ''
        with urllib.request.urlopen(self._url) as f:
            host_name = self._get_host_name(self._url)
            tmp = Tmp()
            template = tmp.get_templates_from_host_name(host_name)
            meta_tags = template['meta_tags']
            text_tags = template['text_tags']
            delete_tags = template['delete_tags']
            html_raw = f.read().decode('utf-8')
            root_bs = BeautifulSoup(html_raw, "html.parser")
            # print(html_raw)
            print('site:', host_name, end=' ')
            if len(meta_tags) == 0:
                print('template not find')
            else:
                print('template find')
            text_nodes = self._get_nodes_with_text_bs(root_bs, meta_tags, text_tags, delete_tags)
            # print(text_nodes)
            article_text = self._get_text_from_nodes(text_nodes, [])
        # print(article_text)
        return article_text


    @staticmethod
    def _get_host_name(url):
        parse_url = urllib.parse.urlparse(url)
        return parse_url.hostname

    def _get_nodes_with_text_bs(self, root_bs, meta_tags, text_tags, delete_tags)-> list:
        if len(delete_tags) > 0:
            delete_nodes = root_bs.find_all(delete_tags)
            for delete in delete_nodes:
                delete.extract()
        text_nodes = []
        if len(meta_tags) == 0:
            # сайт был без шаблона, надо найти <div> с самым длинным текстом
            text_nodes = root_bs.find_all(text_tags)
            fat_text_node = self._get_parent_node_with_longest_text(text_nodes)
            text_nodes = fat_text_node.find_all(text_tags)
            pass
        else:
            # сайт с шаблоном, ищем по шаблону
            meta_nodes = []
            for mt in meta_tags:
                for key, value in mt.items():
                    nodes_list = root_bs.find_all(key, value)
                    meta_nodes += nodes_list
            for node in meta_nodes:
                list_n = node.find_all(text_tags)
                text_nodes += list_n
        return text_nodes

    @staticmethod
    def _get_parent_node_with_longest_text(text_nodes):
        parents = {}
        for node in text_nodes:
            parent = node.parent
            if parent in parents.keys():
                parents[parent] += len(node.text)
            else:
                parents.update({parent: len(node.text)})
        max_len = max(parents.values())
        max_node = [key for key, value in parents.items() if value == max_len]
        return max_node[0]

    @staticmethod
    def _get_text_from_nodes(text_nodes, tags_replace_template)-> str:
        text = ''
        for node in text_nodes:
            refs = node.find_all('a')
            for ref in refs:
                ref_str = ref.text + ' [' + ref.get('href') + ']'
                ref.replaceWith(ref_str)
            node_text = node.text
            node_text = ''.join(node_text)
            node_text = node_text.replace('\n', '')
            node_text = node_text.replace('\t', '')
            text += '\n'.join(textwrap.wrap(node_text)) + '\n\n'
        return text

    def _get_nodes_with_text(self, html_raw, meta_tags, text_tags) ->dict:
        nodes_with_text = {}
        tree = html.fromstring(html_raw)
        div_nodes = tree.xpath('//div')

        for node in div_nodes:
            text_tags_count = 0
            for text_t in text_tags:
                text_children = node.xpath('./' + text_t)
                text_tags_count += len(text_children)
            # print(node.attrib)
            # print('children tags with text for node = %d' % text_tags_count)
            # print()
            if text_tags_count > 0:
                nodes_with_text.update({node: text_tags_count})
        return nodes_with_text
